---
shallow_toc: 2
---
This example demonstrates a server-client setup with two scripts that connect
to each other, one as the sender and one as the receiver. The scripts do 
nothing except send keepalive device-watchdog-request occasionally (roughly 
every 20 seconds).

## Server

This file is available as `examples/idle_server.py`.

```python
-8<- "examples/idle_server.py"
```

## Client

This file is available as `examples/idle_client.py`.

```python
-8<- "examples/idle_client.py"
```