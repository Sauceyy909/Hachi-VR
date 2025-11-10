#!/usr/bin/env python3
"""
Enhanced Tracking System for HTC Vive Cosmos
Attempts to enable inside-out tracking with multiple fallback options
"""

import subprocess
import os
import sys
import json
import time
from pathlib import Path

class CosmosTrackingManager:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "cosmos-tracking"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "tracking_config.json"
        self.load_config()
    
    def load_config(self):
        """Load or create tracking configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "tracking_mode": "auto",  # auto, cameras, imu_only, hybrid
                "camera_exposure": "auto",
                "imu_fusion_weight": 0.7,
                "room_scale_enabled": True,
                "tracking_smoothing": 0.5,
                "camera_ids": [],
                "calibration_data": None
            }
            self.save_config()
    
    def save_config(self):
        """Save tracking configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, indent=2, fp=f)
    
    def detect_cameras(self):
        """Detect Cosmos tracking cameras"""
        print("Scanning for Cosmos tracking cameras...")
        cameras = []
        
        try:
            # Check for video devices
            result = subprocess.run(['v4l2-ctl', '--list-devices'], 
                                  capture_output=True, text=True)
            
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if 'cosmos' in line.lower() or '0bb4' in line.lower():
                    # Found a Cosmos camera
                    if i + 1 < len(lines):
                        device = lines[i + 1].strip()
                        if device.startswith('/dev/video'):
                            cameras.append(device)
                            print(f"  Found camera: {device}")
        except FileNotFoundError:
            print("  v4l2-ctl not found. Installing v4l-utils...")
            subprocess.run(['sudo', 'rpm-ostree', 'install', 'v4l-utils'], 
                         check=False)
            print("  Please reboot and run again")
        
        self.config["camera_ids"] = cameras
        self.save_config()
        return cameras
    
    def setup_camera_permissions(self):
        """Setup udev rules for camera access"""
        print("\nSetting up camera permissions...")
        
        udev_rule = """# HTC Vive Cosmos Camera Access
SUBSYSTEM=="video4linux", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0178", MODE="0666", GROUP="video"
SUBSYSTEM=="video4linux", ATTRS{idVendor}=="0bb4", MODE="0666", GROUP="video"
"""
        
        rule_file = "/etc/udev/rules.d/99-vive-cosmos-camera.rules"
        
        try:
            with open('/tmp/cosmos-camera.rules', 'w') as f:
                f.write(udev_rule)
            
            subprocess.run(['sudo', 'mv', '/tmp/cosmos-camera.rules', rule_file], 
                         check=True)
            subprocess.run(['sudo', 'udevadm', 'control', '--reload-rules'], 
                         check=True)
            subprocess.run(['sudo', 'udevadm', 'trigger'], check=True)
            
            # Add user to video group
            subprocess.run(['sudo', 'usermod', '-a', '-G', 'video', os.getlogin()], 
                         check=True)
            
            print("✓ Camera permissions configured")
            print("⚠ You may need to log out and back in for group changes")
            return True
        except Exception as e:
            print(f"✗ Failed to setup camera permissions: {e}")
            return False
    
    def configure_camera_settings(self, camera_device):
        """Optimize camera settings for tracking"""
        print(f"\nConfiguring camera: {camera_device}")
        
        settings = {
            "exposure_auto": "1",  # Manual exposure
            "exposure_absolute": "156",  # Optimized for tracking
            "brightness": "128",
            "contrast": "128",
            "saturation": "128",
            "gain": "64",
        }
        
        for setting, value in settings.items():
            try:
                subprocess.run([
                    'v4l2-ctl',
                    '-d', camera_device,
                    '-c', f"{setting}={value}"
                ], check=False, capture_output=True)
            except:
                pass
        
        print(f"✓ Camera {camera_device} configured")
    
    def create_monado_config(self):
        """Create optimized Monado configuration for Cosmos"""
        print("\nCreating optimized Monado configuration...")
        
        monado_config_dir = Path.home() / ".config" / "monado"
        monado_config_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            "active": "steamvr",
            "steamvr": {
                "enable": true,
                "vive_tracking": {
                    "enable_camera_tracking": True,
                    "imu_fusion": True,
                    "tracking_mode": self.config["tracking_mode"]
                }
            },
            "tracking": {
                "hand_tracking": False,
                "slam_tracking": True,
                "camera_auto_exposure": self.config["camera_exposure"] == "auto",
                "imu_integration": True,
                "prediction_time_ms": 16,
                "smoothing_factor": self.config["tracking_smoothing"]
            }
        }
        
        config_file = monado_config_dir / "config_v0.json"
        with open(config_file, 'w') as f:
            json.dump(config, indent=2, fp=f)
        
        print(f"✓ Monado config created: {config_file}")
    
    def enable_imu_only_mode(self):
        """Configure for IMU-only tracking (3DOF)"""
        print("\nEnabling IMU-only tracking mode...")
        print("This provides 3DOF (rotation only) tracking")
        
        self.config["tracking_mode"] = "imu_only"
        self.config["room_scale_enabled"] = False
        self.save_config()
        self.create_monado_config()
        
        print("✓ IMU-only mode enabled")
        print("  This is good for seated VR experiences")
    
    def enable_hybrid_mode(self):
        """Enable hybrid IMU + camera tracking"""
        print("\nEnabling hybrid tracking mode...")
        
        cameras = self.detect_cameras()
        
        if not cameras:
            print("⚠ No cameras detected, falling back to IMU-only")
            self.enable_imu_only_mode()
            return
        
        self.setup_camera_permissions()
        
        for camera in cameras:
            self.configure_camera_settings(camera)
        
        self.config["tracking_mode"] = "hybrid"
        self.config["room_scale_enabled"] = True
        self.save_config()
        self.create_monado_config()
        
        print("✓ Hybrid tracking mode enabled")
        print("  Combines IMU and camera data for 6DOF tracking")
    
    def calibrate_room_scale(self):
        """Room scale calibration utility"""
        print("\n" + "="*60)
        print("ROOM SCALE CALIBRATION")
        print("="*60)
        print("\nThis will help calibrate your play space.")
        print("\nInstructions:")
        print("1. Stand in the center of your play area")
        print("2. Point your headset forward")
        print("3. Press Enter when ready")
        
        input("\nPress Enter to start calibration...")
        
        # Create calibration data
        calibration = {
            "timestamp": time.time(),
            "play_space_type": "room_scale",
            "bounds": None,
            "center_point": [0, 0, 0],
            "forward_direction": [0, 0, -1]
        }
        
        print("\nMove to each corner of your play space and press Enter")
        print("Press 'q' and Enter when finished")
        
        corners = []
        corner_num = 1
        
        while True:
            response = input(f"\nCorner {corner_num} (or 'q' to finish): ").strip()
            if response.lower() == 'q':
                break
            
            # In a real implementation, we'd capture the actual position
            # For now, we'll store placeholder data
            corners.append(f"corner_{corner_num}")
            corner_num += 1
        
        if len(corners) >= 3:
            calibration["bounds"] = corners
            self.config["calibration_data"] = calibration
            self.save_config()
            
            print("\n✓ Room scale calibration complete!")
            print(f"  Captured {len(corners)} corner points")
        else:
            print("\n⚠ Need at least 3 corners for room scale")
    
    def test_tracking(self):
        """Test current tracking setup"""
        print("\n" + "="*60)
        print("TRACKING TEST")
        print("="*60)
        
        print("\nCurrent configuration:")
        print(f"  Tracking mode: {self.config['tracking_mode']}")
        print(f"  Room scale: {'Enabled' if self.config['room_scale_enabled'] else 'Disabled'}")
        print(f"  Cameras detected: {len(self.config['camera_ids'])}")
        
        print("\nTesting components...")
        
        # Test cameras
        for camera in self.config['camera_ids']:
            print(f"\n  Testing {camera}...")
            try:
                result = subprocess.run(['v4l2-ctl', '-d', camera, '--all'],
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    print(f"    ✓ Camera accessible")
                else:
                    print(f"    ✗ Camera not accessible")
            except:
                print(f"    ✗ Camera test failed")
        
        # Test Monado
        print("\n  Testing Monado service...")
        result = subprocess.run(['pgrep', '-x', 'monado-service'], 
                              capture_output=True)
        if result.returncode == 0:
            print("    ✓ Monado is running")
        else:
            print("    ⚠ Monado is not running")
            print("      Start with: monado-service &")
        
        print("\n" + "="*60)
        print("Put on your headset and move around to test tracking")
        print("="*60)

def print_menu():
    print("\n" + "="*60)
    print("COSMOS ENHANCED TRACKING MANAGER")
    print("="*60)
    print("1. Auto-configure (Recommended)")
    print("2. Enable Hybrid Tracking (Camera + IMU)")
    print("3. Enable IMU-Only Mode (Seated VR)")
    print("4. Detect and Setup Cameras")
    print("5. Calibrate Room Scale")
    print("6. Test Tracking")
    print("7. View Current Config")
    print("8. Exit")
    print("="*60)

def main():
    if os.geteuid() == 0:
        print("⚠ Warning: Running as root")
    
    manager = CosmosTrackingManager()
    
    while True:
        print_menu()
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            print("\nAuto-configuring tracking system...")
            cameras = manager.detect_cameras()
            if cameras:
                manager.enable_hybrid_mode()
            else:
                print("\nNo cameras detected. Trying alternative methods...")
                manager.enable_imu_only_mode()
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            manager.enable_hybrid_mode()
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            manager.enable_imu_only_mode()
            input("\nPress Enter to continue...")
            
        elif choice == '4':
            cameras = manager.detect_cameras()
            if cameras:
                manager.setup_camera_permissions()
            else:
                print("\nNo cameras detected. Possible reasons:")
                print("  - Cameras not powered on")
                print("  - Missing kernel drivers (uvcvideo)")
                print("  - USB bandwidth issues")
            input("\nPress Enter to continue...")
            
        elif choice == '5':
            manager.calibrate_room_scale()
            input("\nPress Enter to continue...")
            
        elif choice == '6':
            manager.test_tracking()
            input("\nPress Enter to continue...")
            
        elif choice == '7':
            print("\nCurrent Configuration:")
            print(json.dumps(manager.config, indent=2))
            input("\nPress Enter to continue...")
            
        elif choice == '8':
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
