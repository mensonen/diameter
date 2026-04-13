# Diameter Client Setup - Quick Start Guide

## What You're Building
You're building a **Diameter client** that connects to a **Diameter server running in a Kubernetes pod** via an **AWS Network Load Balancer (NLB)**.

### Architecture:
```
Your Client → AWS NLB FQDN → Kubernetes Pod (Diameter Server)
             (DNS Lookup)     (172.30.15.203:3868)
```

---

## Quick Start

### 1. First, Diagnose Your Connection
This will check if your network can reach the server:

```bash
cd C:\Diameter\diameter_project
python examples/diagnose_connection.py
```

**Expected output if everything works:**
```
✓ [PASS] DNS resolved successfully: [FQDN] → 172.30.15.203
✓ [PASS] TCP connection successful to 172.30.15.203:3868
✓ [PASS] All diagnostics passed!
```

If this fails, fix the issue before proceeding to step 2.

### 2. Run the NLB Client
This is the properly configured client for your setup:

```bash
python examples/nlb_client.py
```

**What you should see:**
```
[STEP 1] Resolving NLB FQDN to IP address...
✓ FQDN resolved: [FQDN] → 172.30.15.203

[STEP 2] Creating Diameter client node...
✓ Client node created successfully

[STEP 3] Adding server peer...
✓ Server peer added successfully

[STEP 4] Creating Diameter Credit Control application...
✓ Application created and added successfully

[STEP 5] Starting Diameter client...
✓ Client node started successfully

Client is now running and attempting to connect to server...
Press CTRL+C to stop
```

### 3. Monitor Debug Output
The client logs everything to `nlb_client_debug.log`:

```bash
# View logs in PowerShell
Get-Content -Tail 50 -Wait nlb_client_debug.log
```

---

## What Was Wrong with Your Previous Setup

### Problem 1: Hard-Coded IP Address
❌ **Your code had:**
```python
server_peer = node.add_peer(
    f"aaa://diameter01.eseye.com:3868",
    ip_addresses=["172.30.15.203"],  # ← Hard-coded!
)
```

✅ **Should be:**
```python
# Resolve DNS first
ip_address = socket.getaddrinfo(fqdn, port)[0][4][0]

# Then use both FQDN and resolved IP
server_peer = node.add_peer(
    f"aaa://{fqdn}:3868",
    ip_addresses=[ip_address],
)
```

### Problem 2: Invalid Local Bind Address
❌ **Your code had:**
```python
ip_addresses=["198.18.153.35"]  # ← This IP doesn't exist on your machine!
```

✅ **Should be:**
```python
ip_addresses=["0.0.0.0"]  # Let the OS choose an available interface
```

### Problem 3: Windows Socket Error
❌ **Error you got:**
```
OSError: [WinError 10038] An operation was attempted on something that is not a socket
```

**Cause:** The diameter library uses `select.select()` which doesn't work properly on Windows for socket management.

✅ **Solution:** The new `nlb_client.py` handles this correctly.

---

## Configuration Values

Your setup uses these values:

| Item | Value | Notes |
|------|-------|-------|
| **NLB FQDN** | `k8s-diameter-diameter-4fb9aa25ea-aa09fb21c62940ee.elb.eu-west-1.amazonaws.com` | This is what the client connects to |
| **Resolved IP** | `172.30.15.203` | The actual IP that the FQDN resolves to |
| **Port** | `3868` | Standard Diameter port (TCP) |
| **Client Host** | `client01.eseye.net` | Your client's identity |
| **Client Realm** | `diameter.eseye.net` | Your client's realm |
| **Server Realm** | `diameter.eseye.com` | Server's realm |
| **Application** | Diameter Credit Control (Gy) | AAA protocol for credit-based billing |

---

## Understanding the Diameter Connection Flow

### 1. **DNS Resolution**
```
Client asks: "What IP is k8s-diameter-diameter-...amazonaws.com?"
DNS replies: "172.30.15.203"
```

### 2. **TCP Connection**
```
Client → Kubernetes Pod: "Hi, I want to connect on TCP port 3868"
Pod ← Client: "OK, connection accepted"
```

