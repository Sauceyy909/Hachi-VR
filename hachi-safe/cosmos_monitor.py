#!/usr/bin/env python3
"""
HTC Vive Cosmos Monitor and Debug Tool for Linux
This script monitors the Cosmos headset and provides debugging information
"""

import usb.core
import usb.util
import sys
import time
from datetime import datetime

# HTC Vive Cosmos USB Vendor/Product IDs
COSMOS_DEVICES = [
    {'vendor': 0x0bb4, 'product': 0x0313, 'name': 'HTC Vive Cosmos'},
    {'vendor': 0x0bb4, 'product': 0x0178, 'name': 'HTC Vive Cosmos Camera'},
    {'vendor': 0x0bb4, 'product': 0x030e, 'name': 'HTC Vive Cosmos Hub'},
    {'vendor': 0x28de, 'product': 0x2000, 'name': 'Valve Controller'},
    {'vendor': 0x28de, 'product': 0x2101, 'name': 'Valve Controller Dongle'},
]

class CosmosMonitor:
    def __init__(self):
        self.devices = []
        
    def scan_devices(self):
        """Scan for connected Vive Cosmos devices"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scanning for HTC Vive Cosmos devices...\n")
        self.devices = []
        
        for device_info in COSMOS_DEVICES:
            dev = usb.core.find(idVendor=device_info['vendor'], 
                               idProduct=device_info['product'])
            if dev is not None:
                self.devices.append((dev, device_info['name']))
                print(f"✓ Found: {device_info['name']}")
                print(f"  Vendor ID: 0x{device_info['vendor']:04x}")
                print(f"  Product ID: 0x{device_info['product']:04x}")
                print(f"  Bus: {dev.bus}, Address: {dev.address}")
                
                try:
                    if dev.is_kernel_driver_active(0):
                        print(f"  Status: Kernel driver active ✓")
                    else:
                        print(f"  Status: No kernel driver ✗")
                except:
                    print(f"  Status: Cannot determine driver status")
                
                print()
        
        if not self.devices:
            print("✗ No Vive Cosmos devices found!")
            print("\nTroubleshooting:")
            print("1. Ensure the headset is plugged in and powered on")
            print("2. Check if udev rules are installed: ls /etc/udev/rules.d/*vive*")
            print("3. Verify you're in the plugdev group: groups | grep plugdev")
            print("4. Try running with sudo: sudo ./cosmos_monitor.py")
            return False
        
        return True
    
    def get_device_config(self, dev):
        """Get detailed configuration information"""
        try:
            cfg = dev.get_active_configuration()
            print(f"\n  Configuration {cfg.bConfigurationValue}:")
            
            for intf in cfg:
                print(f"\n    Interface {intf.bInterfaceNumber}:")
                print(f"      Class: {intf.bInterfaceClass}")
                print(f"      Subclass: {intf.bInterfaceSubClass}")
                print(f"      Protocol: {intf.bInterfaceProtocol}")
                
                for ep in intf:
                    print(f"      Endpoint: 0x{ep.bEndpointAddress:02x}")
                    print(f"        Type: {ep.bmAttributes & 0x3}")
                    print(f"        Max Packet Size: {ep.wMaxPacketSize}")
        except Exception as e:
            print(f"  Could not read configuration: {e}")
    
    def monitor_realtime(self):
        """Monitor devices in real-time"""
        print("\n" + "="*60)
        print("REAL-TIME MONITORING (Press Ctrl+C to stop)")
        print("="*60)
        
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                print(f"Monitoring at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                for dev, name in self.devices:
                    try:
                        # Try to read basic status
                        print(f"{name}: ", end='')
                        if dev.is_kernel_driver_active(0):
                            print("ACTIVE ✓")
                        else:
                            print("INACTIVE ✗")
                    except Exception as e:
                        print(f"ERROR: {e}")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
    
    def detailed_info(self):
        """Print detailed information about all devices"""
        print("\n" + "="*60)
        print("DETAILED DEVICE INFORMATION")
        print("="*60)
        
        for dev, name in self.devices:
            print(f"\n{name}:")
            print("-" * 60)
            print(f"USB Version: {dev.bcdUSB}")
            print(f"Device Class: {dev.bDeviceClass}")
            print(f"Device Subclass: {dev.bDeviceSubClass}")
            print(f"Device Protocol: {dev.bDeviceProtocol}")
            print(f"Max Packet Size: {dev.bMaxPacketSize0}")
            
            try:
                print(f"Manufacturer: {usb.util.get_string(dev, dev.iManufacturer)}")
                print(f"Product: {usb.util.get_string(dev, dev.iProduct)}")
                print(f"Serial Number: {usb.util.get_string(dev, dev.iSerialNumber)}")
            except:
                print("Could not read string descriptors (may need elevated permissions)")
            
            self.get_device_config(dev)
    
    def test_communication(self):
        """Test basic communication with the device"""
        print("\n" + "="*60)
        print("TESTING DEVICE COMMUNICATION")
        print("="*60)
        
        for dev, name in self.devices:
            print(f"\nTesting {name}...")
            
            try:
                # Try to detach kernel driver
                if dev.is_kernel_driver_active(0):
                    print("  Attempting to detach kernel driver...")
                    try:
                        dev.detach_kernel_driver(0)
                        print("  ✓ Kernel driver detached")
                        reattach = True
                    except usb.core.USBError as e:
                        print(f"  ✗ Could not detach kernel driver: {e}")
                        reattach = False
                else:
                    reattach = False
                
                # Try to claim interface
                try:
                    usb.util.claim_interface(dev, 0)
                    print("  ✓ Interface claimed successfully")
                    
                    # Release interface
                    usb.util.release_interface(dev, 0)
                    print("  ✓ Interface released successfully")
                except usb.core.USBError as e:
                    print(f"  ✗ Could not claim interface: {e}")
                
                # Reattach kernel driver if we detached it
                if reattach:
                    try:
                        dev.attach_kernel_driver(0)
                        print("  ✓ Kernel driver reattached")
                    except:
                        print("  ⚠ Could not reattach kernel driver")
                        
            except Exception as e:
                print(f"  ✗ Communication test failed: {e}")

import os

def print_menu():
    print("\n" + "="*60)
    print("HTC VIVE COSMOS LINUX MONITOR")
    print("="*60)
    print("1. Scan for devices")
    print("2. Show detailed information")
    print("3. Test communication")
    print("4. Real-time monitoring")
    print("5. Check system configuration")
    print("6. Exit")
    print("="*60)

def check_system_config():
    """Check system configuration for VR readiness"""
    print("\n" + "="*60)
    print("SYSTEM CONFIGURATION CHECK")
    print("="*60)
    
    # Check udev rules
    print("\n1. Checking udev rules...")
    if os.path.exists("/etc/udev/rules.d/99-vive-cosmos.rules"):
        print("  ✓ Vive Cosmos udev rules found")
    else:
        print("  ✗ Vive Cosmos udev rules NOT found")
        print("    Run the setup script to install them")
    
    # Check group membership
    print("\n2. Checking group membership...")
    try:
        import grp
        groups = [g.gr_name for g in grp.getgrall() if os.getlogin() in g.gr_mem]
        if 'plugdev' in groups:
            print("  ✓ User is in plugdev group")
        else:
            print("  ✗ User is NOT in plugdev group")
            print("    Run: sudo usermod -a -G plugdev $USER")
    except:
        print("  ⚠ Could not check group membership")
    
    # Check for SteamVR
    print("\n3. Checking for SteamVR...")
    steamvr_path = os.path.expanduser("~/.steam/steam/steamapps/common/SteamVR")
    if os.path.exists(steamvr_path):
        print("  ✓ SteamVR installation found")
    else:
        print("  ✗ SteamVR NOT found")
        print("    Install it from Steam")
    
    # Check for Monado
    print("\n4. Checking for Monado...")
    monado_paths = ["/usr/local/bin/monado-service", "/usr/bin/monado-service"]
    found_monado = False
    for path in monado_paths:
        if os.path.exists(path):
            print(f"  ✓ Monado found at {path}")
            found_monado = True
            break
    if not found_monado:
        print("  ✗ Monado NOT found")
        print("    Run the setup script to build it")
    
    # Check OpenXR runtime
    print("\n5. Checking OpenXR runtime...")
    openxr_path = "/usr/share/openxr/1/openxr_monado.json"
    if os.path.exists(openxr_path):
        print("  ✓ Monado OpenXR runtime configured")
    else:
        print("  ⚠ Monado OpenXR runtime not found")
    
    print()

def main():
    monitor = CosmosMonitor()
    
    if os.geteuid() != 0:
        print("⚠ Warning: Not running as root. Some features may be limited.")
        print("  Consider running with: sudo python3 cosmos_monitor.py\n")
    
    while True:
        print_menu()
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            monitor.scan_devices()
        elif choice == '2':
            if monitor.devices or monitor.scan_devices():
                monitor.detailed_info()
            input("\nPress Enter to continue...")
        elif choice == '3':
            if monitor.devices or monitor.scan_devices():
                monitor.test_communication()
            input("\nPress Enter to continue...")
        elif choice == '4':
            if monitor.devices or monitor.scan_devices():
                monitor.monitor_realtime()
        elif choice == '5':
            check_system_config()
            input("\nPress Enter to continue...")
        elif choice == '6':
            print("\nExiting...")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
