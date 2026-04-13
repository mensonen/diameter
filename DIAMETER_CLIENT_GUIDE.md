# Diameter Client Configuration Guide - NLB Connection

## Project Overview

This is a Python Diameter protocol client/server implementation. Diameter is an authentication, authorization, and accounting (AAA) protocol commonly used in telecom networks.

### Key Components:
- **Diameter Node**: Represents a network element that communicates with other Diameter nodes
- **Diameter Peers**: Other Diameter nodes that this node communicates with
- **Diameter Applications**: Protocol implementations for specific use cases (e.g., Credit Control, Authentication)
- **AVPs**: Attribute-Value Pairs (the data in Diameter messages)

---

## Your Setup: Client → NLB → Diameter Pod Server

Your architecture:
```
┌──────────────────┐         ┌─────────────────────────────┐
│  Diameter Client │ ──────→ │  AWS NLB (Network Load      │
│   (Local/Remote) │ TCP:    │  Balancer) FQDN             │
└──────────────────┘ 3868    └──────────────────────────────┘
                                        │
                                        ↓
                              ┌─────────────────────┐
                              │  Diameter Pod       │
                              │  (Kubernetes)       │
                              │  IP: 172.30.15.203  │
                              │  Port: 3868         │
                              └─────────────────────┘
```

---

## Configuration Details

### Server Details (Your Setup)
- **NLB FQDN**: `k8s-diameter-diameter-4fb9aa25ea-aa09fb21c62940ee.elb.eu-west-1.amazonaws.com`
- **Resolved IP**: `172.30.15.203`
- **Port**: `3868` (Standard Diameter port)
- **Protocol**: TCP
- **Realm**: `diameter.eseye.com`

### Client Configuration
- **Origin Host**: `client01.eseye.net`
- **Realm**: `diameter.eseye.net`
- **Local Bind IP**: `0.0.0.0` (Let OS choose available interface)
- **Local Port**: Dynamic (OS-assigned)
- **Application**: Diameter Credit Control (Gy)

---

## Issues in Your Previous Attempts

### Issue 1: Hard-coded IP Instead of FQDN
**Problem**: The client was configured with hard-coded IP `172.30.15.203`
```python
# ❌ BAD: Hard-coded IP
server_peer = node.add_peer(
    f"aaa://{ip_address}:3868",
    ip_addresses=["172.30.15.203"],
)
```

**Solution**: Use FQDN for the peer address, then provide resolved IP
```python
# ✅ GOOD: FQDN with DNS resolution
server_ip = socket.getaddrinfo(fqdn, port)[0][4][0]
server_peer = node.add_peer(
    f"aaa://{fqdn}:3868",
    ip_addresses=[server_ip],  # Resolved IP
)
```

### Issue 2: Invalid Bind Address
**Problem**: `198.18.153.35` doesn't exist on your machine
```python
# ❌ BAD: Non-existent local IP
ip_addresses=["198.18.153.35"]
```

**Solution**: Use `0.0.0.0` to let the OS choose
```python
# ✅ GOOD: Let OS select local interface
ip_addresses=["0.0.0.0"]
```

Or use the actual local IP of your machine:
```python
# ✅ ALSO GOOD: Specific local IP
ip_addresses=["192.168.1.100"]  # Your actual local IP
```

### Issue 3: Socket Error on Windows
**Problem**: `OSError: [WinError 10038] An operation was attempted on something that is not a socket`
- This occurs in the Diameter library's socket handling
- On Windows, `select.select()` doesn't work the same as Unix
- The library has issues with socket lifecycle management

**Solution**: 
1. Use the provided `nlb_client.py` which handles this properly
2. Or update the library to use `selectors` module instead of `select()`

### Issue 4: Immediate Disconnection
**Problem**: Connection established but immediately dropped with:
```
WARNING <PeerConnection> was last available peer connection
DEBUG <PeerConnection> removed
INFO connection has been lost for 6 seconds, reconnecting
```

**Causes**:
1. Capabilities Exchange (CER/CEA) negotiation failing
2. TLS/SSL configuration mismatch
3. Vendor ID mismatch
4. Realm validation failure

**Solution**:
- Ensure `vendor_ids` match between client and server
- Check that realms are properly configured
- Verify server accepts your client's identity

---

## Running the Client

### Option 1: Using the New NLB Client (Recommended)
```bash
cd C:\Diameter\diameter_project
python examples/nlb_client.py
```

This will:
1. Resolve the NLB FQDN to IP
2. Create a Diameter client node
3. Add the server as a peer
4. Start the client
5. Log all DEBUG level messages to console and `nlb_client_debug.log`

### Option 2: Using the Updated idle_client.py
```bash
python examples/idle_client.py
```

