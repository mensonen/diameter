#!/usr/bin/env python
"""
Diameter Client Connectivity Diagnostic Tool

This script performs comprehensive checks to diagnose connection issues
with the Diameter server via NLB.
"""

import socket
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("DIAGNOSTIC")

class DiameterDiagnostics:
    def __init__(self):
        self.fqdn = "k8s-diameter-diameter-4fb9aa25ea-aa09fb21c62940ee.elb.eu-west-1.amazonaws.com"
        self.port = 3868
        self.results = []

    def print_header(self, title):
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")

    def check_mark(self, passed, message):
        symbol = "✓" if passed else "✗"
        status = "PASS" if passed else "FAIL"
        print(f"  {symbol} [{status}] {message}")
        self.results.append((status, message))

    def test_fqdn_resolution(self):
        """Test DNS resolution of the NLB FQDN"""
        self.print_header("Step 1: FQDN Resolution")

        print(f"Target FQDN: {self.fqdn}")
        print(f"Target Port: {self.port}\n")

        try:
            result = socket.getaddrinfo(self.fqdn, self.port, socket.AF_INET, socket.SOCK_STREAM)

            if result:
                ip_address = result[0][4][0]
                self.check_mark(True, f"DNS resolved successfully: {self.fqdn} → {ip_address}")
                return ip_address
            else:
                self.check_mark(False, "DNS resolution returned empty result")
                return None

        except socket.gaierror as e:
            self.check_mark(False, f"DNS resolution failed: {e}")
            logger.error(f"  Error details: {e}")
            return None
        except Exception as e:
            self.check_mark(False, f"Unexpected error during DNS resolution: {e}")
            return None

    def test_tcp_connectivity(self, ip_address):
        """Test TCP connectivity to the server"""
        self.print_header("Step 2: TCP Connectivity")

        print(f"Target IP: {ip_address}")
        print(f"Target Port: {self.port}\n")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # 10-second timeout

            logger.info(f"Attempting connection to {ip_address}:{self.port}...")
            sock.connect((ip_address, self.port))

            self.check_mark(True, f"TCP connection successful to {ip_address}:{self.port}")

            # Try to receive data (Diameter greeting)
            sock.settimeout(2)
            try:
                data = sock.recv(1024)
                if data:
                    self.check_mark(True, f"Received {len(data)} bytes from server")
                    return True
                else:
                    self.check_mark(True, "Connected but no data received (server may be waiting)")
                    return True
            except socket.timeout:
                self.check_mark(True, "Connected but no immediate response (normal for Diameter)")
                return True
            finally:
                sock.close()

        except socket.timeout:
            self.check_mark(False, f"Connection timeout (10s) to {ip_address}:{self.port}")
            logger.error("  The server may be down, unreachable, or blocking the connection")
            return False
        except ConnectionRefusedError:
            self.check_mark(False, f"Connection refused by {ip_address}:{self.port}")
            logger.error("  The server rejected the connection. Possible causes:")
            logger.error("    - Server is not running")
            logger.error("    - Server is not listening on port 3868")
            logger.error("    - IP address is incorrect")
            return False
        except OSError as e:
            self.check_mark(False, f"Connection error: {e}")
            logger.error(f"  OS Error details: {e}")
            return False
        except Exception as e:
            self.check_mark(False, f"Unexpected error: {e}")
            return False

    def test_local_network(self):
        """Test local network configuration"""
        self.print_header("Step 3: Local Network Configuration")

        try:
            # Get hostname
            hostname = socket.gethostname()
            self.check_mark(True, f"Local hostname: {hostname}")

            # Get all local IPs
            local_ips = []
            try:
                # Try to get hostname and resolve it
                ips = socket.gethostbyname_ex(hostname)[2]
                local_ips = ips
                self.check_mark(True, f"Local IPs configured: {', '.join(local_ips)}")
            except:
                # Fallback: use socket connection to determine local IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    s.connect((self.fqdn, self.port))
                    local_ip = s.getsockname()[0]
                    self.check_mark(True, f"Default outbound IP: {local_ip}")
                except:
                    self.check_mark(False, "Could not determine local IP configuration")
                finally:
                    s.close()

            return True
        except Exception as e:
            self.check_mark(False, f"Error checking local network: {e}")
            return False

    def test_firewall(self):
        """Test if firewall might be blocking"""
        self.print_header("Step 4: Firewall & Port Accessibility")

        # Test common ports to see if any work
        test_ports = [80, 443, 3868, 6666, 5060]

        print("Testing common ports for outbound connectivity:\n")

        accessible_ports = []
        for test_port in test_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex(("8.8.8.8", test_port))
                sock.close()

                if result == 0:
                    print(f"  ✓ Port {test_port}: OPEN")
                    accessible_ports.append(test_port)
                else:
                    print(f"  ✗ Port {test_port}: BLOCKED/FILTERED")
            except Exception as e:
                print(f"  ? Port {test_port}: ERROR - {e}")

        if 3868 in accessible_ports:
            self.check_mark(True, "Port 3868 is accessible")
            return True
        else:
            self.check_mark(False, "Port 3868 appears to be blocked by firewall")
            logger.error("  You may need to configure firewall rules to allow port 3868")
            return False

    def check_python_version(self):
        """Check Python version compatibility"""
        self.print_header("Step 5: Python & Dependencies")

        version = sys.version_info
        print(f"Python Version: {version.major}.{version.minor}.{version.micro}\n")

        self.check_mark(version >= (3, 6), f"Python {version.major}.{version.minor}.{version.micro} (requires 3.6+)")

        # Check diameter library
        try:
            import diameter
            self.check_mark(True, "diameter package is installed")

            try:
                version = diameter.__version__
                print(f"    Version: {version}")
            except:
                pass

            return True
        except ImportError:
            self.check_mark(False, "diameter package not found (install with: pip install python-diameter)")
            return False

    def generate_report(self):
        """Generate diagnostic report"""
        self.print_header("Diagnostic Report Summary")

        passed = sum(1 for status, _ in self.results if status == "PASS")
        failed = sum(1 for status, _ in self.results if status == "FAIL")
        total = len(self.results)

        print(f"Results: {passed}/{total} tests passed, {failed} failed\n")

        if failed > 0:
            print("Failed Tests:")
            for status, message in self.results:
                if status == "FAIL":
                    print(f"  • {message}")

        print(f"\n{'='*70}\n")

        if failed == 0:
            print("✓ All diagnostics passed! Your network configuration appears correct.")
            print("  The client should be able to connect to the Diameter server.")
        else:
            print("✗ Some diagnostic tests failed.")
            print("  Please review the errors above and fix the issues.")
            print("\nCommon solutions:")
            print("  1. DNS: Check that the FQDN can be resolved (DNS settings)")
            print("  2. Connectivity: Check that port 3868 is accessible (firewall rules)")
            print("  3. Server: Verify the server is running and accepting connections")
            print("  4. Dependencies: Ensure python-diameter is installed")

def main():
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "Diameter Client Diagnostics Tool" + " "*21 + "║")
    print("╚" + "="*68 + "╝")

    diag = DiameterDiagnostics()

    # Run all tests
    ip_address = diag.test_fqdn_resolution()

    if ip_address:
        diag.test_tcp_connectivity(ip_address)
    else:
        print("\n⚠ Cannot continue without successful DNS resolution\n")

    diag.test_local_network()
    diag.test_firewall()
    diag.check_python_version()

    # Generate report
    diag.generate_report()

if __name__ == "__main__":
    main()
