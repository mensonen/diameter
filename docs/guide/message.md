# Parsing and writing messages

The `diameter` package can parse network-received diameter command messages into
Python structures that have AVP values accessible as instance attributes. Some 
of these structures can also be converted back to actual diameter commands.

The diameter stack handles command messages in three different ways:

1. Full Python implementation
:   A small set of diameter command messages have an implementation written 
    fully in Python. These implementations all inherit from same base class
    [`DefinedMessage`][diameter.message.DefinedMessage] and allow reading AVPs 
    as instance attributes, as well as setting values for AVPs just by assigning 
    a value to an instance attribute. These implementations exist mostly for the
    most commonly used messages, such as CER/CEA, DWR/DEA, CCR/CCA, however the 
    list is extended periodically.

2. Known message with no implementation
:   The stack contains a large list of command messages that are known, but 
    have no actual implementation. These messages inherit 
    [`UndefinedMessage`][diameter.message.UndefinedMessage] and
    also permit reading AVP values as instance attributes. The message class
    attempts to generate an instance attribute name that matches the name of
    each AVP as closely as possible. These messages are essentially read-only,
    the AVP values cannot be altered, and new messages cannot be created by
    assigning values to instance attributes.

3. Unknown messages
:   The diameter stack can also parse messages that are entirely unknown. These
    will also inherit `UndefinedMessage`, however the stack will not be able
    to map them to known command codes and names and will name each message just
    as "Unknown". AVP values are also accessible as instance attributes.



## Reading messages

Messages received from the network can be converted directly to Python types 
using [`Message.from_bytes`][diameter.message.Message.from_bytes].

```python
from diameter.message import Message
from diameter.message.commands import CreditControlRequest

ccr = Message.from_bytes(b"\x01\x00\x02\x90\xc0 ... ")
assert isinstance(ccr, CreditControlRequest)
```

Messages that have a Python implementation (e.g. "Accounting", "Credit-Control")
are further split into "Request" and "Answer" classes. Parsing an "Accounting"
message that is also a request will return an instance of 
[`AccountingRequest`][diameter.message.commands.accounting.AccountingRequest],
while an answer message would return an instance of 
[`AccountingRequest`][diameter.message.commands.accounting.AccountingRequest].

Python implementations with direct attribute access are currently provided for 
the following Diameter Commands:

 * [Aa][diameter.message.commands.Aa]
 * [Aa-Mobile-Node][diameter.message.commands.AaMobileNode]
 * [Abort-Session][diameter.message.commands.AbortSession]
 * [Accounting][diameter.message.commands.Accounting]
 * [Authentication-Information][diameter.message.commands.AuthenticationInformation]
 * [Cancel-Location][diameter.message.commands.CancelLocation]
 * [Cancel-VCSG-Location][diameter.message.commands.CancelVcsgLocation]
 * [CapabilitiesExchange][diameter.message.commands.CapabilitiesExchange]
 * [Credit-Control][diameter.message.commands.CreditControl]
 * [Delete-Subscriber-Data][diameter.message.commands.DeleteSubscriberData]
 * [Device-Watchdog][diameter.message.commands.DeviceWatchdog]
 * [Diameter-EAP][diameter.message.commands.DiameterEap]
 * [Disconnect-Peer][diameter.message.commands.DisconnectPeer]
 * [Home-Agent-MIP][diameter.message.commands.HomeAgentMip]
 * [Insert-Subscriber-Data][diameter.message.commands.InsertSubscriberData]
 * [Location-Info][diameter.message.commands.LocationInfo]
 * [ME-Identity-Check][diameter.message.commands.MeIdentityCheck]
 * [Multimedia-Auth][diameter.message.commands.MultimediaAuth]
 * [Notify][diameter.message.commands.Notify]
 * [Profile-Update][diameter.message.commands.ProfileUpdate]
 * [Purge-UE][diameter.message.commands.PurgeUe]
 * [Push-Notification][diameter.message.commands.PushNotification]
 * [Push-Profile][diameter.message.commands.PushProfile]
 * [Re-Auth][diameter.message.commands.ReAuth]
 * [Registration-Termination][diameter.message.commands.RegistrationTermination]
 * [Reset][diameter.message.commands.Reset]
 * [Server-Assignment][diameter.message.commands.ServerAssignment]
 * [Session-Termination][diameter.message.commands.SessionTermination]
 * [Spending-Limit][diameter.message.commands.SpendingLimit]
 * [Spending-Status-Notification][diameter.message.commands.SpendingStatusNotification]
 * [Subscribe-Notifications][diameter.message.commands.SubscribeNotifications]
 * [Update-Location][diameter.message.commands.UpdateLocation]
 * [Update-VCSG-Location][diameter.message.commands.UpdateVcsgLocation]
 * [User-Authorization][diameter.message.commands.UserAuthorization]
 * [User-Data][diameter.message.commands.UserData]

