"""
Diameter application implementations.

Instances of Applications, or their subclasses, provided by this module can be
passed directly to an instance of a `Node`, for receiving and sending diameter
application messages.

In most cases, the most suitable option to use is
[`SimpleThreadingApplication`][diameter.node.application.SimpleThreadingApplication],
which will cover the most scenarios without requiring any unnecessary setup.
"""
from __future__ import annotations

import queue
import logging
import threading

from typing import TypeVar, Callable

from ..message import Message
from ..message import constants
from ._helpers import StoppableThread


_AnyMessageType = TypeVar("_AnyMessageType", bound=Message)
_AnyAnswerType = TypeVar("_AnyAnswerType", bound=Message)
logger = logging.getLogger("diameter.application")


class Application:
    """A basic diameter application that can be registered with a Node.

    Can be used as a starting point for building applications with custom
    logic. In most cases, `SimpleThreadingApplication` and
    `ThreadingApplication` are more practical.
    """
    def __init__(self, application_id: int = None,
                 is_acct_application: bool = False,
                 is_auth_application: bool = False):
        """Create a new diameter application.

        Args:
            application_id: Authentication application ID
            is_acct_application: Flag the application as an accounting app
            is_auth_application: Flag the application as an authorisation app

        """
        if is_acct_application is False and is_auth_application is False:
            raise ValueError(
                "Either is_acct_application or is_acct_application must be True")

        self.application_id: int = application_id
        self.is_auth_application: bool = is_auth_application
        self.is_acct_application: bool = is_acct_application
        self.name = constants.APPLICATIONS.get(
            self.application_id, "Unknown Application")

        self.is_ready: threading.Event = threading.Event()
        self._node: Node | None = None
        self._answer_waiting: dict[int, WaitingMessage] = {}

    def __str__(self):
        return f"<{self.name} ({self.application_id})>"

    @property
    def node(self) -> Node:
        if self._node is None:
            raise RuntimeError(
                "Application has not been registered with a diameter Node; "
                "has `Node.add_application` been run?")
        return self._node

    def generate_answer(self, message: _AnyMessageType,
                        result_code: int = None,
                        error_message: str = None) -> _AnyAnswerType:
        """Produce an answer message from a request message.

        Calls [Message.to_answer][diameter.message.Message.to_answer] and adds
        origin host, origin realm, session id and application IDs automatically.

        Args:
            message: Any diameter message with a python implementation,
                accepting AVPs as instance attributes
            result_code: An optional result code to add to the answer
            error_message: An optional error message to add to the answer

        """
        answer_msg = message.to_answer()
        answer_msg.origin_host = self.node.origin_host.encode()
        answer_msg.origin_realm = self.node.realm_name.encode()

        if hasattr(message, "session_id"):
            answer_msg.session_id = message.session_id
        if hasattr(message, "proxy_info"):
            answer_msg.proxy_info = message.proxy_info

        if self.is_auth_application:
            answer_msg.auth_application_id = self.application_id
        if self.is_acct_application:
            answer_msg.acct_application_id = self.application_id
        if result_code:
            answer_msg.result_code = result_code
        if result_code:
            answer_msg.error_message = error_message

        return answer_msg

    def receive_answer(self, message: Message):
        if message.header.hop_by_hop_identifier in self._answer_waiting:
            waiting = self._answer_waiting[message.header.hop_by_hop_identifier]
            waiting.answer = message
            waiting.event.set()
        else:
            logger.debug(
                f"{self} received an answer message "
                f"{hex(message.header.hop_by_hop_identifier)} with nobody "
                f"expecting it")
            self.handle_answer(message)

    def receive_request(self, message: Message):
        self.handle_request(message)

    def handle_request(self, message: Message):
        """Called every time a request message is received.

        The parent diameter node does not check or expect this method to return
        anyhing; the application is expected to send its answer messages back
        towards the network by using the `send_message` method.

        !!! Warning

            This method is called in the main thread; its execution blocks the
            diameter Node from processing any incoming or outgoing messages.
            The implementing party is expected to utilise a message queue and
            do the work in a separate thread. Alternatively, the
            [ThreadingApplication][diameter.node.application.ThreadingApplication]
            can be used, which spawns a new thread for every request.

        """
        raise NotImplementedError("handle_request must be overridden")

    def handle_answer(self, message: Message):
        """Called every time an unexpected answer message is received.

        Normally, answers are returned directly as the return values of
        `send_request`; overriding this method is not strictly required. It is
        called every time an answer is received, with nobody expecting one.
        This could happen e.g. when the answer wait timeout has been exceeded.
        By default, this method does nothing and only discards every unexpected
        message.

        !!! Warning

            This method is called in the main thread; its execution blocks the
            diameter Node from processing any incoming or outgoing messages.
            The implementing party is expected to utilise a message queue and
            do the work in a separate thread.

        """
        pass

    def send_answer(self, message: Message):
        """Send an answer message.

        Routes the message directly to the parent diameter node, where it will
        be forwarded through the network to the appropriate peer. The
        application ID, hop-by-hop identifier and end-to-end identifiers must
        already be set (copied from the original request).

        Args:
            message: A diameter message to send

        The method will return nothing; it returns immediately without waiting
        for any results from the network.
        """
        peer, _ = self.node.route_answer(message)

        self.node.send_message(peer, message)

    def send_request(self, message: Message, timeout: int = 30) -> Message:
        """Send a request message.

        Routes the message directly to the parent diameter node, where it will
        be forwarded through the network to the appropriate peer. The header
        application ID and end-to-end hop identifiers are set automatically,
        if not already present.

        The hop-by-hop identifier will be set by the node, if the message can
        be routed to a peer and if the identifier is not already present.

        Args:
            message: A diameter message to send
            timeout: A timeout in seconds to wait for an answer

        Returns:
            A diameter answer message, if one was received within the timeout
                seconds, otherwise `None`. If the sent message was not a
                request, returns `None` immediately without waiting.

        """
        if not message.header.end_to_end_identifier:
            message.header.end_to_end_identifier = self.node.end_to_end_seq.next_sequence()
        if not message.header.application_id:
            message.header.application_id = self.application_id
        peer, _ = self.node.route_request(self, message)

        waiting = WaitingMessage()
        self._answer_waiting[message.header.hop_by_hop_identifier] = waiting
        self.node.send_message(peer, message)

        try:
            if waiting.event.wait(timeout) is not True:
                raise TimeoutError("Timed out waiting for answer")

            if waiting.answer is None:
                raise EmptyAnswer("Response is None")

            return waiting.answer
        except Exception:
            raise
        finally:
            del self._answer_waiting[message.header.hop_by_hop_identifier]

    def start(self):
        logger.info(f"{self} application started")

    def stop(self):
        for waiting in self._answer_waiting.values():
            waiting.event.set()
        logger.info(f"{self} application stopped")

    def wait_for_ready(self, timeout: int = 30):
        """Wait for application connectivity to become ready.

        Waits until at least one of the peers specified for the application has
        completed its CER/CEA procedure and become ready to accept requests. If
        all the configured peers for the application become again disconnected,
        `wait_for_ready` will block again, until at least one of the peers has
        returned and completed their CER/CEA.

        !!! Note
            This method can be called every time before `send_request` is to be
            used, for increased certainty that a request will go through,
            however it will not guarantee that a peer will not go offline
            between calling this method and sending the request.

        Args:
            timeout: Amount of time to wait, in seconds

        Raises:
            ApplicationError: If no peer becomes available before timeout

        """
        if self.is_ready.wait(timeout) is not True:
            raise ApplicationError("No connection available within timeout")
        logger.info(f"{self} at least one peer has become available")


