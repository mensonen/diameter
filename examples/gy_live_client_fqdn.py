import time
import socket
import logging
from diameter.message import constants

from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication
from diameter.message.constants import *
from diameter.message.commands.credit_control import CreditControlRequest

logging.basicConfig(level=logging.INFO)

# ============================================================
# CONFIG
# ============================================================

FQDN = "k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com"
PORT = 3868

ORIGIN_HOST = "client01.eseye.net"
ORIGIN_REALM = "diameter.eseye.net"
DEST_REALM = "diameter.eseye.com"

LOCAL_IP = "198.18.152.233"

# ============================================================
# Resolve FQDN
# ============================================================

print(f"🔍 Resolving FQDN: {FQDN}")
ip = socket.gethostbyname(FQDN)
print(f"✅ Resolved to: {ip}")

# ============================================================
# Create Node
# ============================================================

node = Node(
    origin_host=ORIGIN_HOST,
    realm_name=ORIGIN_REALM,
    ip_addresses=[LOCAL_IP],
    tcp_port=0,
    vendor_ids=[0],
)

print("✓ Node created")

# ============================================================
# Add Peer (IMPORTANT: aaa://)
# ============================================================

peer = node.add_peer(
    f"aaa://{FQDN}:{PORT}",
    realm_name=DEST_REALM,
    ip_addresses=[ip],
    is_persistent=True,
)

print(f"✓ Peer added via URI: aaa://{FQDN}:{PORT}")

# ============================================================
# Add Gy Application
# ============================================================

app = SimpleThreadingApplication(
    APP_DIAMETER_CREDIT_CONTROL_APPLICATION,
    is_auth_application=True,
)

node.add_application(app, [peer])

# ============================================================
# Start node
# ============================================================

node.start()

print("⏳ Waiting for CER/CEA...")
time.sleep(6)

# ============================================================
# Build CCR-I
# ============================================================

ccr = CreditControlRequest()

ccr.session_id = f"{ORIGIN_HOST};{int(time.time())}"
ccr.origin_host = ORIGIN_HOST.encode()
ccr.origin_realm = ORIGIN_REALM.encode()
ccr.destination_realm = DEST_REALM.encode()
ccr.auth_application_id = APP_DIAMETER_CREDIT_CONTROL_APPLICATION
ccr.cc_request_type = constants.E_CC_REQUEST_TYPE_INITIAL_REQUEST
ccr.cc_request_number = 0

# ⭐ STRONGLY RECOMMENDED FOR REAL OCS
ccr.service_context_id = "32251@3gpp.org"

print("🚀 Sending CCR-I...")

try:
    answer = app.send_request(ccr, peer=peer, timeout=15)

    if answer:
        print("✅ CCA RECEIVED")
        print(answer)
    else:
        print("❌ No CCA received")

except Exception as e:
    print("❌ Error sending CCR:", e)

# ============================================================
# Keep alive
# ============================================================

print("🔄 Keeping session alive for 30s...")
time.sleep(30)

node.stop()
print("✓ Client stopped")
