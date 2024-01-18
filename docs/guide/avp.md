# Parsing and writing AVPs

The `diameter` package contains an extensive dictionary, with ~2700 AVPs, 
~140 Applications, ~100 command codes, ~30 Vendors and ~2400 ENUM values 
defined. These can be imported as:

```python
from diameter.message.constants import *
```

This imports following constants:

 * `APP_`, application identifiers, e.g. `APP_3GPP_GX`
 * `VENDOR_`, vendor codes, e.g. `VENDOR_NOKIA`
 * `CMD_`, diameter command codes, e.g. `CMD_ACCOUNTING`
 * `AVP_`, diameter AVPs. These are either labeled `AVP_<name>`, for the
    diameter base protocol (e.g. `AVP_SERVICE_TYPE`), or `AVP_<vendor>_<name>`,
    for the vendor-specific AVPs (e.g. `AVP_TGPP_GGSN_ADDRESS`)
 * `E_`, for all the enumerations, e.g. `E_DISCONNECT_CAUSE_BUSY`

The package does support also creating and parsing AVPs that are not included
in the dictionary, as long as the AVP code and its type is known.


## Reading an AVP

Each AVP is an instance of [`Avp`][diameter.message.Avp] and consists of 
attributes `code`, `is_mandatory`, `is_private`, `is_vendor`, `length`, 
`vendor_id` and `value`. 

Most commonly, AVPs are received as bytes from the network and can be converted
into their Python types by using 
[`Avp.from_bytes`][diameter.message.avp.Avp.from_bytes].

```python
from diameter.message import Avp
from diameter.message.constants import *

avp_bytes = bytes.fromhex("000001cd40000016333232353140336770702e6f72670000")
a = Avp.from_bytes(avp_bytes)

assert a.code == 461
assert a.code == AVP_SERVICE_CONTEXT_ID
assert a.is_mandatory is True
assert a.is_private is False
assert a.is_vendor is False
assert a.length == 22
assert a.value == "32251@3gpp.org"
```

When parsing, as long as the AVP is of a known type, an instance of a subclass 
of [`Avp`][diameter.message.Avp] is returned. Each subclass represents a specific
AVP type; e.g. an "Integer32" AVP is represented by 
[`AvpInteger32`][diameter.message.avp.AvpInteger32], a "Grouped" AVP is 
[`AvpGrouped`][diameter.message.avp.AvpGrouped], etc.

The AVPs hold two attributes, `payload` and `value`. The payload is the actual
encoded byte string, while value is the Python value that can be set and read.

```python
from diameter.message.avp import AvpInteger32
from diameter.message.constants import *

a = AvpInteger32(AVP_ACCT_INPUT_PACKETS)
a.value = 294967

assert a.value == 294967  # Python value
assert a.payload == b"\x00\x04\x807"  # Network bytes representation
```

Each individual AVP type has their specific python value, refer to 
[AVP API reference](../api/avp/index.md) for details.


## Creating an AVP

[`Avp.new`][diameter.message.Avp.new] class method is the expected way to 
build new AVPs. It ensures that a correct type of AVP is returned, 
i.e "Float32", "OctetString" etc. AVPs encode and decode their content
automatically according to the RFC, when their `value` attribute is altered.
The actual, byte-encoded payload is stored in the `payload` attribute.

```python
from diameter.message import Avp
from diameter.message.avp import AvpUtf8String
from diameter.message.constants import *

a = Avp.new(AVP_USER_NAME)
# Has returned an instance of AvpUtf8String
assert isinstance(a, AvpUtf8String)
a.value = "汉语"

# `value` is human-readable, `payload` has the network bytes
assert a.value == "汉语"
assert a.payload == b"\xe6\xb1\x89\xe8\xaf\xad"
```

When creating an AVP, its vendor must be specified, if the AVP does not belong
to the Diameter Base RFCs:

```python
from diameter.message import Avp
from diameter.message.constants import *

ua = Avp.new(AVP_CISCO_USER_AGENT, VENDOR_CISCO)
```

When creating an AVP, its flags and value can also be set during creation, 
which can be practical especially for nested "Grouped" type AVPs:

```python
from diameter.message import Avp
from diameter.message.constants import *

ps_information = Avp.new(AVP_TGPP_PS_INFORMATION, VENDOR_TGPP, value=[
    Avp.new(AVP_TGPP_3GPP_PDP_TYPE, VENDOR_TGPP, value=0),
    Avp.new(AVP_TGPP_PDP_ADDRESS, VENDOR_TGPP, value="10.40.93.32")
])
```

Each individual AVP type has their specific type of python value, and 
attempting to set a value that has an invalid type will raise an exception. 
Refer to [AVP API reference](../api/avp/index.md) for details for each AVP 
type.


## Using the AVP dictionary

The package contains a large dictionary that holds a definition for each AVP, 
with which AVPs can be constructed. This dictionary is automatically consulted
when creating AVPs using `Avp.new` and `Avp.from_bytes`, however it permits 
also direct access:

```python
from diameter.message.avp import AvpEnumerated
from diameter.message.avp.dictionary import AVP_DICTIONARY
from diameter.message.constants import *

avp_def =  AVP_DICTIONARY[AVP_SERVICE_TYPE]

assert avp_def["name"] == "Service-Type"
assert avp_def["type"] == AvpEnumerated
assert avp_def["mandatory"] is True
```

Vendor-specific AVPs are stored in individual dictionaries, separate for each 
vendor:

```python
from diameter.message.avp import AvpUtf8String
from diameter.message.avp.dictionary import AVP_VENDOR_DICTIONARY
from diameter.message.constants import *

avp_def =  AVP_VENDOR_DICTIONARY[VENDOR_TGPP][AVP_TGPP_CONTENT_TYPE]

assert avp_def["name"] == "Content-Type"
assert avp_def["type"] == AvpUtf8String
assert avp_def["mandatory"] is True
assert avp_def["vendor"] == 10415
assert avp_def["vendor"] == VENDOR_TGPP
```