class ThreadingApplication(Application):
    """A diameter application that starts a thread for each request.

    An alternative to the base application, where each message received by the
    diameter node is handled in a separate thread. The implementing party
    should override the `handle_request` method and do the message processing
    work within, returning a new answer.
    """
    def __init__(self, application_id: int = None,
                 is_acct_application: bool = False,
                 is_auth_application: bool = False,
                 max_threads: int = 0):
        """Create a new threading diameter application.

        Args:
            application_id: Authentication application ID
            is_acct_application: Flag the application as an accounting app
            is_auth_application: Flag the application as an authorisation app
            max_threads: Maximum threads to start simultaneously for processing
                messages. When maximum thread count is reached, the application
                does not handle any further messages, until at least one of the
                already started threads has exited. If set to 0, the amount of
                threads to spawn is unlimited.

        """
        super().__init__(application_id, is_acct_application,
                         is_auth_application)

        # Queue where node produced messages arrive
        self._recv_msg_queue = queue.Queue()
        # Queue where user-implemented `handle_message` results drop
        self._resp_msg_queue = queue.Queue()
        # A queue that blocks if `max_threads` is reached. This could be a
        # BoundedSemaphore as well, however we might want to put something
        # meaningful in the slot queue in the future; e.g. some information on
        # the threads that have been spawned. Right now it's just filled with
        # `Nones`.
        self._thread_slots = queue.Queue(maxsize=max_threads)

        self._recv_queue_consumer = StoppableThread(
            target=self._wait_for_recv_msg)
        self._resp_queue_consumer = StoppableThread(
            target=self._wait_for_resp_msg)

    def _wait_for_recv_msg(self, _thread):
        while True:
            if _thread.is_stopped:
                break
            try:
                recv_message = self._recv_msg_queue.get(True, timeout=3)
            except queue.Empty:
                continue
            try:
                self._thread_slots.put(None, timeout=5)
            except queue.Full:
                answer = self.generate_answer(
                    recv_message,
                    result_code=constants.E_RESULT_CODE_DIAMETER_TOO_BUSY,
                    error_message="Insufficient resources to handle the request")
                self.send_answer(answer)
                continue

            process_message = threading.Thread(
                target=self._process_recv_msg, args=(recv_message,))
            try:
                process_message.start()
            except RuntimeError as e:
                logger.warning(
                    f"{self} failed to spawn a thread for calling "
                    f"`handle_request`: {e}, discarded message "
                    f"{hex(recv_message.header.hop_by_hop_identifier)}")

    def _wait_for_resp_msg(self, _thread):
        while True:
            if _thread.is_stopped:
                break
            try:
                resp_message = self._resp_msg_queue.get(True, timeout=3)
            except queue.Empty:
                continue
            try:
                self._thread_slots.get(block=False)
            except Exception:
                pass
            if isinstance(resp_message, Message):
                self.send_answer(resp_message)

    def _process_recv_msg(self, message: Message):
        try:
            answer = self.handle_request(message)
        except Exception as e:
            logger.warning(f"{self} message handling failed: {repr(e)}")
            answer = self.generate_answer(
                message,
                result_code=constants.E_RESULT_CODE_DIAMETER_UNABLE_TO_COMPLY)
        if answer is not None:
            self._resp_msg_queue.put(answer)

    def handle_request(self, message: Message) -> Message | None:
        """Called by diameter node every time a request message is received.

        Unlike the base `Application` version of this same method, the
        `handle_request` is expected to return an answer, either `None` or a
        valid diameter Message. The return value of the method is sent
        automatically back towards the network. Any exceptions raised by the
        method are caught and result in a DIAMETER_UNABLE_TO_COMPLY result
        being returned to the network.
        """
        raise NotImplementedError("handle_request must be overridden")

    def receive_request(self, message: Message):
        self._recv_msg_queue.put(message)

    def start(self):
        self._resp_queue_consumer.start()
        self._recv_queue_consumer.start()

    def stop(self):
        self._resp_queue_consumer.stop()
        self._recv_queue_consumer.stop()
        self._resp_queue_consumer.join(2)
        self._recv_queue_consumer.join(2)
        super().stop()


