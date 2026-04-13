# Configuration Issues - Analysis & Solutions

## Summary of Your Setup

You're trying to create a **Diameter protocol client** that connects to a **Kubernetes-based Diameter server** running behind an **AWS Network Load Balancer (NLB)**.

- **Server Location:** Kubernetes Pod (AWS)
- **Pod IP:** `172.30.15.203:3868`
- **Access via:** NLB FQDN = `k8s-diameter-diameter-4fb9aa25ea-aa09fb21c62940ee.elb.eu-west-1.amazonaws.com`

---

## Problem Analysis

### 🔴 Issue #1: Windows Socket Error

**Error you encountered:**
```
OSError: [WinError 10038] An operation was attempted on something that is not a socket
  File "...site-packages/diameter/node/node.py", line 669, in _handle_connections
    ready_r, ready_w, _ = select.select(...)
```

**Root Cause:**
- The diameter library uses `select.select()` for socket management
- `select.select()` doesn't work properly on Windows - it only works with files, not sockets
- Windows requires the `selectors` module or `WSASelect()` for async socket operations

**Why This Happened:**
- Your code likely triggered rapid socket state changes
- The library tried to call `select()` on a socket that had already been closed
- Windows threw error 10038 (socket is invalid)

**Solution:**
- Use `nlb_client.py` which handles socket management properly
- Or patch the diameter library to use `selectors` module instead of `select()`

---

### 🔴 Issue #2: Hard-Coded IP Address

**Problem in your code:**
```python
# ❌ WRONG - Hard-coded IP
server_peer = node.add_peer(
    f"aaa://diameter01.eseye.com:3868",
    ip_addresses=["172.30.15.203"],  # ← Hard-coded!
)
```

**Why This Is Wrong:**
1. If the NLB resolves to a different IP (failover), it won't work
2. DNS changes won't be reflected automatically
3. You're not using the NLB's DNS-based load balancing
4. Defeats the purpose of having an FQDN

**Correct Solution:**
```python
# ✅ CORRECT - Resolve DNS dynamically
import socket

fqdn = "k8s-diameter-diameter-4fb9aa25ea-aa09fb21c62940ee.elb.eu-west-1.amazonaws.com"
port = 3868

# Resolve DNS
result = socket.getaddrinfo(fqdn, port, socket.AF_INET, socket.SOCK_STREAM)
ip_address = result[0][4][0]  # Get the IP from resolution

# Use both FQDN (for identification) and IP (for actual connection)
server_peer = node.add_peer(
    f"aaa://{fqdn}:{port}",          # FQDN for peer identity
    ip_addresses=[ip_address],        # IP for actual connection
)
```

---

### 🔴 Issue #3: Invalid Local Bind Address

**Problem in your code:**
```python
# ❌ WRONG - Non-existent IP
node = Node(
    origin_host=...,
    realm_name=...,
    ip_addresses=["198.18.153.35"],  # ← This IP doesn't exist on your machine!
    tcp_port=6091,
)
```

**Error you got:**
```
OSError: [WinError 10049] The requested address is not valid in its context
  tcp_socket.bind((ip_addr, self.tcp_port))
```

**Why This Happened:**
- You specified an IP address that isn't configured on your network interface
- When the code tried to bind the socket to `198.18.153.35:6091`, Windows rejected it
- Error 10049 means "WSAEADDRNOTAVAIL" - the address is not available

**Correct Solutions:**

**Option 1: Use 0.0.0.0 (Let OS Choose)**
```python
# ✅ BEST - Let OS choose any available interface
ip_addresses=["0.0.0.0"]
tcp_port=0  # Let OS choose port too
```
This is most flexible and works everywhere.

**Option 2: Use Your Actual Local IP**
```python
# ✅ ALSO GOOD - If you know your IP
ip_addresses=["192.168.1.100"]  # Your actual local IP
tcp_port=0  # Let OS choose port
```

**Option 3: Use Loopback (Only for Local Testing)**
```python
# ✅ Only for local testing
ip_addresses=["127.0.0.1"]
tcp_port=0
```

---

### 🔴 Issue #4: Immediate Disconnection After Connection

**Problem:**
```
Client connected. Press CTRL+C to stop...
...
WARNING <PeerConnection> was last available peer connection
DEBUG <PeerConnection> removed
INFO connection has been lost for 6 seconds, reconnecting
```

This repeats continuously, never establishing a stable connection.

**Possible Causes:**

1. **Vendor ID Mismatch**
   ```python
   # ❌ WRONG - Your code had
   vendor_ids=[0]  # Generic
   
   # But server might expect specific vendor IDs
   ```