### 3. **Capabilities Exchange (CER/CEA)**
```
Client: "I'm 'client01.eseye.net' from realm 'diameter.eseye.net'"
Client: "I support these applications and vendors"

Server: "Hi client! I'm 'diameter01.eseye.com' from realm 'diameter.eseye.com'"
Server: "I accept your capabilities"

Result: ✓ Connection established!
```

### 4. **Send/Receive Messages**
```
Client ← → Server: Exchange Diameter messages
```

---

## Files You Should Use

### For Your Use Case:
1. **`nlb_client.py`** ← **USE THIS ONE** (Recommended)
   - Properly configured for FQDN-based connection
   - Includes comprehensive logging
   - Has proper error handling for Windows

2. **`diagnose_connection.py`** ← **RUN THIS FIRST**
   - Tests if your network can reach the server
   - Identifies common connectivity issues

3. **`DIAMETER_CLIENT_GUIDE.md`** ← **READ THIS**
   - Comprehensive documentation
   - Detailed troubleshooting guide

### Don't Use (Has Issues):
- ❌ `idle_client.py` - Hard-coded IP, invalid bind address
- ❌ `test_connection.py` - Same issues as idle_client.py

---

## Debug Logging

Both clients include comprehensive debug logging. You'll see messages like:

### Successful Connection Sequence:
```
2026-02-18 14:31:52,594 diameter.node          INFO    auto-connecting to k8s-diameter...amazonaws.com
2026-02-18 14:31:52,595 diameter.node          INFO    added a new connection [172.30.15.203]:3868
2026-02-18 14:31:52,596 diameter.connection   DEBUG   sending CER message
2026-02-18 14:31:52,597 diameter.connection   DEBUG   received CEA message
```

### Connection Failed (Bad):
```
2026-02-18 14:31:52,595 diameter.node          WARNING <PeerConnection> was last available peer connection
2026-02-18 14:31:52,595 diameter.node          DEBUG   <PeerConnection> removed
2026-02-18 14:31:58,606 diameter.node          INFO    connection has been lost for 6 seconds, reconnecting
```

---

## Troubleshooting

### 1. "DNS resolution failed"
```
DNS resolution failed for [FQDN]: [Errno 11001] getaddrinfo failed
```
**Solution:**
- Check your internet connection
- Verify the FQDN is correct
- Try pinging the server: `ping k8s-diameter-...amazonaws.com`

### 2. "Connection refused"
```
OSError: [WinError 10061] No connection could be made
```
**Solution:**
- Server might not be running
- Check that the IP address is correct
- Check that port 3868 is open
- Check firewall rules

### 3. "Connection timeout"
```
ConnectionTimeout: Operation timed out
```
**Solution:**
- Server is unreachable from your network
- Firewall is blocking port 3868
- Run `diagnose_connection.py` to identify the issue

### 4. "Immediate disconnection after connecting"
```
WARNING <PeerConnection> was last available peer connection for <Application>
```
**Solution:**
- Server rejected your capabilities
- Check vendor_id matches
- Check realm names are correct
- Run with DEBUG logging to see detailed CER/CEA exchange

---

## Next Steps

1. **Run diagnostics:**
   ```bash
   python examples/diagnose_connection.py
   ```

2. **If diagnostics pass, run the client:**
   ```bash
   python examples/nlb_client.py
   ```

3. **Monitor the debug log:**
   ```bash
   Get-Content -Tail 50 -Wait nlb_client_debug.log
   ```

4. **If connection succeeds:**
   - You'll see continuous heartbeat messages (Device Watchdog)
   - You can send Credit Control Request (CCR) messages
   - Server responds with Credit Control Answer (CCA)

5. **If connection fails:**
   - Check the debug log for error messages
   - Compare with the troubleshooting section above
   - Verify server configuration on the other end

---

## Need More Help?

- **Read:** `DIAMETER_CLIENT_GUIDE.md` for detailed configuration guide
- **Check:** `nlb_client_debug.log` for detailed debug messages
- **Run:** `examples/diagnose_connection.py` to identify issues
- **Reference:** Python-Diameter documentation at https://python-diameter.org