class SimpleThreadingApplication(ThreadingApplication):
    """A diameter application that starts a thread for each request.

    An alternative to the base threading application, that does not require
    subclassing or overwriting. The implementing party should pass a callback
    function in the `request_handler` argument. The application will call
    the passed function for every received request in a separate thread,
    passing an instance of the app itself and the message to handle as
    arguments.

    If the application acts as a client only and never expects any requests,
    the callback function is optional.

    ```
    from diameter.node.application import SimpleThreadingApplication
    from diameter.message import constants

    def handle_request(app: Application, message: Message):
        print("Got", message)
        answer = app.generate_answer(message)
        return answer

    app = SimpleThreadingApplication(
        constants.APP_DIAMETER_BASE_ACCOUNTING,
        is_acct_application=True,
        request_handler=handle_request)
    ```

    """
    def __init__(self, application_id: int = None,
                 is_acct_application: bool = False,
                 is_auth_application: bool = False,
                 max_threads: int = 0,
                 request_handler: Callable = None):
        """Create a new threading diameter application.

        Args:
            application_id: Authentication application ID
            is_acct_application: Flag the application as an accounting app
            is_auth_application: Flag the application as an authorisation app
            max_threads: Maximum threads to start simultaneously for processing
                messages. When maximum thread count is reached, the application
                does not handle any further messages, until at least one of the
                already started threads has exited. If set to 0, the amount of
                threads to spawn is unlimited.
            request_handler: Any callable that will be called whenever a
                request is received. It will receive an instance of the app and
                request message as its arguments and is expected to return an
                answer message

        """
        super().__init__(application_id,
                         is_acct_application=is_acct_application,
                         is_auth_application=is_auth_application,
                         max_threads=max_threads)
        self._request_handler = request_handler

    def handle_request(self, message: Message) -> Message | None:
        if self._request_handler:
            return self._request_handler(self, message)
        return None


class ApplicationError(Exception):
    """Base error class for all Application-raised errors."""
    pass


class EmptyAnswer(ApplicationError):
    """An error received when a diameter peer fails to respond."""
    pass


class RequestTimeout(ApplicationError):
    """An error received when no answer is received within a given timeout."""
    pass


class WaitingMessage:
    def __init__(self):
        self.event: threading.Event = threading.Event()
        self.answer: Message | None = None


from .node import Node
