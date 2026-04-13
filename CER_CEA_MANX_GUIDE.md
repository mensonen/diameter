# Diameter Client CER/CEA Configuration Guide (Manx Reference)

## Overview

This guide explains how to properly configure a Diameter client to connect to a Diameter server using the Capabilities Exchange (CER/CEA) protocol, based on the Manx (Nokia SR-OS-MG) reference format.

---

## Understanding CER/CEA

### What is CER/CEA?

**CER (Capabilities-Exchange-Request)** and **CEA (Capabilities-Exchange-Answer)** are the first messages exchanged when a Diameter client connects to a server. They allow both sides to:

1. **Identify each other** - Origin-Host and Origin-Realm
2. **Negotiate capabilities** - Which applications are supported
3. **Determine vendors** - Which vendor-specific extensions both support
4. **Verify configuration** - Ensure realms match and are trusted

### Why CER/CEA Fails

The most common reasons for connection failures are:

| Issue | Symptom | Fix |
|-------|---------|-----|
| Wrong Vendor ID | CER sent, no CEA response | Check with server admin, update vendor_id |
| Unsupported App ID | CER sent, CEA with error | Use correct Auth-Application-Id |
| Realm mismatch | CER sent, no CEA response | Verify Origin-Realm matches server expectations |
| Binding to wrong IP | Socket bind error | Use 0.0.0.0 to let OS choose, or specific IP |

---

## Manx Reference Format

From the Manx (Nokia SR-OS-MG) example provided:

### CER (Client Sends)
```
Capabilities-Exchange-Request (CER)
  ApplicationId: 0
  Origin-Host: mscp05.gpgw-01
  Origin-Realm: worldov.com
  Host-IP-Address: 10.0.5.90
  Vendor-Id: 6527                          ← Nokia
  Product-Name: SR-OS-MG
  Origin-State-Id: 1753697272
  Supported-Vendor-Id: 10415               ← 3GPP
  Supported-Vendor-Id: 5535                ← Alternative vendor
  Auth-Application-Id: 4                   ← Credit Control (Gy)
```

### CEA (Server Responds)
```
Capabilities-Exchange-Answer (CEA)
  ApplicationId: 0
  Result-Code: 2001                        ← SUCCESS
  Origin-Host: diameter01.eseye.com
  Origin-Realm: diameter.eseye.com
  Host-IP-Address: 192.168.111.4
  Vendor-Id: 0                             ← Generic
  Product-Name: diamserver
  Origin-State-Id: 1753697272
  Auth-Application-Id: 4                   ← Credit Control
  Supported-Vendor-Id: 10415               ← 3GPP support confirmed
  Firmware-Revision: 267
```

### Key Fields Explained

| Field | Manx Value | Your Value | Notes |
|-------|-----------|-----------|-------|
| Origin-Host | mscp05.gpgw-01 | client01.eseye.net | Unique client identifier |
| Origin-Realm | worldov.com | diameter.eseye.net | Must exist in server config |
| Host-IP-Address | 10.0.5.90 | 0.0.0.0 or your IP | IP of the interface the client binds to |
| Vendor-Id | 6527 (Nokia) | 0 (Generic) | Get from server admin if specific vendor required |
| Supported-Vendor-Id | 10415, 5535 | Your vendor list | Vendors your client supports |
| Product-Name | SR-OS-MG | diamserver | Your product identifier |
| Auth-Application-Id | 4 | 4 | 4 = Credit Control (Gy), check with server if different |
| Origin-State-Id | 1753697272 | Timestamp | Timestamp of client startup |

---

## Configuration Steps

### Step 1: Identify Your Vendor and Application Requirements

**Contact your server administrator to provide:**

1. **Vendor ID** - What should your client advertise?
   ```
   Common values:
   - 0 = Generic (no vendor-specific extensions)
   - 10415 = 3GPP
   - 6527 = Nokia
   - Other: Get from your vendor
   ```

2. **Required Applications**
   ```
   Common values:
   - 4 = Credit Control (Gy/Ro)
   - 16777236 = SIP
   - 16777251 = MIPv4
   ```

3. **Supported Vendors List**
   - Which vendor IDs must be supported?
   - Example: [10415, 5535]

4. **Realm Configuration**
   - What realm names are trusted?
   - Client realm vs. Server realm

5. **Host IP Address**
   - Should it be 0.0.0.0 (auto) or specific IP?
   - Example: 10.0.5.90

### Step 2: Update Client Configuration

Edit `examples/nlb_client_manx.py` and update the `CLIENT_CONFIG` section:

```python
CLIENT_CONFIG = {
    "identity": {
        "origin_host": "YOUR_HOSTNAME",           # e.g., "client01.eseye.net"
        "origin_realm": "YOUR_REALM",             # e.g., "diameter.eseye.net"
        "product_name": "YOUR_PRODUCT",           # e.g., "diamserver"
        "vendor_id": 0,                           # Get from server admin
        "supported_vendor_ids": [10415, 5535],    # Update as needed
        "host_ip_address": "0.0.0.0",             # or specific IP
        "firmware_revision": 1
    },
    "server": {
        "host": "NLB_FQDN",                       # Your NLB FQDN
        "realm": "SERVER_REALM",                  # Server's realm
        "port": 3868                              # Standard Diameter port
    }
}
```

### Step 3: Enable Debug Logging

The client logs all CER/CEA exchanges to two files:

1. **`nlb_client_manx_debug.log`** - Full debug output
2. **`cer_cea_debug.log`** - CER/CEA details only

