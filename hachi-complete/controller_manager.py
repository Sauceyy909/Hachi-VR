#!/usr/bin/env python3
"""
HTC Vive Cosmos Controller Manager
Handles controller pairing, connectivity, and troubleshooting
"""

import subprocess
import re
import time
import sys
import os
from pathlib import Path

class ControllerManager:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "cosmos-controllers"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Cosmos controller Bluetooth addresses (will be detected)
        self.controllers = []
        
    def check_bluetooth(self):
        """Check if Bluetooth is available and running"""
        print("Checking Bluetooth status...")
        
        try:
            result = subprocess.run(['systemctl', 'is-active', 'bluetooth'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Bluetooth service is running")
                return True
            else:
                print("✗ Bluetooth service is not running")
                print("  Starting Bluetooth...")
                subprocess.run(['sudo', 'systemctl', 'start', 'bluetooth'], check=True)
                return True
        except Exception as e:
            print(f"✗ Bluetooth check failed: {e}")
            return False
    
    def enable_bluetooth_permissions(self):
        """Setup permissions for Bluetooth access"""
        print("\nConfiguring Bluetooth permissions...")
        
        # Add user to bluetooth group
        try:
            subprocess.run(['sudo', 'usermod', '-a', '-G', 'bluetooth', 
                          os.getlogin()], check=True)
            print("✓ User added to bluetooth group")
            print("  You may need to log out and back in")
        except Exception as e:
            print(f"⚠ Could not add to bluetooth group: {e}")
    
    def scan_for_controllers(self, duration=10):
        """Scan for Cosmos controllers"""
        print(f"\nScanning for controllers ({duration}s)...")
        print("Please turn on your controllers now")
        print("(Hold the system button until LED flashes)")
        
        try:
            # Start bluetoothctl scan
            scan_process = subprocess.Popen(
                ['bluetoothctl'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send scan command
            scan_process.stdin.write("power on\n")
            scan_process.stdin.write("scan on\n")
            scan_process.stdin.flush()
            
            found_devices = []
            start_time = time.time()
            
            while time.time() - start_time < duration:
                line = scan_process.stdout.readline()
                if line:
                    # Look for HTC or Vive devices
                    if 'NEW' in line or 'CHG' in line:
                        if 'HTC' in line or 'Vive' in line or 'Controller' in line:
                            print(f"  Found: {line.strip()}")
                            
                            # Extract MAC address
                            match = re.search(r'([0-9A-F]{2}:){5}[0-9A-F]{2}', line, re.I)
                            if match:
                                mac = match.group(0)
                                if mac not in found_devices:
                                    found_devices.append(mac)
            
            # Stop scan
            scan_process.stdin.write("scan off\n")
            scan_process.stdin.flush()
            scan_process.terminate()
            
            self.controllers = found_devices
            
            if found_devices:
                print(f"\n✓ Found {len(found_devices)} controller(s)")
                for i, mac in enumerate(found_devices, 1):
                    print(f"  Controller {i}: {mac}")
            else:
                print("\n✗ No controllers found")
                print("\nTroubleshooting:")
                print("  1. Make sure controllers are charged")
                print("  2. Hold system button until LED flashes")
                print("  3. Move controllers closer to PC")
                print("  4. Try removing and reinserting batteries")
            
            return found_devices
            
        except Exception as e:
            print(f"✗ Scan failed: {e}")
            return []
    
    def pair_controller(self, mac_address):
        """Pair a specific controller"""
        print(f"\nPairing controller: {mac_address}")
        
        commands = [
            "power on",
            f"pair {mac_address}",
            f"trust {mac_address}",
            f"connect {mac_address}"
        ]
        
        try:
            bt_process = subprocess.Popen(
                ['bluetoothctl'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            for cmd in commands:
                print(f"  Executing: {cmd}")
                bt_process.stdin.write(f"{cmd}\n")
                bt_process.stdin.flush()
                time.sleep(2)
            
            bt_process.stdin.write("exit\n")
            bt_process.stdin.flush()
            bt_process.wait(timeout=5)
            
            print("✓ Pairing commands sent")
            print("  If pairing failed, try:")
            print("  1. Remove controller (bluetoothctl remove <MAC>)")
            print("  2. Reset controller (hold system + trigger for 5s)")
            print("  3. Try pairing again")
            
        except Exception as e:
            print(f"✗ Pairing failed: {e}")
    
    def pair_all_controllers(self):
        """Pair all detected controllers"""
        if not self.controllers:
            print("No controllers detected. Run scan first.")
            return
        
        for mac in self.controllers:
            self.pair_controller(mac)
            time.sleep(3)
    
    def list_paired_devices(self):
        """List all paired Bluetooth devices"""
        print("\nListing paired devices...")
        
        try:
            result = subprocess.run(
                ['bluetoothctl', 'devices', 'Paired'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.stdout:
                print(result.stdout)
            else:
                print("No paired devices found")
                
        except Exception as e:
            print(f"✗ Could not list devices: {e}")
    
    def remove_device(self, mac_address):
        """Remove a paired device"""
        print(f"\nRemoving device: {mac_address}")
        
        try:
            subprocess.run(
                ['bluetoothctl', 'remove', mac_address],
                timeout=5
            )
            print("✓ Device removed")
        except Exception as e:
            print(f"✗ Remove failed: {e}")
    
    def optimize_bluetooth_settings(self):
        """Optimize Bluetooth for low-latency VR controllers"""
        print("\nOptimizing Bluetooth settings...")
        
        # Create Bluetooth config for better latency
        bt_config = """# Optimized for VR Controllers
[General]
MinConnectionInterval=6
MaxConnectionInterval=9
ConnectionLatency=0
SupervisionTimeout=300
AutoEnable=true
FastConnectable=true

[Policy]
AutoEnable=true
"""
        
        config_file = "/etc/bluetooth/main.conf.d/vr-controllers.conf"
        
        try:
            # Create directory if it doesn't exist
            subprocess.run(['sudo', 'mkdir', '-p', 
                          '/etc/bluetooth/main.conf.d/'], check=True)
            
            # Write config
            with open('/tmp/vr-controllers.conf', 'w') as f:
                f.write(bt_config)
            
            subprocess.run(['sudo', 'mv', '/tmp/vr-controllers.conf', 
                          config_file], check=True)
            
            # Restart Bluetooth
            print("  Restarting Bluetooth service...")
            subprocess.run(['sudo', 'systemctl', 'restart', 'bluetooth'], 
                         check=True)
            time.sleep(2)
            
            print("✓ Bluetooth optimized for VR controllers")
            
        except Exception as e:
            print(f"✗ Optimization failed: {e}")
    
    def test_controller_connectivity(self):
        """Test controller connectivity"""
        print("\n" + "="*60)
        print("CONTROLLER CONNECTIVITY TEST")
        print("="*60)
        
        if not self.controllers:
            print("\nNo controllers in list. Scanning...")
            self.scan_for_controllers(duration=5)
        
        if not self.controllers:
            print("No controllers to test")
            return
        
        print("\nTesting controller connections...")
        
        for i, mac in enumerate(self.controllers, 1):
            print(f"\nController {i} ({mac}):")
            
            try:
                result = subprocess.run(
                    ['bluetoothctl', 'info', mac],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                
                if 'Connected: yes' in result.stdout:
                    print("  ✓ Connected")
                elif 'Connected: no' in result.stdout:
                    print("  ✗ Not connected")
                    print("  Attempting to connect...")
                    subprocess.run(['bluetoothctl', 'connect', mac], timeout=5)
                else:
                    print("  ? Unknown status")
                
                # Check RSSI (signal strength)
                rssi_match = re.search(r'RSSI: (-?\d+)', result.stdout)
                if rssi_match:
                    rssi = int(rssi_match.group(1))
                    if rssi > -70:
                        print(f"  Signal: Good ({rssi} dBm)")
                    elif rssi > -85:
                        print(f"  Signal: Fair ({rssi} dBm)")
                    else:
                        print(f"  Signal: Weak ({rssi} dBm)")
                        print("    Move controller closer or remove obstacles")
                
            except Exception as e:
                print(f"  ✗ Test failed: {e}")
    
    def create_controller_udev_rules(self):
        """Create udev rules for controller access"""
        print("\nCreating controller udev rules...")
        
        udev_rules = """# HTC Vive Cosmos Controllers
KERNEL=="hidraw*", ATTRS{idVendor}=="28de", MODE="0666", GROUP="plugdev"
KERNEL=="hidraw*", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="28de", MODE="0666", GROUP="plugdev"
"""
        
        try:
            with open('/tmp/cosmos-controllers.rules', 'w') as f:
                f.write(udev_rules)
            
            subprocess.run(['sudo', 'mv', '/tmp/cosmos-controllers.rules',
                          '/etc/udev/rules.d/99-cosmos-controllers.rules'], 
                         check=True)
            
            subprocess.run(['sudo', 'udevadm', 'control', '--reload-rules'], 
                         check=True)
            subprocess.run(['sudo', 'udevadm', 'trigger'], check=True)
            
            print("✓ Controller udev rules created")
            
        except Exception as e:
            print(f"✗ Failed to create udev rules: {e}")

def print_menu():
    print("\n" + "="*60)
    print("COSMOS CONTROLLER MANAGER")
    print("="*60)
    print("1. Quick Setup (Scan & Pair)")
    print("2. Scan for Controllers")
    print("3. Pair All Detected Controllers")
    print("4. List Paired Devices")
    print("5. Test Controller Connectivity")
    print("6. Optimize Bluetooth Settings")
    print("7. Remove a Device")
    print("8. Troubleshooting Guide")
    print("9. Exit")
    print("="*60)

def show_troubleshooting():
    print("\n" + "="*60)
    print("CONTROLLER TROUBLESHOOTING GUIDE")
    print("="*60)
    
    print("""
PROBLEM: Controllers won't pair
SOLUTIONS:
  1. Charge controllers fully
  2. Reset controller: Hold system button + trigger for 5 seconds
  3. Remove old pairing: bluetoothctl remove <MAC>
  4. Make sure Bluetooth is on: systemctl status bluetooth
  5. Check for interference from WiFi routers

PROBLEM: Controllers disconnect frequently
SOLUTIONS:
  1. Move closer to PC (within 3 meters)
  2. Remove USB 3.0 devices that might cause interference
  3. Update Bluetooth firmware
  4. Use a Bluetooth dongle instead of built-in Bluetooth
  5. Run: sudo systemctl restart bluetooth

PROBLEM: High latency/lag
SOLUTIONS:
  1. Optimize Bluetooth settings (use option 6 in menu)
  2. Use 5GHz WiFi instead of 2.4GHz to reduce interference
  3. Close bandwidth-heavy applications
  4. Ensure controllers are charged (low battery causes lag)

PROBLEM: One controller works, other doesn't
SOLUTIONS:
  1. Pair controllers one at a time
  2. Reset the non-working controller
  3. Check if both controllers show in bluetoothctl devices
  4. Verify both have fresh batteries

PROBLEM: Buttons not responding in VR
SOLUTIONS:
  1. Check SteamVR controller bindings
  2. Verify controllers show as "connected" in SteamVR
  3. Restart SteamVR
  4. Check /var/log/syslog for input errors

ADVANCED: Using a USB Bluetooth Dongle
  - Often works better than built-in Bluetooth
  - Look for dongles with "Class 1" Bluetooth (better range)
  - Recommended: ASUS BT500 or similar
  - Disable internal Bluetooth in BIOS if using external dongle
""")
    
    input("\nPress Enter to continue...")

def main():
    manager = ControllerManager()
    
    while True:
        print_menu()
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            print("\n=== QUICK SETUP ===")
            manager.check_bluetooth()
            manager.enable_bluetooth_permissions()
            manager.optimize_bluetooth_settings()
            manager.create_controller_udev_rules()
            manager.scan_for_controllers(duration=15)
            if manager.controllers:
                manager.pair_all_controllers()
                manager.test_controller_connectivity()
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            manager.scan_for_controllers(duration=10)
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            manager.pair_all_controllers()
            input("\nPress Enter to continue...")
            
        elif choice == '4':
            manager.list_paired_devices()
            input("\nPress Enter to continue...")
            
        elif choice == '5':
            manager.test_controller_connectivity()
            input("\nPress Enter to continue...")
            
        elif choice == '6':
            manager.optimize_bluetooth_settings()
            manager.create_controller_udev_rules()
            input("\nPress Enter to continue...")
            
        elif choice == '7':
            manager.list_paired_devices()
            mac = input("\nEnter MAC address to remove: ").strip()
            if mac:
                manager.remove_device(mac)
            input("\nPress Enter to continue...")
            
        elif choice == '8':
            show_troubleshooting()
            
        elif choice == '9':
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
