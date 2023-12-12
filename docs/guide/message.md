# Parsing and writing messages

The `diameter` package contains python implementations for the command messages
described in the Diameter Base protocol, and for other, commonly used messages,
such as credit control.


## Reading mesasges

Messages received from the network can be converted directly to Python types 
using [`Message.from_bytes`][diameter.message.Message.from_bytes].

```python
from diameter.message import Message
from diameter.message.commands import CreditControlRequest

ccr = Message.from_bytes(b"\x01\x00\x02\x90\xc0 ... ")
assert isinstance(ccr, CreditControlRequest)
```

Messages that have a Python implementation (e.g. "Accounting", "Credit-Control")
are further split into "Request" and "Answer" classes. Parsing an Accounting
message that is also a request will return an instance of 
[`AccountingRequest`][diameter.message.commands.accounting.AccountingRequest],
while an answer would return an instance of 
[`AccountingRequest`][diameter.message.commands.accounting.AccountingRequest].

Python implementations with direct attribute access are currently provided for 
the following Diameter Commands:

 * Abort-Session
 * Accounting
 * Capabilities-Exchange
 * Credit-Control
 * Device-Watchdog
 * Disconnect-PeerConnection
 * Re-Auth
 * Session-Termination

For messages that do not have a Python implementation, an instance of 
[`Message`][diameter.message.Message], or one of its subclasses is returned. 
For these, refer to [the full list](../api/commands/other_commands.md).


### Reading AVPs

For any command message that has a Python implementation, any AVP part of the 
RFC can be accessed as an instance attribute:

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

For AVPs not part of the RFCs, a [`find_avps`][diameter.message.Message.find_avps] 
instance method is provided, which can be used to find any AVP within a message:

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

This will also work for message types that have no Python implementation:

```python
from diameter.message import Message
from diameter.message.constants import *

# Contains a 3GPP-Update-Location-Request
ulr = Message.from_bytes(b"\x01\x00\x02\xc8\xc0\x00 ... ")
assert ulr.session_id == ""  # Raises an AttributeError

# Searching will work:
session_id = ulr.find_avps((AVP_SESSION_ID, 0))[0]
```


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
from diameter.message import Avp, Message
from diameter.message.constants import *

msg = Message()
msg.header.command_code = 262
msg.header.is_request = True
msg.avps = [
    Avp.new(AVP_SESSION_ID, value="mnc003.mcc228.3gppnetwork.org;02472683")
]
# etc
msg.as_bytes()
```