For messages that do not have a Python implementation, an instance of 
[`UndefinedMessage`][diameter.message.UndefinedMessage], or one of its 
subclasses is returned. For these, refer to 
[the full list](../api/commands/other_commands.md).


### Accessing message AVPs

For any command message that is known to the diameter stack, any AVP part of the 
specification can be accessed as an instance attribute:

```python
from diameter.message import Message

# Will generate a diameter.message.commands.CreditControlRequest instance
ccr = Message.from_bytes(b"\x01\x00\x02\x90\xc0 ... ")

# AVPs are directly accessible as attributes:
assert ccr.origin_host == b"dra2.gy.mno.net"
assert ccr.destination_realm == b"mvno.net"
# Works also for Grouped AVPs:
assert ccr.multiple_services_credit_control[0].requested_service_unit.cc_total_octets == 0
```

For AVPs not part of the specification, a 
[`find_avps`][diameter.message.Message.find_avps] instance method is provided, 
which can be used to find any AVP within a message:

```python
from diameter.message import Message
from diameter.message.constants import *

# Will generate a diameter.message.commands.CreditControlRequest instance
ccr = Message.from_bytes(b"\x01\x00\x02\x90\xc0 ... ")

# Find accepts tuples of AVP-vendor pairs to search. More than one pair is 
# interpreted as a nested chain, i.e. an AVP within a grouped AVP. This chain 
# searches for a "3GPP-RAT-Type" AVP within a "PS-Information" AVP within a 
# "Service-Information" AVP, all TGPP vendor AVPs. 
avps = ccr.find_avps(
    (AVP_TGPP_SERVICE_INFORMATION, VENDOR_TGPP), 
    (AVP_TGPP_PS_INFORMATION, VENDOR_TGPP),
    (AVP_TGPP_3GPP_RAT_TYPE, VENDOR_TGPP))
assert avps[0].value == b"\x06"
```

Command messages that are known to the diameter stack (see 
[the full list](../api/commands/other_commands.md)), but do not have a written 
Python implementation, still provide read-only access to AVPs as instance 
attributes. Command messages that inherit 
[`UndefinedMessage`][diameter.message.UndefinedMessage] attempt to automatically
convert every AVP that the message contains into instance attributes, by 
converting the AVP name to lowercase and replacing dashes with underscore, e.g.
a "Visited-PLMN-Id" AVP becomes a `visited_plmn_id` instance attribute. This 
conversion may also result in attribute names that cannot be accessed using the
dot notation. E.g. a "3GPP-User-Location-Info" converts into 
`3gpp_user_location_info`, which cannot be accessed with dot notation. For 
these, use of `hasattr` and `getattr` is recommended.

The automatic conversion will also work for grouped AVPs. If an AVP appears 
more than once, it will be converted to a list:

```python
from diameter.message import Message
from diameter.message.constants import *

# Contains a 3GPP-Update-Location-Request
ulr = Message.from_bytes(b"\x01\x00\x02\xc8\xc0\x00 ... ")
assert ulr.session_id == "epc.mnc003.mcc228.3gppnetwork.org;02472683;449d027e;13a0091b"
assert ulr.vendor_specific_application_id.auth_application_id == 16777251

# Searching will also work:
session_id = ulr.find_avps((AVP_SESSION_ID, 0))[0]

# In this message, the "Route-Record" AVP is included multiple times, so it has
# been converted to a list:
for route_record in ulr.route_record:
    print(route_record)
```


## AVP validation

