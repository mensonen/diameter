# Python Diameter Stack

This Python package provides tools to create and parse Diameter Messages and 
AVPs, to communicate with diameter peers using the diameter base protocol and 
to write diameter applications, as defined in the Diameter Base `rfc6733`.

The diameter stack supports transports over both *TCP* and *SCTP*, with 
SCTP support provided by an optional depency on [pysctp](https://pypi.org/project/pysctp/).

The provided Application and Node implementations handle the majority of the 
basic protocol-level operations automatically, such as managing peer tables, 
sending CER/CEA, DWR/DEA and disconnecting with DPR/DPA. 

## Functional overview

The package contains an extensive AVP dictionary and allows constructing
AVPs and Diameter messages either manually, or by parsing network-received 
bytes. Message AVPs can be accessed directly as instance attributes.

The `diameter` package provides tools for:

- [Parsing and writing AVPs](guide/avp.md)
- [Parsing and writing diameter Mesages](guide/message.md)
- [Creating diameter nodes and connecting to other peers](guide/node.md)
- [Writing diameter applications](guide/application.md)

## Supported applications

The diameter stack has inbuilt support for Diameter Base, *Gy*, *Rf*, *Ro* and
*Sy* applications and a generic implementation of application types that allows
working even with unsupported application types.

## Supported diameter application commands

The diameter stack provides a Python command class for the following 
application message types:

*Diameter Base Protocol* `rfc3588`, `rfc6733`
:   * Abort-Session
    * Accounting
    * Capabilities-Exchange
    * Device-Watchdog
    * Disconnect-PeerConnection
    * Re-Auth
    * Session-Termination

*Diameter Mobile IPv4* `rfc4004`
:   * AA-Mobile-Node
    * Home-Agent-MIP

*Diameter Network Access Server* `rfc4005`, `rfc7155`
:   * AA
    * Abort-Session
    * Accounting
    * Re-Auth
    * Session-Termination

*Diameter Credit Control* `rf4006`, `rfc6733`, `3GPP TS 32.299`
:   * Credit-Control, with full 3GPP specification support

*Diameter Extensible Authentication Protocol (EAP)* `rfc4072`
:   * Diameter-EAP

*Diameter Policy and charging control* `rfc4072`
:   * Spending-Limit
    * Spending-Status-Notification

The stack includes also a generic fallback Python class for every other message.
