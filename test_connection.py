#!/usr/bin/env python
"""
Test script to verify client connection with better error handling
"""
import logging
import time
import sys

from diameter.message.constants import *
from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication

# Configure logging with more verbose output
logging.basicConfig(
    format="%(asctime)s %(name)-22s %(levelname)-7s %(message)s",
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('diameter_test.log')
    ]
)
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)

print("=" * 70)
print("Starting Diameter Client Connection Test")
print("=" * 70)

# Client Configuration
CLIENT_CONFIG = {
    "identity": {
        "origin_host": "client01.eseye.net",
        "origin_realm": "diameter.eseye.net",
        "product_name": "diamserver",
        "vendor_id": 0,
        "firmware_revision": 1,
        # "host_ip_address": "198.18.152.207"
        "host_ip_address": "192.168.1.10"
    },
    "server": {
        "host": "diameter01.eseye.com",
        "realm": "diameter.eseye.com",
        "ip": "172.30.15.203",
        "port": 3868
    }
}

try:
    print("\n[1/4] Creating client node...")
    # Create client node
    node = Node(
        origin_host=CLIENT_CONFIG["identity"]["origin_host"],
        realm_name=CLIENT_CONFIG["identity"]["origin_realm"],
        ip_addresses=[CLIENT_CONFIG["identity"]["host_ip_address"]],
        tcp_port=6091,
        vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2]
    )
    print("✓ Client node created successfully")

    print("\n[2/4] Adding server peer...")
    # Add server as peer
    server_peer = node.add_peer(
        f"aaa://{CLIENT_CONFIG['server']['host']}:{CLIENT_CONFIG['server']['port']}",
        realm_name=CLIENT_CONFIG['server']['realm'],
        ip_addresses=[CLIENT_CONFIG["server"]["ip"]],
        is_persistent=True
    )
    print("✓ Server peer added successfully")

    print("\n[3/4] Creating and adding application...")
    # Create application
    app = SimpleThreadingApplication(
        APP_DIAMETER_CREDIT_CONTROL_APPLICATION,
        is_auth_application=True
    )
    node.add_application(app, [server_peer])
    print("✓ Application created and added successfully")

    print("\n[4/4] Starting node...")
    # Start the node
    node.start()
    print("✓ Node started successfully")

    print("\n" + "=" * 70)
    print("Client is now running and attempting to connect to server...")
    print("=" * 70)
    print("\nWaiting for connection (60 seconds)...\nPress CTRL+C to stop")

    # Run for 60 seconds
    start_time = time.time()
    while time.time() - start_time < 60:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n\nReceived shutdown signal...")
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("\nShutting down client...")
    try:
        node.stop()
        print("✓ Client stopped gracefully")
    except Exception as e:
        print(f"Error during shutdown: {e}")
    print("\n" + "=" * 70)
    print("Test completed")
    print("=" * 70)
