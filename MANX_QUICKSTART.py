"""
QUICK START: Diameter Client for NLB/Manx Connection
=====================================================

This file contains the essential configuration for connecting to a
Diameter server via NLB (Network Load Balancer) using the Manx format.

BEFORE RUNNING:
1. Update the values below based on your server admin's requirements
2. Run: python examples\nlb_client_manx.py
3. Monitor: Get-Content -Tail 50 -Wait cer_cea_debug.log
"""

# ============================================================================
# STEP 1: GET THESE VALUES FROM YOUR SERVER ADMINISTRATOR
# ============================================================================

# Server Connection Details
NLB_FQDN = "k8s-diameter-diameter-4fb9aa25ea-aa09fb21c62940ee.elb.eu-west-1.amazonaws.com"
SERVER_REALM = "diameter.eseye.com"
SERVER_PORT = 3868

# Client Identity - What your client identifies itself as
CLIENT_ORIGIN_HOST = "client01.eseye.net"        # Your unique identifier
CLIENT_ORIGIN_REALM = "diameter.eseye.net"       # Your realm
CLIENT_PRODUCT_NAME = "diamserver"               # Your product name

# Capabilities - What your client supports
CLIENT_VENDOR_ID = 0                             # Ask server admin! (0 = generic)
CLIENT_SUPPORTED_VENDORS = [10415, 5535]         # Ask server admin!
CLIENT_AUTH_APP_ID = 4                           # 4 = Credit Control (Gy)
                                                  # Ask if different!

# Network Binding
# Use "0.0.0.0" to let OS choose available interface (RECOMMENDED)
# Or specify your actual IP address from: ipconfig
CLIENT_HOST_IP_ADDRESS = "0.0.0.0"

# ============================================================================
# STEP 2: VERIFY YOUR CONFIGURATION
# ============================================================================

# Checklist before running:
CONFIGURATION_CHECKLIST = {
    "NLB_FQDN_resolvable": "Test with: nslookup " + NLB_FQDN,
    "TCP_connectivity": "Test with: Test-NetConnection -ComputerName " + NLB_FQDN + " -Port " + str(SERVER_PORT),
    "Vendor_ID_confirmed": "Contact: server admin for correct value",
    "Realm_trusted": "Contact: server admin to trust '" + CLIENT_ORIGIN_REALM + "'",
    "App_ID_supported": "Contact: server admin if not using App ID " + str(CLIENT_AUTH_APP_ID),
}

print("\n" + "="*70)
print("DIAMETER CLIENT CONFIGURATION QUICK START")
print("="*70)
print("\nYour Configuration:")
print(f"  Server FQDN: {NLB_FQDN}")
print(f"  Server Realm: {SERVER_REALM}")
print(f"  Client Host: {CLIENT_ORIGIN_HOST}")
print(f"  Client Realm: {CLIENT_ORIGIN_REALM}")
print(f"  Vendor ID: {CLIENT_VENDOR_ID}")
print(f"  Auth App ID: {CLIENT_AUTH_APP_ID} (Credit Control)")
print("\nVerify with server admin:")
print(f"  ✓ Vendor ID {CLIENT_VENDOR_ID} is correct?")
print(f"  ✓ Supported Vendors {CLIENT_SUPPORTED_VENDORS} are correct?")
print(f"  ✓ Auth Application ID {CLIENT_AUTH_APP_ID} is supported?")
print(f"  ✓ Client realm '{CLIENT_ORIGIN_REALM}' is trusted?")
print("\n" + "="*70)

# ============================================================================
# STEP 3: EXPECTED CER FORMAT
# ============================================================================

