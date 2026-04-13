# Diameter Client CEA Timeout - Troubleshooting Guide

## The Problem

Your client is connecting to the server successfully, but **the server is not responding with a CEA (Capabilities Exchange Answer)**. The connection sequence looks like:

```
Client → Server: TCP connection established
Client → Server: CER (Capabilities Exchange Request) sent
Server → Client: ??? (No CEA response)

Result: Connection times out and is dropped
```

This repeats continuously, never establishing a stable connection.

---

## Why This Happens

The Capabilities Exchange (CER/CEA) is the first message exchange in Diameter. It allows the client and server to negotiate:
1. **Vendor IDs** - Which vendor-specific extensions are supported
2. **Applications** - Which Diameter applications are supported (e.g., Gy, Cx, etc.)
3. **Realms** - The Diameter realm names
4. **Host names** - Origin-Host identities
5. **Security** - TLS/DTLS requirements

If **ANY of these don't match** the server's expectations, the server will:
- Reject the CER silently (no CEA response)
- Or send a CEA with a failure result code

---

## Debug Information from Your Logs

Looking at your `nlb_client_debug.log`, the CER being sent contains:

```
Vendor-Id: 99999                    ← This might be wrong!
Product-Name: python-diameter
Origin-Host: client01.eseye.net
Origin-Realm: diameter.eseye.net
Auth-Application-Id: 4              ← This is Diameter Credit Control (Gy)
```

**The key issue:** Your client is sending `Vendor-Id: 99999` but this might not match what the server expects.

---

## Solution Steps

### Step 1: Verify Server Configuration

**Ask your server administrator:**
1. What Vendor ID should the client use?
2. What Application IDs does the server accept?
3. What realms does the server trust?
4. Does the server require TLS/DTLS?

### Step 2: Update Client Configuration

Based on the server's configuration, update the client as follows:

**If the server accepts generic (vendor ID 0):**
```python
SUPPORTED_VENDORS = [0]
```

**If the server requires 3GPP (common for telecom):**
```python
from diameter.message.constants import VENDOR_TGPP, VENDOR_ETSI, VENDOR_TGPP2

SUPPORTED_VENDORS = [VENDOR_TGPP, VENDOR_ETSI, VENDOR_TGPP2]
```

**If the server requires specific vendor:**
```python
SUPPORTED_VENDORS = [VENDOR_CISCO]  # Or whatever vendor the server needs
```

### Step 3: Update Application ID

The current configuration uses `APP_DIAMETER_CREDIT_CONTROL_APPLICATION` (ID: 4). If your server doesn't support this:

```python
# Check what the server supports and change to:
app = SimpleThreadingApplication(
    APP_RELAY,  # For relay/proxy mode
    is_auth_application=True
)
```

### Step 4: Verify Realm Configuration

Ensure realms match:
```python
# Client sends:
Origin-Realm: "diameter.eseye.net"

# Server must recognize this realm
# And server sends back:
Origin-Realm: "diameter.eseye.com"
```

---

## Testing Steps

### 1. Run the Diagnostic Script First

This checks basic connectivity:
```bash
python examples/diagnose_connection.py
```

All should pass (DNS resolution, TCP connectivity).

### 2. Run the Updated Client

```bash
python examples/diameter_fqdn_nld_client.py
```

### 3. Monitor the Debug Log

```bash
Get-Content -Tail 100 -Wait diameter_fqdn_nld_client.log
```

**Look for:**
- `SENT ... Capabilities-Exchange` - CER is being sent ✓
- `RECEIVED ... Capabilities-Exchange` - CEA is received ✓
- `WARNING <PeerConnection> was last available peer connection` - CEA NOT received ✗

### 4. Check Server Logs

The server must have logs showing:
- Incoming CER from your client
- Why it rejected/dropped the CER (if it did)
- Any configuration issues

---

## Common Issues and Fixes

### Issue 1: Wrong Vendor ID

**Symptom:** CER sent but no CEA response

**Fix:** Check with server admin and update:
```python
# Current (probably wrong)
SUPPORTED_VENDORS = [0]

# Try 3GPP (very common)
SUPPORTED_VENDORS = [VENDOR_TGPP]
```

### Issue 2: Realm Mismatch

**Symptom:** CER sent but no CEA response

**Check:** The server's expected realm:
```python
CLIENT_CONFIG["identity"]["origin_realm"] = "diameter.eseye.net"  # Must match server config
```

### Issue 3: Unsupported Application

**Symptom:** CER sent but no CEA response

**Fix:** Check server's supported applications:
```python
# Current: APP_DIAMETER_CREDIT_CONTROL_APPLICATION (ID: 4)
# Try: APP_RELAY (Generic relay)

app = SimpleThreadingApplication(
    APP_RELAY,
    is_auth_application=True
)
```

### Issue 4: Origin-Host Not Trusted

**Symptom:** CER sent but no CEA response

**Fix:** Server must trust this origin-host:
```python
# Current
"origin_host": "client01.eseye.net"

# Check with server admin - must be whitelisted
```

---

## What the Fixed Client Does

The updated `diameter_fqdn_nld_client.py` now includes:

1. **Better logging of configuration:**
   ```
   Origin Host: client01.eseye.net
   Product Name: python-diameter       ← Changed from "diamserver"
   Vendor IDs: [0]                     ← Configurable
   Local Bind IP: 0.0.0.0
   ```

2. **CEA timeout detection:**
   ```
   If CEA not received after 30 seconds:
   - Warning logged
   - Suggests possible causes
   - Suggests next debugging steps
   ```

3. **Better error messages:**
   ```
   ⚠ WARNING: CEA not received after 30 seconds
   Possible causes:
   1. Server rejected the CER (check vendor_id, realm, or origin_host)
   2. Server is not responding (check if server is running)
   3. Network connectivity issue (firewall, routing)
   4. Check server logs for why it rejected the CER
   ```

---

## Running the Fixed Client

```bash
# Go to the project directory
cd C:\Diameter\diameter_project

# Run the updated client with better debugging
python examples/diameter_fqdn_nld_client.py
```

---

## Next Steps

1. **Get server configuration details** from the server administrator:
   - Expected vendor IDs
   - Expected realm names
   - Supported applications
   - Any authentication requirements

2. **Update the configuration** in `diameter_fqdn_nld_client.py` based on server requirements

3. **Test again** and monitor the debug logs

4. **If still failing**, share the debug logs and server configuration with your team

---

## Key Files

- **Client:** `examples/diameter_fqdn_nld_client.py` (UPDATED - Use this)
- **Debug Log:** `diameter_fqdn_nld_client.log`
- **Diagnostic:** `examples/diagnose_connection.py`

