# Quick Action Plan - Get Connected Now

## What to Do Right Now

### 1. Run This Command (Takes 30 seconds)
```bash
cd C:\Diameter\diameter_project
python examples/diameter_fqdn_nld_client.py
```

### 2. Watch the Output

You will see:
```
======================================================================
Diameter Client - NLB/FQDN Connection
======================================================================

[STEP 1] Resolving NLB FQDN to IP address...
✓ FQDN resolved: k8s-diameter-...amazonaws.com -> 172.30.X.X

[STEP 2] Creating Diameter client node...
  Origin Host: client01.eseye.net
  Origin Realm: diameter.eseye.net
  Product Name: python-diameter          ← FIXED
  Vendor IDs: [0]                         ← FIXED
  Local Bind IP: 0.0.0.0

[STEP 3] Adding server peer...
✓ Server peer added successfully

[STEP 4] Creating Diameter Credit Control application...
✓ Application created and added successfully

[STEP 5] Starting Diameter client...
✓ Client node started successfully

WAITING FOR CAPABILITIES EXCHANGE (CER/CEA)...
- Client has sent CER (Capabilities Exchange Request)
- Waiting for server to respond with CEA...
```

### 3. Wait 30 Seconds and Look For:

#### ✅ SUCCESS (Connection Works):
```
SENT k8s-diameter-...
Capabilities-Exchange <Version: 0x01, ... sent ...>

RECEIVED k8s-diameter-...
Capabilities-Exchange <... received ...>

Still running... (30 seconds elapsed)
```
→ **If you see this, your connection is working!** Press CTRL+C to stop.

#### ❌ FAILURE (Connection Doesn't Work):
```
SENT k8s-diameter-...
Capabilities-Exchange <... sent ...>

Still running... (30 seconds elapsed)
⚠ WARNING: CEA not received after 30 seconds
  Possible causes:
  1. Server rejected the CER (check vendor_id, realm, or origin_host)
  2. Server is not responding (check if server is running)
  3. Network connectivity issue (firewall, routing)
  4. Check server logs for why it rejected the CER
```
→ **If you see this, the server is rejecting the connection.** Follow steps below.

---

## If Connection Fails

### Step 1: Check Basic Connectivity
```bash
python examples/diagnose_connection.py
```

If this FAILS: Network/DNS problem → Fix network issues first
If this PASSES: Continue to Step 2

### Step 2: Get Server Configuration
Contact your server administrator and ask:
- **What Vendor ID(s) should the client use?** (Default: 0)
- **What Application IDs does the server support?** (Default: 4 for Credit Control)
- **What realms does the server trust?** (Default: diameter.eseye.com)

### Step 3: Update Client Configuration

Edit `examples/diameter_fqdn_nld_client.py`:

**If server needs generic:**
```python
SUPPORTED_VENDORS = [0]  # Already set
```

**If server needs 3GPP (telecom common):**
```python
# At the top, add this import
from diameter.message.constants import VENDOR_TGPP, VENDOR_ETSI, VENDOR_TGPP2

# Then update vendor IDs
SUPPORTED_VENDORS = [VENDOR_TGPP, VENDOR_ETSI, VENDOR_TGPP2]
```

**If server needs other vendor:**
```python
# Import the vendor constant from diameter.message.constants
from diameter.message.constants import VENDOR_CISCO

SUPPORTED_VENDORS = [VENDOR_CISCO]
```

### Step 4: Test Again
```bash
python examples/diameter_fqdn_nld_client.py
```

---

## Files and Their Purpose

| File | Purpose | When to Use |
|------|---------|------------|
| `diameter_fqdn_nld_client.py` | Main client (FIXED) | **← USE THIS** |
| `diagnose_connection.py` | Test connectivity | Run first if connection fails |
| `nlb_client_debug.log` | Debug output | Check logs for error details |
| `ERROR_RESOLUTION_SUMMARY.md` | What was fixed | Read if you want details |
| `CEA_TIMEOUT_TROUBLESHOOTING.md` | Detailed troubleshooting | Read if connection fails |
| `QUICK_START.md` | General guide | Reference |
| `DIAMETER_CLIENT_GUIDE.md` | Full documentation | Reference |

---

## Most Common Issues and Quick Fixes

### Issue: "CEA not received after 30 seconds"
**→ Try:** Update SUPPORTED_VENDORS
```python
SUPPORTED_VENDORS = [VENDOR_TGPP]  # If server is 3GPP
```

### Issue: "DNS resolution failed"
**→ Check:** Your internet connection
```bash
ping k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com
```

### Issue: "Connection refused"
**→ Check:** Server is running and firewall allows port 3868

### Issue: "Still running but never connects"
**→ Check:** Server logs - may be rejecting your client identity
**→ Ask:** Server admin if they're seeing your connection attempt

---

## Expected Debug Log Output (Success Case)

```
2026-02-18 20:05:34 diameter.node       INFO   auto-connecting to k8s-diameter-...
2026-02-18 20:05:35 diameter.node       INFO   added a new connection [172.30.X.X]:3868
2026-02-18 20:05:35 diameter.connection INFO   <PeerConnection> is now connected, waiting CER/CEA
2026-02-18 20:05:35 diameter.node       INFO   <PeerConnection> sending CER

2026-02-18 20:05:35 diameter.peer.msg   DEBUG  SENT k8s-diameter-...
                                                Capabilities-Exchange <... sent ...>

2026-02-18 20:05:35 diameter.connection INFO   <PeerConnection> is ready (peer-to-peer connection)
2026-02-18 20:05:35 diameter.node       INFO   <PeerConnection> has been ready for ... seconds
```

---

## Expected Debug Log Output (Failure Case)

```
2026-02-18 20:05:34 diameter.node       INFO   auto-connecting to k8s-diameter-...
2026-02-18 20:05:35 diameter.node       INFO   added a new connection [172.30.X.X]:3868
2026-02-18 20:05:35 diameter.connection INFO   <PeerConnection> is now connected, waiting CER/CEA
2026-02-18 20:05:35 diameter.node       INFO   <PeerConnection> sending CER

2026-02-18 20:05:35 diameter.peer.msg   DEBUG  SENT k8s-diameter-...
                                                Capabilities-Exchange <... sent ...>

2026-02-18 20:05:40 diameter.node       WARNING <PeerConnection> was last available peer connection
2026-02-18 20:05:40 diameter.node       DEBUG  <PeerConnection> removed
2026-02-18 20:05:40 diameter.node       INFO   connection has been lost for 6 seconds, reconnecting
                                               [This repeats...]
```

---

## Summary

**You have:**
- ✅ A properly configured Diameter client
- ✅ Debug logging to see what's happening
- ✅ Timeout detection (30 seconds)
- ✅ Helpful error messages
- ✅ Easy-to-update configuration

**To connect:**
1. Run: `python examples/diameter_fqdn_nld_client.py`
2. Wait 30 seconds
3. Check if CEA is received
4. If not, update vendor ID based on server config

**You're ready to start testing!**

