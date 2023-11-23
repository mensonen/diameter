# Diameter library

This Python module provides tools to create and parse Diameter Messags and AVPs,
as defined in `rfc6733`, `rfc8506` and `rfc5777`. 

The module contains an extensive AVP dictionary, based on the current Wireshark
Diameter dictionary.xml (and kept up to date frequently) and allows constructing
AVPs and Diameter messages either manually, or by parsing network-received 
bytes. For messages described in the Diameter Base and Diameter Credit Control
RFCs, additional Message types are provided, which permit reading and updating
message AVPs as python instance properties.

Minimum required Python version is 3.11.

## Parsing and creating messages

### Message parsing

Network-received bytes can be converted directly to Python types:

```python
from diameter.message import Message

# Will generate a diameter.message.commands.CreditControlRequest insance
ccr = Message.from_bytes(b"\x01\x00\x02\x90\xc0 ... ")

# AVPs are directly accessible as attributes:
assert ccr.origin_host == b"dra2.gy.mno.net"
assert ccr.destination_realm == b"mvno.net"
# Works also for Grouped AVPs:
assert ccr.multiple_services_credit_control[0].requested_service_unit.cc_total_octets == 0
```

AVPs not part of the base RFCs can be retrieved by searching, using the 
`find_avps` instance method:

```python
from diameter.message import Message
from diameter.message.constants import *

# Will generate a diameter.message.commands.CreditControlRequest insance
ccr = Message.from_bytes(b"\x01\x00\x02\x90\xc0 ... ")
# Find accepts tuples of AVP-vendor pairs to search. More than one pair is 
# interpreted as a nested chain, i.e. an AVP within an AVP. This searches for 
# a "3GPP-RAT-Type" AVP within a "PS-Information" AVP within a 
# "Service-Information" AVP, all TGPP vendor AVPs. 
avps = ccr.find_avps(
    (AVP_TGPP_SERVICE_INFORMATION, VENDOR_TGPP), 
    (AVP_TGPP_PS_INFORMATION, VENDOR_TGPP),
    (AVP_TGPP_3GPP_RAT_TYPE, VENDOR_TGPP))
assert avps[0].value == b"\x06"
```

Python implementations with direct attribute access are currently provided for 
the following Diameter Commands:
* Abort-Session
* Accounting
* Capabilities-Exchange
* Credit-Control
* Device-Watchdog
* Disconnect-Peer
* Re-Auth
* Session-Termination

Other command types can be parsed, but their AVPs cannot be accessed as 
attributes:

```python
from diameter.message import Message
from diameter.message.constants import *

# Contains a 3GPP-Update-Location-Request
ulr = Message.from_bytes(b"\x01\x00\x02\xc8\xc0\x00 ... ")
assert ulr.session_id == ""  # Raises an AttributeError

# Searching will work:
session_id = ulr.find_avps((AVP_SESSION_ID, 0))[0]
```

In addition, a `diameter.message.dump` method exists, which converts any valid
Diameter message structure into a human-readable output, such as:

```
3GPP-Update-Location <Version: 0x01, Length: 712, Flags: 0xc0 (request, proxyable), Hop-by-Hop Identifier: 0x73e4, End-to-End Identifier: 0x40b6>
  Session-Id <Code: 0x107, Flags: 0x40 (-M-), Length: 78, Val: mnc003.mcc228.3gppnetwork.org;02472683>
  Vendor-Specific-Application-Id <Code: 0x104, Flags: 0x40 (-M-), Length: 32>
    Vendor-Id <Code: 0x10a, Flags: 0x40 (-M-), Length: 12, Val: 10415>
    Auth-Application-Id <Code: 0x102, Flags: 0x40 (-M-), Length: 12, Val: 16777251>
  Auth-Session-State <Code: 0x115, Flags: 0x40 (-M-), Length: 12, Val: 1>
  ...
```


### Message building

Message types that have a Python implementation can be built by creating new 
instances of the needed type:

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

Commands can be constructed manually as well, in case a Python implementaion is
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