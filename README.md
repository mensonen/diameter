# Python Diameter Stack

This Python package provides tools to create and parse Diameter Messages and 
AVPs, to communicate with diameter peers using the diameter base protocol and 
to write diameter applications, as defined in the Diameter Base `rfc6733`.

The diameter stack supports transports over both *TCP* and *SCTP*.

The provided Application and Node implementations handle the majority of the 
basic protocol-level operations automatically, such as managing peer tables, 
sending CER/CEA, DWR/DEA and disconnecting with DPR/DPA. 

## Installation

The latest version can be installed from PyPI as 
[python-diameter](https://pypi.org/project/python-diameter/):

```shell
~# pip install python-diameter
```

SCTP support provided by an optional depency on [pysctp](https://pypi.org/project/pysctp/).

## Functional overview

The package contains an extensive AVP dictionary and allows constructing
AVPs and Diameter messages either manually, or by parsing network-received 
bytes. Message AVPs can be accessed directly as instance attributes.

The `diameter` package provides tools for:

- [Parsing and writing AVPs](https://python-diameter.org/docs/current/guide/avp/)
- [Parsing and writing diameter Mesages](https://python-diameter.org/docs/current/guide/message/)
- [Creating diameter nodes and connecting to other peers](https://python-diameter.org/docs/current/guide/node/)
- [Writing diameter applications](https://python-diameter.org/docs/current/guide/application/)

## Supported applications

The diameter stack has inbuilt support for Diameter Base, *Gy*, *Rf*, *Ro*, 
*Sy*, *Cx* and *Dx* applications and a generic implementation of application 
types that allows working even with unsupported application types.

## Supported diameter application commands

The diameter stack provides a Python command class for the following 
application message types:

*Diameter Base Protocol* `rfc3588`, `rfc6733`

 * Abort-Session
 * Accounting
 * Capabilities-Exchange
 * Device-Watchdog
 * Disconnect-PeerConnection
 * Re-Auth
 * Session-Termination

*Diameter Mobile IPv4* `rfc4004`

 * AA-Mobile-Node
 * Home-Agent-MIP

*Diameter Network Access Server* `rfc4005`, `rfc7155`

 * AA
 * Abort-Session
 * Accounting
 * Re-Auth
 * Session-Termination

*Diameter Credit Control* `rf4006`, `rfc6733`, `3GPP TS 32.299`

 * Credit-Control, with full 3GPP specification support

*Diameter Extensible Authentication Protocol (EAP)* `rfc4072`
 
 * Diameter-EAP

*Diameter Policy and charging control* `3GPP TS 29.219`

 * Spending-Limit
 * Spending-Status-Notification

*Diameter Cx and Dx interfaces* `3GPP TS 29.229`

 * User-Authorization
 * Server-Assignment
 * Location-Info
 * Multimedia-Auth
 * Registration-Termination
 * Push-Profile

*Diameter S6a/S6d interface* `3GPP TS 29.272`
 * Update-Location
 * Cancel-Location-Request
 * Authentication-Information
 * Insert-Subscriber-Data
 * Delete-Subscriber-Data
 * Purge-UE
 * Reset
 * Notify

*Diameter S13 interface* `3GPP TS 29.272`

 * ME-Identity-Check

*Diameter S7a/S7d interface* `3GPP TS 29.272`

 * Update-VCSG-Location
 * Insert-Subscriber-Data
 * Delete-Subscriber-Data
 * Reset-Request
 * Cancel-VCSG-Location-Request

*Diameter Sh interface* `3GPP TS 29.329`

 * User-Data
 * Profile-Update
 * Subscribe-Notifications
 * Push-Notification

The stack includes also a generic fallback Python class for every other message.