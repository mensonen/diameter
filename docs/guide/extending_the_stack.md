# Extending the stack

The diameter stack can be extended by adding or overwriting command 
implementations with custom ones, or by defining or overwriting AVP definitions.


## Adding or overwriting AVPs

The [message.avp.avp.register][diameter.message.avp.avp.register] method can be
used to either add new AVP definitions or to overwrite behaviour of existing
AVPs.

```python
# Add a new AVP definition for AVP 90000001 and vendor 9999999
from diameter.message.avp import avp, AvpUtf8String

VENDOR_SPECIAL = 9999999
AVP_SPECIAL_SESSION_ID = 90000001

avp.register(avp=AVP_SPECIAL_SESSION_ID, 
             name="Special-Session-Id", 
             type_cls=AvpUtf8String, 
             vendor=VENDOR_SPECIAL)
```

Existing AVPs can be overwritten by redefining an existing code. When 
overwriting an AVP definition, all the defining values (name, type, vendor, 
etc.) will be overwritten, even if no value was given.


```python
# Overwrite behaviour for "Framed-IPv6-Prefix" AVP so that its value can be 
# given as an IPV6 string instead of bytes containing the necessary data.
import socket

from diameter.message.avp import Avp, avp
from diameter.message.constants import *


class AvpFramedIpv6(Avp):
    @property
    def value(self) -> bytes:
        return self.payload

    @value.setter
    def value(self, new_value: str):
        framed_ipv6 = socket.inet_pton(socket.AF_INET6, new_value)
        self.payload = b"\00" + (len(framed_ipv6) * 8).to_bytes() + framed_ipv6


# Use identical values as the existing definition but change the type from 
# AvpOctetString to AvpFramedIpv6
avp.register(AVP_FRAMED_IPV6_PREFIX, "Framed-IPv6-Prefix", AvpFramedIpv6, 
             mandatory=True)

framed_ipv6_prefix = Avp.new(AVP_FRAMED_IPV6_PREFIX)
framed_ipv6_prefix.value = "2a00:1fa2:c863:8c7e::"
print(framed_ipv6_prefix)

# Prints:
# Framed-IPv6-Prefix <Code: 0x61, Flags: 0x40 (-M-), Length: 26, Val: b'\x00\x80*\x00\x1f\xa2\xc8c\x8c~\x00\x00\x00\x00\x00\x00\x00\x00'>
```

After overwriting or creating an AVP definition, it becomes available globally
and will be used everywhere, where AVPs are concerned, without having to change 
the definition for each command individually:

```python
# After changing the type for Framed-IPv6-Prefix, it can be used everywhere
from diameter.message import dump
from diameter.message.commands.abort_session import AbortSessionRequest

asr = AbortSessionRequest()
asr.framed_ipv6_prefix = ["2a00:1fa2:c863:8c7e::"]
print(dump(asr))

# Prints:
# Abort-Session <Version: 0x01, Length: 0, Flags: 0xc0 (request, proxyable), Hop-by-Hop Identifier: 0x0, End-to-End Identifier: 0x0>
#  Auth-Application-Id <Code: 0x102, Flags: 0x40 (-M-), Length: 12, Val: 0>
#  Framed-IPv6-Prefix <Code: 0x61, Flags: 0x40 (-M-), Length: 26, Val: b'\x00\x80*\x00\x1f\xa2\xc8c\x8c~\x00\x00\x00\x00\x00\x00\x00\x00'>

```

## Adding or overwriting commands

The [message.commands.register][diameter.message.commands.register] method can
be used to either add a new command definition or to overwrite an existing 
command definition. When added, using the 
[Message.from_bytes][diameter.message.Message.from_bytes] method will 
automatically return instances of the added command. If the command also has 
"Request" and "Answer" subclasses, those are returned automatically as well.

```python
# Define a new "Special-Message" command with both request and answer 
# subclasses and AVP definitions and add it to the command registry. The way
# these classes are defined is similar to how all subclasses of `DefinedMessage`
# are implemented in the diameter.message.commands module.

from diameter.message import Message, DefinedMessage, MessageHeader, dump
from diameter.message._base import  _AnyMessageType
from diameter.message.avp.generator import AvpGenDef, AvpGenType
from diameter.message.commands import register
from diameter.message.commands._attributes import assign_attr_from_defs
from diameter.message.constants import *

from typing import Type


class SpecialMessage(DefinedMessage):
    code: int = 999
    name: str = "Special-Message"
    avp_def: AvpGenType

    def __post_init__(self):
        self.header.command_code = self.code
        super().__post_init__()

    @classmethod
    def type_factory(cls, header: MessageHeader) -> Type[_AnyMessageType] | None:
        if header.is_request:
            return SpecialMessageRequest
        return SpecialMessageAnswer


class SpecialMessageRequest(SpecialMessage):
    session_id: str

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = True
        self.header.is_proxyable = True

        assign_attr_from_defs(self, self._avps)
        self._avps = []


class SpecialMessageAnswer(SpecialMessage):
    session_id: str
    result_code: int

    avp_def: AvpGenType = (
        AvpGenDef("session_id", AVP_SESSION_ID, is_required=True),
        AvpGenDef("result_code", AVP_RESULT_CODE, is_required=True)
    )

    def __post_init__(self):
        super().__post_init__()
        self.header.is_request = False
        self.header.is_proxyable = True

        assign_attr_from_defs(self, self._avps)
        self._avps = []


# Adds SpecialMessage and its subclasses to the registry of commands 
register(SpecialMessage)

msg = SpecialMessageRequest()
msg.session_id = "host.realm;1"

print(dump(msg))
# Prints:
# Special-Message <Version: 0x01, Length: 40, Flags: 0xc0 (request, proxyable), Hop-by-Hop Identifier: 0x0, End-to-End Identifier: 0x0>
#  Session-Id <Code: 0x107, Flags: 0x40 (-M-), Length: 20, Val: host.realm;1>

req = Message.from_bytes(msg.as_bytes())
assert isinstance(req, SpecialMessageRequest)

```