For every message that extends [`DefinedMessage`][diameter.message.DefinedMessage],
and is received via network through a [`Node`](node.md), the presence of every
AVP marked as required in their respective specifications is checked. Every AVP
that is missing in an incoming message will result in an automatic message 
rejection and a `DIAMETER_MISSING_AVP` error being returned back to the 
originating peer.

This behaviour may be unwanted, if working with peers that deliberately send 
messages that lack mandatory AVPs. The validation can be turned off by setting
[`Node.validate_received_request_avps`][diameter.node.Node.validate_received_request_avps] 
to `False`. 

This is the only scenario where AVP presence is validated.


## Creating messages

Message types that have a Python implementation can be built by creating new 
instances of the needed type, and AVPs can be set directly as instance 
attributes.

```python
from diameter.message.commands import CreditControlRequest
from diameter.message.constants import *

ccr = CreditControlRequest()
# AVPs included in the base RFCs can be set as instance attributes. AVPs that 
# are listed as mandatory in the spec are also mandatory here
ccr.session_id = "dsrkat01.mnc003.mcc260.3gppnetwork.org;65574b0c-2d02"
ccr.origin_host = b"dra2.gy.mno.net"
ccr.origin_realm = b"mno.net"
ccr.destination_realm = b"mvno.net"
ccr.service_context_id = "32251@3gpp.org"
ccr.cc_request_type = E_CC_REQUEST_TYPE_UPDATE_REQUEST
ccr.cc_request_number = 952
ccr.destination_host = b"dra3.mvno.net"

# Message header can be manipulated as well:
ccr.header.hop_by_hop_identifier = 10001
ccr.header.end_to_end_identifier = 20001
ccr.header.is_proxyable = False

# For AVPs that can appear multiple times, `add_` methods are provided:
ccr.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_E164, "485089163847")
ccr.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, "260036619905065")

# Message can be built by converting it into bytes, which returns the entire
# message, including its header and auto-generates all AVPs
ccr_bytes = ccr.as_bytes()
```

!!! Note
    There is no checking for mandatory AVPs being set; it is the responsibility
    of the implementing party to ensure that all AVPs required are included.
    Leaving out a required AVP will emit a debug log entry, but will produce no
    other visible warning.

For commands that accept additional AVPs according to the RFCs, custom AVPs can
be added:

```python
from diameter.message import Avp
from diameter.message.commands import AbortSessionRequest
from diameter.message.constants import *

asr = AbortSessionRequest()
asr.append_avp(
    Avp.new(AVP_TGPP_ABORT_CAUSE, VENDOR_TGPP, value=E_ABORT_CAUSE_BEARER_RELEASED)
)
```

Commands can be constructed manually as well, in case a Python implementation is
not ready yet, or if custom behaviour is required:

```python
from diameter.message import Avp, Message, dump
from diameter.message.commands import UpdateLocation
from diameter.message.constants import *

# UpdateLocation is known but has no implementation, AVPs must be created
# manually and added to the command
ulr = UpdateLocation()
ulr.header.is_request = True
ulr.avps = [
    Avp.new(AVP_SESSION_ID, value="mnc003.mcc228.3gppnetwork.org;02472683")
]
print(dump(ulr))
# produces:
# 3GPP-Update-Location <Version: 0x01, Length: 68, Flags: 0x80 (request), Hop-by-Hop Identifier: 0x0, End-to-End Identifier: 0x0>
#   Session-Id <Code: 0x107, Flags: 0x40 (-M-), Length: 46, Val: mnc003.mcc228.3gppnetwork.org;02472683>


# When building a message using the `Message` base class, command code must
# be provided manually:
msg = Message()
msg.header.command_code = 262
msg.header.is_request = True
msg.avps = [
    Avp.new(AVP_SESSION_ID, value="mnc003.mcc228.3gppnetwork.org;02472683")
]
print(dump(msg))
# produces:
# Unknown <Version: 0x01, Length: 0, Flags: 0x80 (request), Hop-by-Hop Identifier: 0x0, End-to-End Identifier: 0x0>
#   Session-Id <Code: 0x107, Flags: 0x40 (-M-), Length: 46, Val: mnc003.mcc228.3gppnetwork.org;02472683>

```