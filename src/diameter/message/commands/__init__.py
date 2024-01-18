"""
Placeholder classes that extend `Message`, but do not provide any direct
python API for reading and setting AVPs.
"""
from typing import Type

from .._base import Message, DefinedMessage, UndefinedMessage

# Message types that have "proper" implementations; Requests and Answers are
# their own distinct classes and permit AVP values to be accessed as instance
# attributes
from .aa import *
from .aa_mobile_node import *
from .abort_session import *
from .accounting import *
from .capabilities_exchange import *
from .credit_control import *
from .device_watchdog import *
from .diameter_eap import *
from .disconnect_peer import *
from .home_agent_mip import *
from .re_auth import *
from .spending_limit import *
from .spending_status_notification import *
from .session_termination import *


# Remaining Message types that have no implementation (yet), either because
# they are vendor specific extensions documented outside the RFCs, or because
# they are less common in day-to-day usage. They can be used but there is no
# attribute-based AVP access.


class SipUserAuthorization(UndefinedMessage):
    """A SIP-User-Authorization message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SipUserAuthorization.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 283
    name: str = "SIP-User-Authorization"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class SipServerAssignment(UndefinedMessage):
    """A SIP-Server-Assignment message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SipServerAssignment.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 284
    name: str = "SIP-Server-Assignment"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class SipLocationInfo(UndefinedMessage):
    """A SIP-Location-Info message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SipLocationInfo.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 285
    name: str = "SIP-Location-Info"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class SipMultimediaAuth(UndefinedMessage):
    """A SIP-Multimedia-Auth message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SipMultimediaAuth.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 286
    name: str = "SIP-Multimedia-Auth"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class SipRegistrationTermination(UndefinedMessage):
    """A SIP-Registration-Termination message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SipRegistrationTermination.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 287
    name: str = "SIP-Registration-Termination"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class SipPushProfile(UndefinedMessage):
    """A SIP-Push-Profile message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SipPushProfile.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 288
    name: str = "SIP-Push-Profile"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class UserAuthorization(UndefinedMessage):
    """A User-Authorization message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [UserAuthorization.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 300
    name: str = "User-Authorization"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ServerAssignment(UndefinedMessage):
    """A Server-Assignment message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ServerAssignment.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 301
    name: str = "Server-Assignment"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class LocationInfo(UndefinedMessage):
    """A Location-Info message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [LocationInfo.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 302
    name: str = "Location-Info"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class MultimediaAuth(UndefinedMessage):
    """A Multimedia-Auth message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [MultimediaAuth.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 303
    name: str = "Multimedia-Auth"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RegistrationTermination(UndefinedMessage):
    """A Registration-Termination message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [AaMobileNode.append_avpRegistrationTerminationdiameter.message.Message.append_avp] method.
    """
    code: int = 304
    name: str = "Registration-Termination"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class PushProfile(UndefinedMessage):
    """A Push-Profile message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [PushProfile.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 305
    name: str = "Push-Profile"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class UserData(UndefinedMessage):
    """A User-Data message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [UserData.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 306
    name: str = "User-Data"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProfileUpdate(UndefinedMessage):
    """A Profile-Update message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProfileUpdate.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 307
    name: str = "Profile-Update"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class SubscribeNotifications(UndefinedMessage):
    """A Subscribe-Notifications message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SubscribeNotifications.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 308
    name: str = "Subscribe-Notifications"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class PushNotification(UndefinedMessage):
    """A Push-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [PushNotification.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 309
    name: str = "Push-Notification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class BootstrapingInfo(UndefinedMessage):
    """A Bootstraping-Info message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [BootstrapingInfo.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 310
    name: str = "Bootstraping-Info"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class MessageProcess(UndefinedMessage):
    """A Message-Process message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [MessageProcess.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 311
    name: str = "Message-Process"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class UpdateLocation(UndefinedMessage):
    """A 3GPP-Update-Location message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [UpdateLocation.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 316
    name: str = "3GPP-Update-Location"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class CancelLocation(UndefinedMessage):
    """A 3GPP-Cancel-Location message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [CancelLocation.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 317
    name: str = "3GPP-Cancel-Location"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class AuthenticationInformation(UndefinedMessage):
    """A 3GPP-Authentication-Information message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [AuthenticationInformation.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 318
    name: str = "3GPP-Authentication-Information"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class InsertSubscriberData(UndefinedMessage):
    """A 3GPP-Insert-Subscriber-Data message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [InsertSubscriberData.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 319
    name: str = "3GPP-Insert-Subscriber-Data"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class DeleteSubscriberData(UndefinedMessage):
    """A 3GPP-Delete-Subscriber-Data message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [DeleteSubscriberData.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 320
    name: str = "3GPP-Delete-Subscriber-Data"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class PurgeUE(UndefinedMessage):
    """A 3GPP-Purge-UE message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [PurgeUE.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 321
    name: str = "3GPP-Purge-UE"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class TgppReset(UndefinedMessage):
    """A 3GPP-Reset message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [Reset.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 322
    name: str = "3GPP-Reset"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class Notify(UndefinedMessage):
    """A 3GPP-Notify message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [Notify.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 323
    name: str = "3GPP-Notify"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class MeIdentityCheck(UndefinedMessage):
    """A 3GPP-ME-Identity-Check message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [AaMobileNode.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 324
    name: str = "3GPP-ME-Identity-Check"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class MIp6(UndefinedMessage):
    """A MIP6 message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [MIp6.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 325
    name: str = "MIP6"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class QoSAuthorization(UndefinedMessage):
    """A QoS-Authorization message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [QoSAuthorization.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 326
    name: str = "QoS-Authorization"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class QoSInstall(UndefinedMessage):
    """A QoS-Install message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [QoSInstall.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 327
    name: str = "QoS-Install"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class CapabilitiesUpdate(UndefinedMessage):
    """A Capabilities-Update message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [CapabilitiesUpdate.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 328
    name: str = "Capabilities-Update"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class IKEv2SK(UndefinedMessage):
    """An IKEv2-SK message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [IKEv2SK.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 329
    name: str = "IKEv2-SK"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NATControl(UndefinedMessage):
    """A NAT-Control message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NATControl.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 330
    name: str = "NAT-Control"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class WIMAXHRPDSFF(UndefinedMessage):
    """A WIMAX-HRPD-SFF message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [WIMAXHRPDSFF.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388608
    name: str = "WIMAX-HRPD-SFF"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class WiMAXDiameterEAP(UndefinedMessage):
    """A WiMAX-Diameter-EAP message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [WiMAXDiameterEAP.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388609
    name: str = "WiMAX-Diameter-EAP"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class WiMAXChangeofAuthorization(UndefinedMessage):
    """A WiMAX-Change-of-Authorization message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [WiMAXChangeofAuthorization.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388610
    name: str = "WiMAX-Change-of-Authorization"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class WiMAXReauthentication(UndefinedMessage):
    """A WiMAX-Reauthentication message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [WiMAXReauthentication.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388611
    name: str = "WiMAX-Reauthentication"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class WiMAXSessionTermination(UndefinedMessage):
    """A WiMAX-Session-Termination message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [WiMAXSessionTermination.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388612
    name: str = "WiMAX-Session-Termination"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class WiMAXAbortSession(UndefinedMessage):
    """A WiMAX-Abort-Session message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [WiMAXAbortSession.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388613
    name: str = "WiMAX-Abort-Session"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class WiMAXHomeAgentIPv4(UndefinedMessage):
    """A WiMAX-Home-Agent-IPv4 message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [WiMAXHomeAgentIPv4.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388614
    name: str = "WiMAX-Home-Agent-IPv4"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class WiMAXHomeAgentIPv6(UndefinedMessage):
    """A WiMAX-Home-Agent-IPv6 message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [WiMAXHomeAgentIPv6.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388615
    name: str = "WiMAX-Home-Agent-IPv6"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class WiMAXDHCP(UndefinedMessage):
    """A WiMAX-DHCP message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [WiMAXDHCP.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388616
    name: str = "WiMAX-DHCP"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class WiMAXLAA(UndefinedMessage):
    """A WiMAX-LAA message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [WiMAXLAA.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388617
    name: str = "WiMAX-LAA"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class WiMAXLocationAccounting(UndefinedMessage):
    """A WiMAX-Location-Accounting message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [WiMAXLocationAccounting.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388618
    name: str = "WiMAX-Location-Accounting"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class WiMAXLocationMeasurementQuery(UndefinedMessage):
    """A WiMAX-Location-Measurement-Query message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [WiMAXLocationMeasurementQuery.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388619
    name: str = "WiMAX-Location-Measurement-Query"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProvideLocation(UndefinedMessage):
    """A 3GPP-Provide-Location message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProvideLocation.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388620
    name: str = "3GPP-Provide-Location"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class LocationReport(UndefinedMessage):
    """A 3GPP-Location-Report message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [LocationReport.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388621
    name: str = "3GPP-Location-Report"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class LCSRoutingInfo(UndefinedMessage):
    """A 3GPP-LCS-Routing-Info message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [LCSRoutingInfo.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388622
    name: str = "3GPP-LCS-Routing-Info"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class Notif(UndefinedMessage):
    """A Notif message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [Notif.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388623
    name: str = "Notif"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class MsgInterface(UndefinedMessage):
    """A Msg-Interface message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [MsgInterface.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388624
    name: str = "Msg-Interface"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class MobileApplication(UndefinedMessage):
    """A Mobile-Application message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [MobileApplication.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388625
    name: str = "Mobile-Application"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class JuniperSyncEvent(UndefinedMessage):
    """A Juniper-Sync-Event message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [JuniperSyncEvent.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388628
    name: str = "Juniper-Sync-Event"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class JuniperSessionDiscovery(UndefinedMessage):
    """A Juniper-Session-Discovery message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [JuniperSessionDiscovery.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388629
    name: str = "Juniper-Session-Discovery"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class QueryProfile(UndefinedMessage):
    """A Query Profile message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [QueryProfile.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388630
    name: str = "Query Profile"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class SubscriptionInformationApplication(UndefinedMessage):
    """A Subscription Information Application message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SubscriptionInformationApplication.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388631
    name: str = "Subscription-Information-Application"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class DistributedCharging(UndefinedMessage):
    """A Distributed Charging message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [DistributedCharging.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388632
    name: str = "Distributed-Charging"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class EricssonSL(UndefinedMessage):
    """An Ericsson-SL message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [EricssonSL.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388633
    name: str = "Ericsson-SL"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class EricssonSN(UndefinedMessage):
    """An Ericsson-SN message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [EricssonSN.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388634
    name: str = "Ericsson-SN"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class TDFSession(UndefinedMessage):
    """A TDF-Session message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [TDFSession.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388637
    name: str = "TDF-Session"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class UpdateVCSGLocation(UndefinedMessage):
    """A 3GPP-Update-VCSG-Location message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [UpdateVCSGLocation.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388638
    name: str = "3GPP-Update-VCSG-Location"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class DeviceAction(UndefinedMessage):
    """A 3GPP-Device-Action message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [DeviceAction.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388639
    name: str = "3GPP-Device-Action"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class DeviceNotification(UndefinedMessage):
    """A 3GPP-Device-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [DeviceNotification.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388640
    name: str = "3GPP-Device-Notification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class SubscriberInformation(UndefinedMessage):
    """A 3GPP-Subscriber-Information message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SubscriberInformation.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388641
    name: str = "3GPP-Subscriber-Information"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class CancelVCSGLocation(UndefinedMessage):
    """A Cancel-VCSG-Location message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [CancelVCSGLocation.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388642
    name: str = "Cancel-VCSG-Location"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class DeviceTrigger(UndefinedMessage):
    """A 3GPP-Device-Trigger message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [DeviceTrigger.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388643
    name: str = "3GPP-Device-Trigger"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class DeliveryReport(UndefinedMessage):
    """A 3GPP-Delivery-Report message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [DeliveryReport.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388644
    name: str = "3GPP-Delivery-Report"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class MOForwardShortMessage(UndefinedMessage):
    """An MO-Forward-Short-Message message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [MOForwardShortMessage.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388645
    name: str = "MO-Forward-Short-Message"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class MTForwardShortMessage(UndefinedMessage):
    """An MT-Forward-Short-Message message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [MTForwardShortMessage.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388646
    name: str = "MT-Forward-Short-Message"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class SendRoutingInfoforSM(UndefinedMessage):
    """A Send-Routing-Info-for-SM message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [SendRoutingInfoforSM.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388647
    name: str = "Send-Routing-Info-for-SM"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class AlertServiceCentre(UndefinedMessage):
    """An Alert-Service-Centre message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [AlertServiceCentre.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388648
    name: str = "Alert-Service-Centre"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ReportSMDeliveryStatus(UndefinedMessage):
    """A Report-SM-Delivery-Status message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ReportSMDeliveryStatus.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388649
    name: str = "Report-SM-Delivery-Status"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NSNCancelLocationMS(UndefinedMessage):
    """An NSN-Cancel-LocationMS message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NSNCancelLocationMS.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388650
    name: str = "NSN-Cancel-LocationMS"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NSNUserDataMS(UndefinedMessage):
    """An NSN-User-DataMS message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NSNUserDataMS.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388651
    name: str = "NSN-User-DataMS"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NSNProfileUpdateMS(UndefinedMessage):
    """An NSN-Profile-UpdateMS message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NSNProfileUpdateMS.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388652
    name: str = "NSN-Profile-UpdateMS"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NSNSubscribeNotificationsMS(UndefinedMessage):
    """An NSN-Subscribe-NotificationsMS message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NSNSubscribeNotificationsMS.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388653
    name: str = "NSN-Subscribe-NotificationsMS"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NSNPushNotificationMS(UndefinedMessage):
    """An NSN-Push-NotificationMS message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NSNPushNotificationMS.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388654
    name: str = "NSN-Push-NotificationMS"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class GetGateway(UndefinedMessage):
    """A Get-Gateway message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [GetGateway.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388655
    name: str = "Get-Gateway"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class TriggerEstablishment(UndefinedMessage):
    """A Trigger-Establishment message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [TriggerEstablishment.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388656
    name: str = "Trigger-Establishment"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class EricssonBindingData(UndefinedMessage):
    """An Ericsson-Binding-Data message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [EricssonBindingData.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388657
    name: str = "Ericsson-Binding-Data"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class Tggp2SubscriberInformation(UndefinedMessage):
    """A 3GPP2 Subscriber-Information message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [3GPP2SubscriberInformation.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388658
    name: str = "3GPP2 Subscriber-Information"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class VerizonSessionDataRecovery(UndefinedMessage):
    """A Verizon Session Data Recovery message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [VerizonSessionDataRecovery.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388659
    name: str = "Verizon Session Data Recovery"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NokiaCoreService(UndefinedMessage):
    """A Nokia Core Service message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NokiaCoreService.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388660
    name: str = "Nokia Core Service"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NokiaExtendedCommand(UndefinedMessage):
    """A Nokia Extended Command message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NokiaExtendedCommand.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388661
    name: str = "Nokia Extended Command"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class GCSAction(UndefinedMessage):
    """A GCS-Action message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [GCSAction.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388662
    name: str = "GCS-Action"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class GCSNotification(UndefinedMessage):
    """A GCS-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [GCSNotification.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388663
    name: str = "GCS-Notification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProSeSubscriberInformation(UndefinedMessage):
    """A ProSe-Subscriber-Information message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProSeSubscriberInformation.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388664
    name: str = "ProSe-Subscriber-Information"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class UpdateProSeSubscriberData(UndefinedMessage):
    """An Update-ProSe-Subscriber-Data message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [UpdateProSeSubscriberData.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388665
    name: str = "Update-ProSe-Subscriber-Data"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProSeNotify(UndefinedMessage):
    """A ProSe-Notify message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProSeNotify.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388666
    name: str = "ProSe-Notify"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class Reset(UndefinedMessage):
    """A Reset message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [MTData.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388667
    name: str = "Reset"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProSeAuthorization(UndefinedMessage):
    """A ProSe-Authorization message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProSeAuthorization.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388668
    name: str = "ProSe-Authorization"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProSeDiscovery(UndefinedMessage):
    """A ProSe-Discovery message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProSeDiscovery.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388669
    name: str = "ProSe-Discovery"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProSeMatch(UndefinedMessage):
    """A ProSe-Match message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProSeMatch.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388670
    name: str = "ProSe-Match"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProSeMatchReportInfo(UndefinedMessage):
    """A ProSe-Match-Report-Info message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProSeMatchReportInfo.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388671
    name: str = "ProSe-Match-Report-Info"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProSeProximity(UndefinedMessage):
    """A ProSe-Proximity message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProSeProximity.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388672
    name: str = "ProSe-Proximity"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProSeLocationUpdate(UndefinedMessage):
    """A ProSe-Location-Update message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProSeLocationUpdate.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388673
    name: str = "ProSe-Location-Update"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProSeAlert(UndefinedMessage):
    """A ProSe-Alert message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProSeAlert.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388674
    name: str = "ProSe-Alert"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProSeCancellation(UndefinedMessage):
    """A ProSe-Cancellation message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProSeCancellation.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388675
    name: str = "ProSe-Cancellation"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProXimityAction(UndefinedMessage):
    """A ProXimity-Action message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProXimityAction.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388676
    name: str = "ProXimity-Action"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdDSCRegistration(UndefinedMessage):
    """A Rivada Xd DSC-Registration message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdDSCRegistration.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388677
    name: str = "Rivada Xd DSC-Registration"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdHeartBeat(UndefinedMessage):
    """A Rivada Xd Heart-Beat message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdHeartBeat.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388678
    name: str = "Rivada Xd Heart-Beat"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdCellInfoTransfer(UndefinedMessage):
    """A Rivada Xd Cell-Info-Transfer message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdCellInfoTransfer.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388679
    name: str = "Rivada Xd Cell-Info-Transfer"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdCellInfoNotification(UndefinedMessage):
    """A Rivada Xd Cell-Info-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdCellInfoNotification.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388680
    name: str = "Rivada Xd Cell-Info-Notification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdCellInfoModification(UndefinedMessage):
    """A Rivada Xd Cell-Info-Modification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdCellInfoModification.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388681
    name: str = "Rivada Xd Cell-Info-Modification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdCellInfoModificationNotification(UndefinedMessage):
    """A Rivada Xd Cell-Info-Modification-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdCellInfoModificationNotification.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388682
    name: str = "Rivada Xd Cell-Info-Modification-Notification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdResourceAllocation(UndefinedMessage):
    """A Rivada Xd Resource-Allocation message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdResourceAllocation.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388683
    name: str = "Rivada Xd Resource-Allocation"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdResourceAllocationNotification(UndefinedMessage):
    """A Rivada Xd Resource-Allocation-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdResourceAllocationNotification.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388684
    name: str = "Rivada Xd Resource-Allocation-Notification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdResourceModification(UndefinedMessage):
    """A Rivada Xd Resource-Modification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdResourceModification.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388685
    name: str = "Rivada Xd Resource-Modification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdResourceModificationNotification(UndefinedMessage):
    """A Rivada Xd Resource-Modification-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdResourceModificationNotification.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388686
    name: str = "Rivada Xd Resource-Modification-Notification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdResourceHold(UndefinedMessage):
    """A Rivada Xd Resource-Hold message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdResourceHold.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388687
    name: str = "Rivada Xd Resource-Hold"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdResourceHoldNotification(UndefinedMessage):
    """A Rivada Xd Resource-Hold-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdResourceHoldNotification.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388688
    name: str = "Rivada Xd Resource-Hold-Notification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdResourceResume(UndefinedMessage):
    """A Rivada Xd Resource-Resume message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdResourceResume.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388689
    name: str = "Rivada Xd Resource-Resume"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdResourceResumeNotification(UndefinedMessage):
    """A Rivada Xd Resource-Resume-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdResourceResumeNotification.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388690
    name: str = "Rivada Xd Resource-Resume-Notification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdResourceUsageUpdate(UndefinedMessage):
    """A Rivada Xd Resource-Usage-Update message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdResourceUsageUpdate.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388691
    name: str = "Rivada Xd Resource-Usage-Update"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdResourceUsageNotification(UndefinedMessage):
    """A Rivada Xd Resource-Usage-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdResourceUsageNotification.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388692
    name: str = "Rivada Xd Resource-Usage-Notification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdResourceRelease(UndefinedMessage):
    """A Rivada Xd Resource-Release message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdResourceRelease.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388693
    name: str = "Rivada Xd Resource-Release"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXdResourceReleaseNotification(UndefinedMessage):
    """A Rivada Xd Resource-Release-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXdResourceReleaseNotification.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388694
    name: str = "Rivada Xd Resource-Release-Notification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXmResourceAllocation(UndefinedMessage):
    """A Rivada Xm Resource-Allocation message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXmResourceAllocation.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388695
    name: str = "Rivada Xm Resource-Allocation"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXmResourceHold(UndefinedMessage):
    """A Rivada Xm Resource-Hold message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXmResourceHold.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388696
    name: str = "Rivada Xm Resource-Hold"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXmResourceRelease(UndefinedMessage):
    """A Rivada Xm Resource-Release message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXmResourceRelease.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388697
    name: str = "Rivada Xm Resource-Release"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXmResourceModify(UndefinedMessage):
    """A Rivada Xm Resource-Modify message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXmResourceModify.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388698
    name: str = "Rivada Xm Resource-Modify"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXmResourceAllocationNotify(UndefinedMessage):
    """A Rivada Xm Resource-Allocation-Notify message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXmResourceAllocationNotify.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388699
    name: str = "Rivada Xm Resource-Allocation-Notify"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXmResourceResume(UndefinedMessage):
    """A Rivada Xm Resource-Resume message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXmResourceResume.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388700
    name: str = "Rivada Xm Resource-Resume"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXmAddUEContext(UndefinedMessage):
    """A Rivada Xm Add-UE-Context message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXmAddUEContext.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388701
    name: str = "Rivada Xm Add-UE-Context"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXmUpdateUEContext(UndefinedMessage):
    """A Rivada Xm Update-UE-Context message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXmUpdateUEContext.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388702
    name: str = "Rivada Xm Update-UE-Context"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXmDeleteUEContext(UndefinedMessage):
    """A Rivada Xm Delete-UE-Context message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXmDeleteUEContext.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388703
    name: str = "Rivada Xm Delete-UE-Context"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXmDetachUE(UndefinedMessage):
    """A Rivada Xm Detach-UE message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXmDetachUE.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388704
    name: str = "Rivada Xm Detach-UE"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXmPageUE(UndefinedMessage):
    """A Rivada Xm Page-UE message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXmPageUE.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388705
    name: str = "Rivada Xm Page-UE"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXmHeartBeat(UndefinedMessage):
    """A Rivada Xm Heart-Beat message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXmHeartBeat.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388706
    name: str = "Rivada Xm Heart-Beat"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXaDPCRegistration(UndefinedMessage):
    """A Rivada Xa DPC-Registration message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXaDPCRegistration.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388707
    name: str = "Rivada Xa DPC-Registration"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXaHeartBeat(UndefinedMessage):
    """A Rivada Xa Heart-Beat message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXaHeartBeat.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388708
    name: str = "Rivada Xa Heart-Beat"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXaResourceAllocation(UndefinedMessage):
    """A Rivada Xa Resource-Allocation message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXaResourceAllocation.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388709
    name: str = "Rivada Xa Resource-Allocation"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXaResourceRelease(UndefinedMessage):
    """A Rivada Xa Resource-Release message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXaResourceRelease.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388710
    name: str = "Rivada Xa Resource-Release"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXaResourceReleaseNotification(UndefinedMessage):
    """A Rivada Xa Resource-Release-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXaResourceReleaseNotification.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388711
    name: str = "Rivada Xa Resource-Release-Notification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class RivadaXhUserData(UndefinedMessage):
    """A Rivada Xh User-Data message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [RivadaXhUserData.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388712
    name: str = "Rivada Xh User-Data"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProSeInitialLocationInformation(UndefinedMessage):
    """A ProSe-Initial-Location-Information message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProSeInitialLocationInformation.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388713
    name: str = "ProSe-Initial-Location-Information"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NokiaSessionSync(UndefinedMessage):
    """A Nokia Session-Sync message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NokiaSessionSync.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388714
    name: str = "Nokia Session-Sync"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NokiaSessionMassSync(UndefinedMessage):
    """A Nokia Session-Mass-Sync message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NokiaSessionMassSync.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388715
    name: str = "Nokia Session-Mass-Sync"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NokiaFetchSession(UndefinedMessage):
    """A Nokia Fetch-Session message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NokiaFetchSession.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388716
    name: str = "Nokia Fetch-Session"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class EricssonTraceReport(UndefinedMessage):
    """An Ericsson-Trace-Report message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [EricssonTraceReport.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388717
    name: str = "Ericsson-Trace-Report"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ConfigurationInformation(UndefinedMessage):
    """A Configuration-Information message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ConfigurationInformation.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388718
    name: str = "Configuration-Information"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ReportingInformation(UndefinedMessage):
    """A Reporting-Information message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ReportingInformation.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388719
    name: str = "Reporting-Information"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NonAggregatedRUCIReport(UndefinedMessage):
    """A Non-Aggregated-RUCI-Report message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NonAggregatedRUCIReport.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388720
    name: str = "Non-Aggregated-RUCI-Report"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class AggregatedRUCIReport(UndefinedMessage):
    """An Aggregated-RUCI-Report message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [AggregatedRUCIReport.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388721
    name: str = "Aggregated-RUCI-Report"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ModifyUecontext(UndefinedMessage):
    """A Modify-Uecontext message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ModifyUecontext.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388722
    name: str = "Modify-Uecontext"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class BackgroundDataTransfer(UndefinedMessage):
    """A Background-Data-Transfer message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [BackgroundDataTransfer.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388723
    name: str = "Background-Data-Transfer"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NetworkStatus(UndefinedMessage):
    """A Network-Status message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NetworkStatus.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388724
    name: str = "Network-Status"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NetworkStatusContinuousReport(UndefinedMessage):
    """A Network-Status-Continuous-Report message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NetworkStatusContinuousReport.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388725
    name: str = "Network-Status-Continuous-Report"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NIDDInformation(UndefinedMessage):
    """An NIDD-Information message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NIDDInformation.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388726
    name: str = "NIDD-Information"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ProXimityApplication(UndefinedMessage):
    """A ProXimity-Application message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ProXimityApplication.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388727
    name: str = "ProXimity-Application"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class DataPull(UndefinedMessage):
    """A Data-Pull message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [DataPull.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388728
    name: str = "Data-Pull"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class DataUpdate(UndefinedMessage):
    """A Data-Update message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [DataUpdate.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388729
    name: str = "Data-Update"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class NotificationData(UndefinedMessage):
    """A Notification-Data message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [NotificationData.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388730
    name: str = "Notification-Data"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class TSSFNotification(UndefinedMessage):
    """A TSSF-Notification message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [TSSFNotification.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388731
    name: str = "TSSF-Notification"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class ConnectionManagement(UndefinedMessage):
    """A Connection-Management message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [ConnectionManagement.append_avp][diameter.message.Message.append_avp]
    method.
    """
    code: int = 8388732
    name: str = "Connection-Management"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class MOData(UndefinedMessage):
    """An MO-Data message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [MOData.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388733
    name: str = "MO-Data"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


class MTData(UndefinedMessage):
    """An MT-Data message.

    This message implementation provides no python subclasses for requests and
    answers; AVPs must be created manually and added using the
    [MTData.append_avp][diameter.message.Message.append_avp] method.
    """
    code: int = 8388734
    name: str = "MT-Data"

    def __post_init__(self):
        super().__post_init__()
        self.header.command_code = self.code


all_commands: dict[int, Type[Message]] = {
    m.code: m for m in Message.__subclasses__()}
all_commands.update({
    m.code: m for m in DefinedMessage.__subclasses__()
})
all_commands.update({
    m.code: m for m in UndefinedMessage.__subclasses__()
})
