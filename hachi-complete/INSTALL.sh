#!/bin/bash

# Quick Installation Guide for HTC Vive Cosmos on Bazzite Linux

cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     HTC Vive Cosmos for Bazzite Linux - Installation Guide    ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

IMPORTANT DISCLAIMER:
The HTC Vive Cosmos has LIMITED official Linux support. This is 
experimental software that may not provide full functionality,
especially for inside-out tracking features.

═══════════════════════════════════════════════════════════════

INSTALLATION STEPS:

1. SYSTEM SETUP (requires reboot)
   
   chmod +x vive_cosmos_setup.sh
   ./vive_cosmos_setup.sh
   
   ⚠️  REBOOT REQUIRED AFTER THIS STEP

2. BUILD THE DRIVER
   
   make
   sudo make install

3. VERIFY INSTALLATION
   
   make check
   sudo python3 cosmos_monitor.py

4. LAUNCH VR
   
   # Easy way - interactive menu:
   chmod +x vr_manager.sh
   ./vr_manager.sh
   
   # Or manually:
   ./launch_cosmos_vr.sh

═══════════════════════════════════════════════════════════════

INCLUDED FILES:

📄 README.md                  - Complete documentation
📄 vive_cosmos_setup.sh       - System setup script (run first!)
📄 cosmos_bridge.cpp          - C++ driver bridge
📄 cosmos_monitor.py          - Python monitoring tool
📄 vr_manager.sh              - Interactive VR session manager
📄 Makefile                   - Build system
📄 monado-cosmos.service      - Systemd service file
📄 launch_cosmos_vr.sh        - Quick VR launcher

═══════════════════════════════════════════════════════════════

TROUBLESHOOTING:

Problem: Device not detected
Solution: 
  - Check USB connection
  - Verify udev rules: ls /etc/udev/rules.d/*vive*
  - Reload rules: sudo udevadm control --reload-rules && sudo udevadm trigger
  - Check group: groups | grep plugdev

Problem: Permission denied
Solution:
  - Add user to group: sudo usermod -a -G plugdev $USER
  - REBOOT after adding to group
  - Or run with sudo (temporary)

Problem: Tracking doesn't work
Solution:
  - Inside-out tracking is NOT fully supported on Linux
  - Update firmware on Windows first
  - Use seated mode instead of room-scale
  - Consider using Monado instead of SteamVR

Problem: No display in headset
Solution:
  - Check HDMI/DisplayPort cable
  - Verify GPU supports required resolution
  - Try different video port
  - Check GPU drivers are up to date

═══════════════════════════════════════════════════════════════

QUICK REFERENCE:

Check device:
  lsusb | grep 0bb4

Monitor device:
  sudo python3 cosmos_monitor.py

Test driver:
  sudo ./cosmos_bridge --info

Start VR (full):
  ./vr_manager.sh

Start VR (quick):
  ./launch_cosmos_vr.sh

View logs:
  ls -la ~/.local/share/vr-logs/

═══════════════════════════════════════════════════════════════

ALTERNATIVES IF COSMOS DOESN'T WORK:

1. Use Windows in a VM with USB passthrough
2. Dual boot with Windows for VR
3. Consider a different headset (Valve Index, Vive Pro)
4. Wait for better Linux VR driver development

═══════════════════════════════════════════════════════════════

RESOURCES:

🌐 Monado Project: https://gitlab.freedesktop.org/monado/monado
🌐 SteamVR Linux: https://github.com/ValveSoftware/SteamVR-for-Linux
🌐 Bazzite: https://bazzite.gg
🌐 Reddit r/linux_gaming: For community support

═══════════════════════════════════════════════════════════════

For detailed information, see README.md

Good luck with your VR adventures on Linux! 🚀

═══════════════════════════════════════════════════════════════
EOF

echo ""
read -p "Press Enter to start installation, or Ctrl+C to exit..."

echo ""
echo "Starting installation..."
echo ""

# Check if we're on Bazzite
if [ -f /etc/os-release ]; then
    source /etc/os-release
    if [[ ! "$NAME" =~ "Bazzite" ]]; then
        echo "⚠️  Warning: This script is designed for Bazzite Linux"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x vive_cosmos_setup.sh 2>/dev/null || true
chmod +x launch_cosmos_vr.sh 2>/dev/null || true
chmod +x vr_manager.sh 2>/dev/null || true
chmod +x cosmos_monitor.py 2>/dev/null || true

echo ""
echo "✓ Scripts are now executable"
echo ""
echo "Next steps:"
echo "1. Run: ./vive_cosmos_setup.sh"
echo "2. REBOOT your system"
echo "3. Run: make && sudo make install"
echo "4. Run: ./vr_manager.sh"
echo ""
echo "For help, see README.md"
