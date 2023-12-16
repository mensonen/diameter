# Using the diameter stack

The `diameter` package offers tools for parsing and creating AVPs, parsing and
creating diameter messages, connecting to diameter peers and writing diameter
applications.

## Modules

The entire package can be imported as `diameter`. It provides following 
importable modules:

* `diameter.message`
    * `diameter.message.avp`
    * `diameter.message.commands`
    * `diameter.message.constants`
* `diameter.node`
    * `diameter.node.application`
    * `diameter.node.peer`


### AVP and message modules

The AVP and message handling modules are part of `diameter.message`.

```python
# base class for parsing and creating AVPs
from diameter.message import Avp

# subclasses of AVPs are in the `avp` module
from diameter.message.avp import AvpTime, AvpOctetString

# all package constants for AVPs, applications, vendors, enums etc
from diameter.message.constants import *
```

See [working with AVPs](avp.md) for a guide on AVPs.

```python
# base class for parsing and creating messages
from diameter.message import Message

# subclasses of messages ae in the `commands` module
from diameter.message.commands import AbortSessionRequest, ReAuthRequest
```

See [working with messages](message.md) for a guide on diameter messages.


### Node, application and peer modules

The diameter connectivity and application support are part of `diameter.node`.

```python
# Nodes and peers
from diameter.node import Node
from diameter.node.peer import Peer, PeerConnection
```

See [connecting to peers](node.md) for a guide on node and peer connectivity.

```python
# application base classes
from diameter.node.application import Application, SimpleThreadingApplication
```

See [application basics](application.md) and [sample application](sample_application.md)
for guides on writing applications.