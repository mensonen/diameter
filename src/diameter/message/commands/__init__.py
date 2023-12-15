"""
Placeholder classes that extend `Message`, but do not provide any direct
python API for reading and setting AVPs.
"""
from typing import Type

from .._base import Message, DefinedMessage

# Message types that have "proper" implementations; Requests and Answers are
# their own distinct classes and permit AVP values to be accessed as instance
# attributes
from .abort_session import *
from .accounting import *
from .capabilities_exchange import *
from .credit_control import *
from .device_watchdog import *
from .disconnect_peer import *
from .re_auth import *
from .session_termination import *


# Remaining Message types that have no implementation (yet), either because
# they are vendor specific extensions documented outside the RFCs, or because
# they are less common in day-to-day usage. They can be used but there is no
# attribute-based AVP access.


class AaMobileNode(Message):
    """An AA-Mobile-Node message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [AaMobileNode.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 260
    name: str = "AA-Mobile-Node"

    def __post_init__(self):
        self.header.command_code = self.code


class HomeAgentMip(Message):
    """A Home-Agent-MIP message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [AaMobileNode.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 262
    name: str = "Home-Agent-MIP"

    def __post_init__(self):
        self.header.command_code = self.code


class Aa(Message):
    """An AA message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [Aa.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 265
    name: str = "AA"

    def __post_init__(self):
        self.header.command_code = self.code


class DiameterEap(Message):
    """A Diameter-EAP message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [DiameterEap.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 268
    name: str = "Diameter-EAP"

    def __post_init__(self):
        self.header.command_code = self.code


class SipUserAuthorization(Message):
    """A SIP-User-Authorization message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SipUserAuthorization.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 283
    name: str = "SIP-User-Authorization"

    def __post_init__(self):
        self.header.command_code = self.code


class SipServerAssignment(Message):
    """A SIP-Server-Assignment message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SipServerAssignment.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 284
    name: str = "SIP-Server-Assignment"

    def __post_init__(self):
        self.header.command_code = self.code


class SipLocationInfo(Message):
    """A SIP-Location-Info message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SipLocationInfo.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 285
    name: str = "SIP-Location-Info"

    def __post_init__(self):
        self.header.command_code = self.code


class SipMultimediaAuth(Message):
    """A SIP-Multimedia-Auth message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SipMultimediaAuth.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 286
    name: str = "SIP-Multimedia-Auth"

    def __post_init__(self):
        self.header.command_code = self.code


class SipRegistrationTermination(Message):
    """A SIP-Registration-Termination message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SipRegistrationTermination.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 287
    name: str = "SIP-Registration-Termination"

    def __post_init__(self):
        self.header.command_code = self.code


class SipPushProfile(Message):
    """A SIP-Push-Profile message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SipPushProfile.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 288
    name: str = "SIP-Push-Profile"

    def __post_init__(self):
        self.header.command_code = self.code


class UserAuthorization(Message):
    """A User-Authorization message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [UserAuthorization.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 300
    name: str = "User-Authorization"

    def __post_init__(self):
        self.header.command_code = self.code


class ServerAssignment(Message):
    """A Server-Assignment message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ServerAssignment.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 301
    name: str = "Server-Assignment"

    def __post_init__(self):
        self.header.command_code = self.code


class LocationInfo(Message):
    """A Location-Info message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [LocationInfo.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 302
    name: str = "Location-Info"

    def __post_init__(self):
        self.header.command_code = self.code


class MultimediaAuth(Message):
    """A Multimedia-Auth message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [MultimediaAuth.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 303
    name: str = "Multimedia-Auth"

    def __post_init__(self):
        self.header.command_code = self.code


class RegistrationTermination(Message):
    """A Registration-Termination message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [AaMobileNode.append_avpRegistrationTerminationdiameter.message.Message.append_avp] method.
    """
    code: int = 304
    name: str = "Registration-Termination"

    def __post_init__(self):
        self.header.command_code = self.code


class PushProfile(Message):
    """A Push-Profile message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [PushProfile.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 305
    name: str = "Push-Profile"

    def __post_init__(self):
        self.header.command_code = self.code


class UserData(Message):
    """A User-Data message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [UserData.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 306
    name: str = "User-Data"

    def __post_init__(self):
        self.header.command_code = self.code


class ProfileUpdate(Message):
    """A Profile-Update message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProfileUpdate.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 307
    name: str = "Profile-Update"

    def __post_init__(self):
        self.header.command_code = self.code


class SubscribeNotifications(Message):
    """A Subscribe-Notifications message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SubscribeNotifications.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 308
    name: str = "Subscribe-Notifications"

    def __post_init__(self):
        self.header.command_code = self.code


class PushNotification(Message):
    """A Push-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [PushNotification.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 309
    name: str = "Push-Notification"

    def __post_init__(self):
        self.header.command_code = self.code


class BootstrapingInfo(Message):
    """A Bootstraping-Info message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [BootstrapingInfo.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 310
    name: str = "Bootstraping-Info"

    def __post_init__(self):
        self.header.command_code = self.code


class MessageProcess(Message):
    """A Message-Process message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [MessageProcess.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 311
    name: str = "Message-Process"

    def __post_init__(self):
        self.header.command_code = self.code


class UpdateLocation(Message):
    """A 3GPP-Update-Location message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [UpdateLocation.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 316
    name: str = "3GPP-Update-Location"

    def __post_init__(self):
        self.header.command_code = self.code


class CancelLocation(Message):
    """A 3GPP-Cancel-Location message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [CancelLocation.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 317
    name: str = "3GPP-Cancel-Location"

    def __post_init__(self):
        self.header.command_code = self.code


class AuthenticationInformation(Message):
    """A 3GPP-Authentication-Information message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [AuthenticationInformation.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 318
    name: str = "3GPP-Authentication-Information"

    def __post_init__(self):
        self.header.command_code = self.code


class InsertSubscriberData(Message):
    """A 3GPP-Insert-Subscriber-Data message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [InsertSubscriberData.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 319
    name: str = "3GPP-Insert-Subscriber-Data"

    def __post_init__(self):
        self.header.command_code = self.code


class DeleteSubscriberData(Message):
    """A 3GPP-Delete-Subscriber-Data message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [DeleteSubscriberData.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 320
    name: str = "3GPP-Delete-Subscriber-Data"

    def __post_init__(self):
        self.header.command_code = self.code


class PurgeUE(Message):
    """A 3GPP-Purge-UE message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [PurgeUE.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 321
    name: str = "3GPP-Purge-UE"

    def __post_init__(self):
        self.header.command_code = self.code


class Reset(Message):
    """A 3GPP-Reset message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [Reset.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 322
    name: str = "3GPP-Reset"

    def __post_init__(self):
        self.header.command_code = self.code


class Notify(Message):
    """A 3GPP-Notify message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [Notify.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 323
    name: str = "3GPP-Notify"

    def __post_init__(self):
        self.header.command_code = self.code


class MeIdentityCheck(Message):
    """A 3GPP-ME-Identity-Check message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [AaMobileNode.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 324
    name: str = "3GPP-ME-Identity-Check"

    def __post_init__(self):
        self.header.command_code = self.code


class MIp6(Message):
    """A MIP6 message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [MIp6.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 325
    name: str = "MIP6"

    def __post_init__(self):
        self.header.command_code = self.code


all_commands: dict[int, Type[Message]] = {
    m.code: m for m in Message.__subclasses__()}
all_commands.update({
    m.code: m for m in DefinedMessage.__subclasses__()
})
