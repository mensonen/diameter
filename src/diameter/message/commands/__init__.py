from typing import Type

from .._base import Message

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
    code: int = 260
    name: str = "AA-Mobile-Node"

    def __post_init__(self):
        self.header.command_code = self.code


class HomeAgentMip(Message):
    code: int = 262
    name: str = "Home-Agent-MIP"

    def __post_init__(self):
        self.header.command_code = self.code


class Aa(Message):
    code: int = 265
    name: str = "AA"

    def __post_init__(self):
        self.header.command_code = self.code


class DiameterEap(Message):
    code: int = 268
    name: str = "Diameter-EAP"

    def __post_init__(self):
        self.header.command_code = self.code


class SipUserAuthorization(Message):
    code: int = 283
    name: str = "SIP-User-Authorization"

    def __post_init__(self):
        self.header.command_code = self.code


class SipServerAssignment(Message):
    code: int = 284
    name: str = "SIP-Server-Assignment"

    def __post_init__(self):
        self.header.command_code = self.code


class SipLocationInfo(Message):
    code: int = 285
    name: str = "SIP-Location-Info"

    def __post_init__(self):
        self.header.command_code = self.code


class SipMultimediaAuth(Message):
    code: int = 286
    name: str = "SIP-Multimedia-Auth"

    def __post_init__(self):
        self.header.command_code = self.code


class SipRegistrationTermination(Message):
    code: int = 287
    name: str = "SIP-Registration-Termination"

    def __post_init__(self):
        self.header.command_code = self.code


class SipPushProfile(Message):
    code: int = 288
    name: str = "SIP-Push-Profile"

    def __post_init__(self):
        self.header.command_code = self.code


class UserAuthorization(Message):
    code: int = 300
    name: str = "User-Authorization"

    def __post_init__(self):
        self.header.command_code = self.code


class ServerAssignment(Message):
    code: int = 301
    name: str = "Server-Assignment"

    def __post_init__(self):
        self.header.command_code = self.code


class LocationInfo(Message):
    code: int = 302
    name: str = "Location-Info"

    def __post_init__(self):
        self.header.command_code = self.code


class MultimediaAuth(Message):
    code: int = 303
    name: str = "Multimedia-Auth"

    def __post_init__(self):
        self.header.command_code = self.code


class RegistrationTermination(Message):
    code: int = 304
    name: str = "Registration-Termination"

    def __post_init__(self):
        self.header.command_code = self.code


class PushProfile(Message):
    code: int = 305
    name: str = "Push-Profile"

    def __post_init__(self):
        self.header.command_code = self.code


class UserData(Message):
    code: int = 306
    name: str = "User-Data"

    def __post_init__(self):
        self.header.command_code = self.code


class ProfileUpdate(Message):
    code: int = 307
    name: str = "Profile-Update"

    def __post_init__(self):
        self.header.command_code = self.code


class SubscribeNotifications(Message):
    code: int = 308
    name: str = "Subscribe-Notifications"

    def __post_init__(self):
        self.header.command_code = self.code


class PushNotification(Message):
    code: int = 309
    name: str = "Push-Notification"

    def __post_init__(self):
        self.header.command_code = self.code


class BootstrapingInfo(Message):
    code: int = 310
    name: str = "Bootstraping-Info"

    def __post_init__(self):
        self.header.command_code = self.code


class MessageProcess(Message):
    code: int = 311
    name: str = "Message-Process"

    def __post_init__(self):
        self.header.command_code = self.code


class UpdateLocation(Message):
    code: int = 316
    name: str = "3GPP-Update-Location"

    def __post_init__(self):
        self.header.command_code = self.code


class CancelLocation(Message):
    code: int = 317
    name: str = "3GPP-Cancel-Location"

    def __post_init__(self):
        self.header.command_code = self.code


class AuthenticationInformation(Message):
    code: int = 318
    name: str = "3GPP-Authentication-Information"

    def __post_init__(self):
        self.header.command_code = self.code


class InsertSubscriberData(Message):
    code: int = 319
    name: str = "3GPP-Insert-Subscriber-Data"

    def __post_init__(self):
        self.header.command_code = self.code


class DeleteSubscriberData(Message):
    code: int = 320
    name: str = "3GPP-Delete-Subscriber-Data"

    def __post_init__(self):
        self.header.command_code = self.code


class PurgeUE(Message):
    code: int = 321
    name: str = "3GPP-Purge-UE"

    def __post_init__(self):
        self.header.command_code = self.code


class Reset(Message):
    code: int = 322
    name: str = "3GPP-Reset"

    def __post_init__(self):
        self.header.command_code = self.code


class Notify(Message):
    code: int = 323
    name: str = "3GPP-Notify"

    def __post_init__(self):
        self.header.command_code = self.code


class MeIdentityCheck(Message):
    code: int = 324
    name: str = "3GPP-ME-Identity-Check"

    def __post_init__(self):
        self.header.command_code = self.code


class MIp6(Message):
    code: int = 325
    name: str = "MIP6"

    def __post_init__(self):
        self.header.command_code = self.code


all_commands: dict[int, Type[Message]] = {
    m.code: m for m in Message.__subclasses__()}