---

## Understanding the Logs

### What You Should See:

**Successful Connection Sequence:**
```
[1] Creating client node...
[2] Client node created successfully
[3] Adding server peer...
[4] Server peer added successfully
[5] Creating Diameter Credit Control application...
[6] Application created and added successfully
[7] Starting Diameter client...
[8] Client node started successfully

THEN (in DEBUG logs):
INFO    auto-connecting to [NLB_FQDN]
INFO    added a new connection [172.30.15.203]:3868 for peer Peer<(NLB_FQDN)>
DEBUG   connection established
```

### What Goes Wrong:

**DNS Resolution Failure:**
```
DNS resolution failed for [FQDN]: [Errno 11001] getaddrinfo failed
```
→ Check your network connectivity and that the FQDN is correct

**Connection Refused:**
```
Connection refused
OSError: [WinError 10061] No connection could be made
```
→ Server is not running or the IP/port is wrong

**Capabilities Exchange Failed:**
```
WARNING <PeerConnection> was last available peer connection
INFO connection has been lost for 6 seconds, reconnecting
```
→ Server rejected your client's capabilities (vendor_id, realm, etc.)

---

## Debugging Tips

### Enable More Detailed Logging
The logging configuration already includes DEBUG level, but you can customize it:

```python
# Show message hex dumps (very verbose)
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)

# Show connection events
logging.getLogger("diameter.connection").setLevel(logging.DEBUG)

# Show AVP parsing
logging.getLogger("diameter.message").setLevel(logging.DEBUG)
```

### Check Firewall
On Windows:
```powershell
# Allow port 3868 (Diameter)
New-NetFirewallRule -DisplayName "Allow Diameter" `
    -Direction Outbound -LocalPort 3868 -Protocol TCP -Action Allow
```

### Test Basic Connectivity
```python
import socket

fqdn = "k8s-diameter-diameter-4fb9aa25ea-aa09fb21c62940ee.elb.eu-west-1.amazonaws.com"
port = 3868

# Test DNS resolution
try:
    ip = socket.getaddrinfo(fqdn, port)[0][4][0]
    print(f"✓ Resolved: {fqdn} → {ip}")
except Exception as e:
    print(f"✗ DNS failed: {e}")

# Test TCP connectivity
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((ip, port))
    print(f"✓ TCP connection to {ip}:{port} successful")
    s.close()
except Exception as e:
    print(f"✗ TCP connection failed: {e}")
```

---

## Key Configuration Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `origin_host` | `client01.eseye.net` | Identifies your client to the server |
| `origin_realm` | `diameter.eseye.net` | Realm your client belongs to |
| `host_ip_address` | `0.0.0.0` | Local IP to bind to (0.0.0.0 = any) |
| `tcp_port` | `0` | Local port (0 = let OS choose) |
| `vendor_ids` | `[0]` | Vendor ID (0 = generic) |
| `server_host` | FQDN | NLB FQDN (for DNS resolution) |
| `server_ip` | `172.30.15.203` | Resolved IP address |
| `server_port` | `3868` | Server port |
| `server_realm` | `diameter.eseye.com` | Server's realm |

---

## Common Configuration Mistakes to Avoid

❌ **DON'T:**
- Use hard-coded IPs if DNS/NLB is available
- Specify non-existent local IP addresses
- Forget to resolve FQDN before connecting
- Use mismatched vendor_ids
- Configure wrong realms

✅ **DO:**
- Use FQDN in peer URI, resolved IP in `ip_addresses`
- Use `0.0.0.0` for automatic local interface selection
- Verify DNS resolution before attempting connection
- Match vendor_ids with server configuration
- Verify realm names match across configurations

---

## Files in This Project

- **`nlb_client.py`** - Proper NLB/FQDN-based client (RECOMMENDED)
- **`idle_client.py`** - Original client (has issues)
- **`idle_server.py`** - Simple Diameter server
- **`test_connection.py`** - Connection test script
- **`tests/`** - Unit tests for various Diameter applications

---

## Next Steps

1. **Run the NLB client:**
   ```bash
   python examples/nlb_client.py
   ```

2. **Check the debug log:**
   ```bash
   # View in real-time
   Get-Content -Tail 20 -Wait nlb_client_debug.log
   ```

3. **Verify connection status** from the logs

4. **If connection fails**, check:
   - DNS resolution working?
   - TCP port 3868 reachable?
   - Server running and accepting connections?
   - Vendor ID and realm configuration?

---

## Additional Resources

- [Diameter RFC 6733](https://tools.ietf.org/html/rfc6733)
- [python-diameter Documentation](https://python-diameter.org)
- [Diameter Credit Control (Gy) Application](https://tools.ietf.org/html/rfc4006)