EXPECTED_CER_FORMAT = """
Capabilities-Exchange-Request (CER) to be sent:
  
  Origin-Host: {CLIENT_ORIGIN_HOST}
  Origin-Realm: {CLIENT_ORIGIN_REALM}
  Host-IP-Address: {CLIENT_HOST_IP_ADDRESS} (or actual interface IP)
  Vendor-Id: {CLIENT_VENDOR_ID}
  Product-Name: {CLIENT_PRODUCT_NAME}
  Auth-Application-Id: {CLIENT_AUTH_APP_ID}
  Supported-Vendor-Id: {CLIENT_SUPPORTED_VENDORS}

Expected Server Response (CEA):
  
  Result-Code: 2001 (SUCCESS)
  Origin-Host: (server hostname)
  Origin-Realm: {SERVER_REALM}
  Auth-Application-Id: {CLIENT_AUTH_APP_ID}
  (+ other server capabilities)
""".format(
    CLIENT_ORIGIN_HOST=CLIENT_ORIGIN_HOST,
    CLIENT_ORIGIN_REALM=CLIENT_ORIGIN_REALM,
    CLIENT_HOST_IP_ADDRESS=CLIENT_HOST_IP_ADDRESS,
    CLIENT_VENDOR_ID=CLIENT_VENDOR_ID,
    CLIENT_PRODUCT_NAME=CLIENT_PRODUCT_NAME,
    CLIENT_AUTH_APP_ID=CLIENT_AUTH_APP_ID,
    CLIENT_SUPPORTED_VENDORS=CLIENT_SUPPORTED_VENDORS,
    SERVER_REALM=SERVER_REALM,
)

print("\nExpected CER/CEA Exchange:")
print(EXPECTED_CER_FORMAT)

# ============================================================================
# STEP 4: TROUBLESHOOTING QUICK REFERENCE
# ============================================================================

TROUBLESHOOTING = """
TROUBLESHOOTING QUICK REFERENCE
===============================

Symptom: Socket bind error
  Solution: Change "host_ip_address" to "0.0.0.0" in nlb_client_manx.py

Symptom: DNS resolution failed
  Solution: 
    - Verify FQDN: nslookup {NLB_FQDN}
    - Check network connectivity
    - Contact IT if DNS is blocked

Symptom: Connection refused (TCP fails)
  Solution:
    - Verify port: Test-NetConnection -ComputerName {NLB_FQDN} -Port {SERVER_PORT}
    - Check firewall allows outbound 3868
    - Verify server is running and listening

Symptom: CER sent, no CEA response (keeps reconnecting)
  Solution:
    - Check logs: Get-Content cer_cea_debug.log
    - Compare CER with server expectations
    - Ask server admin about:
      * Vendor ID {CLIENT_VENDOR_ID}
      * Realm {CLIENT_ORIGIN_REALM}
      * Application ID {CLIENT_AUTH_APP_ID}
    - Check server logs for rejection reason

Symptom: CEA received but with error result code
  Solution:
    - Check cer_cea_debug.log for result code meaning
    - Contact server admin with error code
    - Verify all values match server expectations
""".format(
    NLB_FQDN=NLB_FQDN,
    SERVER_PORT=SERVER_PORT,
    CLIENT_VENDOR_ID=CLIENT_VENDOR_ID,
    CLIENT_ORIGIN_REALM=CLIENT_ORIGIN_REALM,
    CLIENT_AUTH_APP_ID=CLIENT_AUTH_APP_ID,
)

print(TROUBLESHOOTING)

# ============================================================================
# STEP 5: HOW TO RUN
# ============================================================================

INSTRUCTIONS = """
RUNNING THE CLIENT
==================

1. Update nlb_client_manx.py with your configuration values from above

2. Run the client:
   cd C:\\Diameter\\diameter_project
   python examples\\nlb_client_manx.py

3. Monitor in real-time:
   Get-Content -Tail 50 -Wait cer_cea_debug.log

4. Look for success indicators:
   ✓ [CER EXCHANGE] Sending Capabilities-Exchange-Request...
   ✓ [CER EXCHANGE] Received Capabilities-Exchange-Answer!
   ✓ Result-Code: 2001 (SUCCESS)

5. If connection succeeds:
   - Let it run for 5+ minutes to verify stability
   - Server admin can send test messages
   - Check for any warnings or disconnections

6. Stop with Ctrl+C
"""

print(INSTRUCTIONS)
print("="*70)