### Step 4: Run the Client

```powershell
cd C:\Diameter\diameter_project
python examples\nlb_client_manx.py
```

### Step 5: Monitor the Logs

Watch for CER/CEA exchange:

```powershell
# In PowerShell, follow the logs in real-time:
Get-Content -Tail 50 -Wait cer_cea_debug.log
```

**Success indicators:**
- ✓ `[CER EXCHANGE] Sending Capabilities-Exchange-Request...`
- ✓ `[CER EXCHANGE] Received Capabilities-Exchange-Answer!`
- ✓ `Result-Code: 2001 (SUCCESS)`

**Failure indicators:**
- ✗ `WARNING <PeerConnection> was last available peer connection` 
- ✗ `connection has been lost for X seconds, reconnecting`
- ✗ No CEA received after CER sent

---

## Troubleshooting

### Problem 1: "OSError: An operation was attempted on something that is not a socket"

**Cause:** Socket binding to wrong address on Windows

**Solution:**
```python
# In nlb_client_manx.py, update:
"host_ip_address": "0.0.0.0"  # Let OS choose available interface
```

### Problem 2: "OSError: The requested address is not valid in its context"

**Cause:** Trying to bind to an IP that doesn't exist on your machine

**Solution:**
```python
# Find your actual IP address in PowerShell:
ipconfig

# Then use either:
"host_ip_address": "0.0.0.0"      # Auto-detect (recommended)
# OR
"host_ip_address": "192.168.x.x"  # Your actual IP from ipconfig
```

### Problem 3: CEA Not Received After CER Sent

**Possible causes:**
1. **Wrong Vendor ID** - Server doesn't accept this vendor
2. **Unsupported Application** - Server doesn't support App ID 4
3. **Realm not trusted** - Server doesn't recognize the realm
4. **Network connectivity** - Can't reach server

**Debug process:**
```powershell
# 1. Check logs for what CER contains
Get-Content cer_cea_debug.log | Select-String "SENT CER" -A 20

# 2. Compare with what server expects
# Contact server admin with CER details

# 3. Verify DNS resolution
[System.Net.Dns]::GetHostAddresses("your-nlb-fqdn.com")

# 4. Verify TCP connectivity
Test-NetConnection -ComputerName your-nlb-fqdn.com -Port 3868
```

### Problem 4: Wrong Supported Vendor IDs

**Check current CER content in logs:**
```
Supported-Vendor-Id: [YOUR_VALUES_HERE]
```

**Update if needed:**
```python
"supported_vendor_ids": [10415, 5535],  # 3GPP and alternative
```

---

## Debugging Checklist

Before contacting support, verify:

- [ ] DNS resolution works: `nslookup your-nlb-fqdn.com`
- [ ] TCP connectivity works: `Test-NetConnection -ComputerName ... -Port 3868`
- [ ] Client logs show CER being sent
- [ ] Check `cer_cea_debug.log` for what's in CER
- [ ] Ask server admin to confirm:
  - [ ] Client realm is trusted
  - [ ] Vendor ID matches expectations
  - [ ] Application ID 4 is supported
  - [ ] Server is accepting connections
- [ ] Verify firewall allows port 3868 outbound
- [ ] Check server logs for rejection reason

---

## Example Log Output (Success)

```
2026-02-18 14:31:52,594 diameter.node          INFO    [CER EXCHANGE] Sending Capabilities-Exchange-Request...

======================================================================
SENT CER (Capabilities-Exchange-Request)
======================================================================
  Header:
    ApplicationId: 0
    Hop-by-Hop-Id: 1234567890
    End-to-End-Id: 0987654321

  AVPs:
    Origin-Host: client01.eseye.net
    Origin-Realm: diameter.eseye.net
    Host-IP-Address: 192.168.1.100
    Vendor-Id: 0
    Product-Name: diamserver
    Origin-State-Id: 1739886712
    Auth-Application-Id: 4 (Credit-Control)
======================================================================

2026-02-18 14:31:53,594 diameter.node          INFO    [CER EXCHANGE] Received Capabilities-Exchange-Answer!

======================================================================
RECEIVED CEA (Capabilities-Exchange-Answer)
======================================================================
  Header:
    ApplicationId: 0
    Hop-by-Hop-Id: 1234567890
    End-to-End-Id: 0987654321

  AVPs:
    Result-Code: 2001 (SUCCESS)
    Origin-Host: diameter01.eseye.com
    Origin-Realm: diameter.eseye.com
    Host-IP-Address: 172.30.15.203
    Vendor-Id: 0
    Product-Name: diamserver
    Origin-State-Id: 1739886712
    Auth-Application-Id: 4 (Credit-Control)
    Supported-Vendor-Id: 10415
======================================================================

2026-02-18 14:31:53,595 diameter.node          INFO    <PeerConnection(7ac123ec681b, k8s-diameter-...> is now ready
```

---

## Next Steps

Once CER/CEA successfully exchanges:

1. **Verify connection is stable** - Monitor for 5+ minutes
2. **Send test messages** - Create CCR (Credit-Control-Request)
3. **Load testing** - Gradually increase message volume
4. **Monitor logs** - Check for any errors or warnings
5. **Optimize timeout values** - Adjust reconnect_wait if needed

---

## Support Information

**For issues, collect:**

1. Full `cer_cea_debug.log`
2. Full `nlb_client_manx_debug.log`
3. Server admin confirmation of expected values
4. Network connectivity test results
5. Error messages (copy exact error text)

**Contact:** Your server administrator with logs and configuration details.

