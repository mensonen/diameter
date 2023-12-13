# Python Diameter Stack

This Python package provides tools to create and parse Diameter Messags and 
AVPs, to communicate with diameter peers using the diameter base protocol and 
to write diameter applications, as defined in `rfc6733`, `rfc8506` and 
`rfc5777`. 

The package contains an extensive AVP dictionary and allows constructing
AVPs and Diameter messages either manually, or by parsing network-received 
bytes. For messages described in the Diameter Base and Diameter Credit Control
RFCs, additional python types are provided, which permit reading and updating
message AVPs as python instance properties.

The `diameter` package provides tools for:

- [Parsing and writing AVPs](https://mensonen.github.io/diameter/guide/avp)
- [Parsing and writing diameter Mesages](https://mensonen.github.io/diameter/guide/message)
- [Creating diameter nodes and connecting to other peers](https://mensonen.github.io/diameter/guide/node)
- [Writing diameter applications](https://mensonen.github.io/diameter/guide/application)

In terms of diameter connectivity, the diameter stack supports both *TCP* and
*SCTP*, with SCTP support provided by an optional depency on 
[pysctp](https://pypi.org/project/pysctp/).

The diameter Application and Node implementations handle the majority of the 
basic protocol-level operations automatically, such as managing peer tables, 
sending CER/CEA, DWR/DEA and disconnecting with DPR/DPA. 

The latest version can be installed from PyPI as 
[python-diameter](https://pypi.org/project/python-diameter/):

```shell
~# pip install python-diameter
```
