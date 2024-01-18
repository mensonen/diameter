# Working with diameter applications

A diameter application is the highest level of abstraction provided by the 
`diameter` package. It automates tasks such as:

 * Synchronous return of answers after sending messages
 * Tracking requests that require answers
 * Routing requests to any suitable peers, including load balancing
 * Constructing answers from received request messages

An "application" is any instance of a subclass of 
[`Application`][diameter.node.application.Application]. An application is 
handed over to a configured node and the node will route every received request
and answer message to the application, when necessary. Protocol-level message
exchanges, i.e. CER (Capabilities-Exchange), DWR (Device-Watchdog) and DPR
(Disconnect-Peer) never reach any application, but every other message is 
expected to be handled by at least one application.

If a node receives a message that no application has been configured to handle,
it will reject the message with a `DIAMETER_APPLICATION_UNSUPPORTED` error.

An example of the most basic client application:

```python
from diameter.message import Message
from diameter.message.constants import *
from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication

my_app = SimpleThreadingApplication(APP_DIAMETER_BASE_ACCOUNTING, 
                                    is_acct_application=True)

node = Node("peername.gy", "realm.net")
peer = node.add_peer("aaa://ocs2.gy;transport=sctp", "realm.net", 
                     ip_addresses=["10.16.0.8", "10.16.5.8"], 
                     is_persistent=True)
node.add_application(my_app, [peer])
node.start()

msg = Message()

my_app.wait_for_ready()
answer = my_app.send_request(msg, timeout=10)
```

The [`add_application`][diameter.node.Node.add_application] call configures 
also the peers that the application will use. More than one application of 
same type can be added at the same time, as long as they use different peers.

The application provides a 
[`wait_for_ready`][diameter.node.application.Application.wait_for_ready] method, 
which will block until at least one of the configured peers becomes available 
to receive requests.

The [`send_request`][diameter.node.application.Application.send_request] 
application instance method will block until an answer message has been 
received, and then returns the message, synchronously.

The `diameter` package offers three different application implementations:

[`Application`][diameter.node.application.Application]
:   The most basic form of an application. Must be subclassed and contains two 
    methods, `handle_request`, which must be overridden, and `handle_answer`,
    which *may* be overriden, but is usually not necessary. 

    The `Application` class calls internally `handle_request` for each 
    received diameter request in the main thread. It calls `handle_answer` for
    each answer that comes unexpected, i.e. without a request waiting for it.

    ```python
    from diameter.message import Message
    from diameter.message.constants import *
    from diameter.node import Node
    from diameter.node.application import Application

    class MyApplication(Application):
        def handle_request(self, message: Message):
            print("Got request", message)
    
    my_app = MyApplication(APP_DIAMETER_BASE_ACCOUNTING, 
                           is_acct_application=True)
    
    node = Node("peername.gy", "realm.net")
    peer = node.add_peer("aaa://ocs2.gy;transport=sctp", "realm.net")
    node.add_application(my_app, [peer])
    ```

    !!! Warning
        The request and answer are called in the main `Node` work thread and 
        they will block the node from processing any other messages. When this
        class is used, the implementing party is expected to build a queue and/or
        threading based solution on top, which would not block the main thread.


[`ThreadingApplication`][diameter.node.application.ThreadingApplication]
:   A variation of application, which spawns a new thread for each incoming 
    request, up to an optional maximum amount of threads. Must be subclassed.
    Also contains two methods, `handle_request`, which must be overridden, 
    and `handle_answer`, which *may* be overriden, but is usually not necessary.

    Unlike in the base `Application` class, the threading application expects
    that the overridden `handle_request` returns a valid diameter message as an
    answer to the received request. Failing to do so results in an automatic 
    generation of a `DIAMETER_UNABLE_TO_COMPLY` error message.
    
    ```python
    from diameter.message import Message
    from diameter.message.constants import *
    from diameter.node import Node
    from diameter.node.application import ThreadingApplication

    class MyApplication(ThreadingApplication):
        def handle_request(self, message: Message) -> Message:
            print("Got request", message)
            answer = self.generate_answer(message)
            return answer
    
    my_app = MyApplication(APP_DIAMETER_BASE_ACCOUNTING, 
                           is_acct_application=True,
                           max_threads=50)
    
    node = Node("peername.gy", "realm.net")
    peer = node.add_peer("aaa://ocs2.gy;transport=sctp", "realm.net")
    node.add_application(my_app, [peer])
    ```

[`SimpleThreadingApplication`][diameter.node.application.SimpleThreadingApplication]
:   A variation of threading application, which does not need to be subclassed 
    and handles incoming requests only optionally. Also spawns a new thread for 
    each incoming request, up to an optional maximum amount of threads. 

    In order to receive requests, the `SimpleThreadingApplication` accepts a 
    callback method in its constructor and calls it in a separate spawned 
    thread. Similar to the threading application, the callback function *must*
    return a valid answer, otherwise a `DIAMETER_UNABLE_TO_COMPLY` error is 
    sent back to the network.

    If no callback is provided, the `SimpleThreadingApplication` acts as a 
    client only and accepts no incoming requests.
    
    ```python
    from diameter.message import Message
    from diameter.message.constants import *
    from diameter.node import Node
    from diameter.node.application import SimpleThreadingApplication
    
    def recv_request(app: SimpleThreadingApplication, message: Message) -> Message:
        print("Got request", message, "through application", app)
        answer = app.generate_answer(message)
        answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
        return answer
    
    my_app = SimpleThreadingApplication(APP_DIAMETER_BASE_ACCOUNTING, 
                                        is_acct_application=True,
                                        max_threads=50,
                                        request_handler=recv_request)
    
    node = Node("peername.gy", "realm.net")
    peer = node.add_peer("aaa://ocs2.gy;transport=sctp", "realm.net")
    node.add_application(my_app, [peer])
    ```