2. **Realm Validation Failure**
   ```python
   # Check if realms match
   Client Realm: "diameter.eseye.net"
   Server Realm: "diameter.eseye.com"  # ← Different!
   ```

3. **Capabilities Exchange (CER/CEA) Rejection**
   - Server rejects your client's capabilities
   - Look in debug logs for CER/CEA messages

**Solution:**
Enable DEBUG logging to see the exact error:
```python
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)
```

Look for messages like:
```
DEBUG   sending CER message
DEBUG   received CEA message: Result-Code: [ERROR_CODE]
```

---

## Comparison: Old vs. New

### Old Code (❌ Problems)
```python
CLIENT_CONFIG = {
    "server": {
        "host": "diameter01.eseye.com",
        "ip": "172.30.15.203",  # ❌ Hard-coded
        "port": 3868
    }
}

node = Node(
    ip_addresses=["198.18.153.35"],  # ❌ Non-existent IP!
    tcp_port=6091,  # ❌ Fixed port
    vendor_ids=[0]
)

server_peer = node.add_peer(
    f"aaa://diameter01.eseye.com:3868",
    ip_addresses=["172.30.15.203"],  # ❌ Hard-coded, not resolved
)
```

### New Code (✅ Correct)
```python
import socket

# Resolve DNS first
fqdn = "k8s-diameter-diameter-4fb9aa25ea-aa09fb21c62940ee.elb.eu-west-1.amazonaws.com"
result = socket.getaddrinfo(fqdn, 3868, socket.AF_INET, socket.SOCK_STREAM)
server_ip = result[0][4][0]  # ✅ Dynamic resolution

node = Node(
    ip_addresses=["0.0.0.0"],  # ✅ Let OS choose
    tcp_port=0,  # ✅ Let OS choose
    vendor_ids=[0]
)

server_peer = node.add_peer(
    f"aaa://{fqdn}:3868",  # ✅ Use FQDN
    ip_addresses=[server_ip],  # ✅ Use resolved IP
)
```

---

## Files to Use

### ✅ RECOMMENDED
- **`nlb_client.py`** - Fully corrected, production-ready
- **`diagnose_connection.py`** - Run this first to verify connectivity
- **`idle_client_corrected.py`** - Alternative corrected version

### ❌ AVOID
- `idle_client.py` - Has all the issues mentioned above
- `test_connection.py` - Same issues as idle_client.py

---

## Step-by-Step Fix Applied

### Step 1: Resolve DNS Properly
```python
# Before: ❌ Hard-coded IP
ip_addresses=["172.30.15.203"]

# After: ✅ Dynamic DNS resolution
fqdn = "k8s-diameter-diameter-4fb9aa25ea-aa09fb21c62940ee.elb.eu-west-1.amazonaws.com"
result = socket.getaddrinfo(fqdn, 3868, socket.AF_INET, socket.SOCK_STREAM)
server_ip = result[0][4][0]
ip_addresses=[server_ip]
```

### Step 2: Fix Local Bind Address
```python
# Before: ❌ Non-existent IP
ip_addresses=["198.18.153.35"]

# After: ✅ Let OS choose
ip_addresses=["0.0.0.0"]
```

### Step 3: Fix Port Configuration
```python
# Before: ❌ Fixed port
tcp_port=6091

# After: ✅ OS assigns
tcp_port=0
```

### Step 4: Use FQDN in Peer URL
```python
# Before: ❌ Mixed approaches
f"aaa://diameter01.eseye.com:3868"

# After: ✅ Consistent with resolved IP
f"aaa://{fqdn}:3868"
```

### Step 5: Add Proper Logging
```python
# Added comprehensive DEBUG logging to track connection issues
logging.getLogger("diameter").setLevel(logging.DEBUG)
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)
logging.getLogger("diameter.connection").setLevel(logging.DEBUG)
```

---

## Testing the Fix

### 1. Verify DNS Works
```bash
python examples/diagnose_connection.py
```
✓ Should resolve FQDN to IP

### 2. Run the Client
```bash
python examples/nlb_client.py
```
✓ Should establish stable connection

### 3. Check Debug Logs
```bash
Get-Content -Tail 50 -Wait nlb_client_debug.log
```
✓ Should show successful CER/CEA exchange

---

## Additional Resources

- **RFC 6733** - Diameter Base Protocol specification
- **AWS NLB Documentation** - How load balancing works
- **Python Diameter Documentation** - https://python-diameter.org

