"""
Simple Diameter client test to capture debug logs
"""
import logging
import sys
import io

# Set up file logging with UTF-8 encoding
log_file = open('client_test_debug.log', 'w', encoding='utf-8')
handler = logging.StreamHandler(log_file)
handler.setFormatter(logging.Formatter("%(asctime)s %(name)-22s %(levelname)-7s %(message)s"))

# Configure all loggers
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(handler)

# Also add console handler with simple format
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
root_logger.addHandler(console_handler)

# Import after logger setup
from diameter.message.constants import *
from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication
import time

print("[OK] Starting Diameter Client Debug Test", file=sys.stderr)

# Client Configuration
CLIENT_CONFIG = {
    "identity": {
        "origin_host": "client01.eseye.net",
        "origin_realm": "diameter.eseye.net",
        "product_name": "diamserver",
        "vendor_id": 0,
        "firmware_revision": 1,
        "host_ip_address": "198.18.152.207"
    },
    "server": {
        "host": "diameter01.eseye.com",
        "realm": "diameter.eseye.com",
        "ip": "172.30.15.203",
        "port": 3868
    }
}

print("[OK] Creating node...", file=sys.stderr)
# Create client node
node = Node(
    origin_host=CLIENT_CONFIG["identity"]["origin_host"],
    realm_name=CLIENT_CONFIG["identity"]["origin_realm"],
    ip_addresses=[CLIENT_CONFIG["identity"]["host_ip_address"]],
    tcp_port=6091,
    vendor_ids=[0]
)

print(f"[OK] Client configured: {CLIENT_CONFIG['identity']['origin_host']}", file=sys.stderr)

# Add server as peer
print("[OK] Adding server peer...", file=sys.stderr)
server_peer = node.add_peer(
    f"aaa://{CLIENT_CONFIG['server']['host']}:{CLIENT_CONFIG['server']['port']}",
    ip_addresses=[CLIENT_CONFIG["server"]["ip"]],
    is_persistent=True
)
server_peer.reconnect_wait = 5

print(f"[OK] Server peer added: {CLIENT_CONFIG['server']['ip']}:{CLIENT_CONFIG['server']['port']}", file=sys.stderr)

# Create relay application
print("[OK] Creating Credit Control application...", file=sys.stderr)
app = SimpleThreadingApplication(
    APP_DIAMETER_CREDIT_CONTROL_APPLICATION,
    is_auth_application=True
)
node.add_application(app, [server_peer])

print("[OK] Starting node...", file=sys.stderr)
print("=" * 60, file=sys.stderr)
print("Starting Diameter Client... (running for 15 seconds)", file=sys.stderr)
print("=" * 60, file=sys.stderr)

node.start()

try:
    print("[OK] Client started. Waiting 15 seconds for connection attempts...", file=sys.stderr)
    for i in range(15):
        time.sleep(1)
        print(f"[{i+1}/15] Connected...", file=sys.stderr)

except (KeyboardInterrupt, SystemExit) as e:
    print("[ERROR] Interrupted", file=sys.stderr)

finally:
    print("[OK] Shutting down client...", file=sys.stderr)
    node.stop()
    print("[OK] Client stopped.", file=sys.stderr)
    log_file.flush()
    log_file.close()
    print("[OK] Log file saved to: client_test_debug.log", file=sys.stderr)
