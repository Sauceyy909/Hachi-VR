# 🎮 HACHI - Arch/Garuda Linux Edition

## HTC Vive Cosmos VR Driver for Arch Linux

**å…« (Hachi) = Vive in Japanese**

This is the **SAFE** version specifically adapted for Arch Linux and Garuda Linux systems.

---

## ✅ What's Different for Arch/Garuda

### Package Manager
- Uses `pacman` instead of `apt-get` or `dnf`
- Compatible with Arch-based distributions (Arch, Garuda, Manjaro, EndeavourOS, etc.)

### System Integration
- Works with Arch package naming conventions
- Compatible with systemd on Arch
- No rpm-ostree or flatpak dependencies

### Safe Installation
- ✅ Only installs user-space tools
- ✅ NO modifications to GPU drivers
- ✅ NO system package changes (except `tk` for GUI)
- ✅ NO kernel modifications

---

## 📥 Quick Installation

### Step 1: Download & Extract
```bash
unzip hachi-arch.zip
cd hachi-arch
```

### Step 2: Run Installer
```bash
chmod +x hachi_safe_installer_arch.sh
./hachi_safe_installer_arch.sh
```

### Step 3: Log Out & Back In
```bash
# Just log out (NOT reboot)
# This applies group permissions
```

### Step 4: Launch HACHI
```bash
hachi
```

That's it! 🎉

---

## 🔧 Prerequisites

### Required (Auto-installed)
- Python 3.8+ (usually pre-installed)
- tk (for GUI - installer handles this)

### Recommended
- SteamVR (from Steam)
- Monado OpenXR runtime (optional, for better tracking)

---

## 📦 What Gets Installed

**User Space Only:**
- `~/.local/bin/hachi` - Launcher command
- `~/.local/bin/hachi_control_center.py` - Main GUI
- `~/.local/share/hachi/` - Configuration and tools
- Desktop shortcut

**System (Minimal):**
- `/etc/udev/rules.d/99-hachi-vr.rules` - VR device permissions
- User added to `plugdev` and `video` groups

**NOT Touched:**
- ❌ GPU drivers (NVIDIA/AMD/Intel)
- ❌ Kernel modules
- ❌ System packages
- ❌ Display configuration

---

## 🎯 Usage

### Launch HACHI
```bash
hachi
```

Or find "HACHI Control Center" in your application menu.

### Enable Finger Tracking
1. Launch HACHI
2. Click "✋ Finger Tracking" tab
3. Click "Enable Finger Tracking"
4. Click "Calibrate Hands"
5. Done!

### Launch VR
1. Plug in Cosmos headset
2. In HACHI dashboard, click "🚀 Launch VR"
3. Put on headset and enjoy!

---

## 🛠️ Troubleshooting

### HACHI Won't Open

**Install tkinter:**
```bash
sudo pacman -S tk
hachi
```

### Headset Not Detected

**Check USB connection:**
```bash
lsusb | grep 0bb4
```

Should show: `ID 0bb4:0313 HTC Corp. Vive Cosmos`

**Check permissions:**
```bash
# Verify rules exist
ls /etc/udev/rules.d/*hachi*

# Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Check groups
groups | grep plugdev

# If not in group, log out and back in
```

### Python Package Errors

**Install manually:**
```bash
pip install --user pyusb opencv-python numpy
```

Or with break-system-packages flag:
```bash
pip install --user --break-system-packages pyusb opencv-python numpy
```

### SteamVR Issues

**Install SteamVR:**
1. Open Steam
2. Library > Tools
3. Search "SteamVR"
4. Install

**Configure for Linux:**
```bash
# Set OpenXR runtime
export XR_RUNTIME_JSON=/usr/share/openxr/1/openxr_monado.json
```

---

## 🔍 Diagnostic Commands

### Check Everything
```bash
# GPU drivers
nvidia-smi  # For NVIDIA
glxinfo | grep "OpenGL renderer"  # For all GPUs

# Python
python3 --version
python3 -c "import tkinter"

# Headset
lsusb | grep 0bb4

# HACHI
which hachi
ls ~/.local/bin/hachi*

# Groups
groups | grep -E 'plugdev|video'
```

### Full Diagnostic
```bash
echo "=== HACHI Diagnostic (Arch) ==="
echo "Python: $(python3 --version)"
python3 -c "import tkinter" && echo "✓ tkinter OK" || echo "✗ tkinter missing"
python3 -c "import cv2" && echo "✓ opencv OK" || echo "✗ opencv missing"
lsusb | grep 0bb4 && echo "✓ Headset connected" || echo "✗ Headset not found"
ls ~/.local/bin/hachi* > /dev/null 2>&1 && echo "✓ HACHI installed" || echo "✗ HACHI not installed"
groups | grep plugdev > /dev/null && echo "✓ In plugdev group" || echo "✗ Not in plugdev group"
```

---

## 🎮 Arch-Specific Notes

### AUR Packages (Optional)

If you prefer using AUR:
```bash
# For additional VR tools
yay -S monado-git
yay -S libsurvive-git
```

### Garuda Gaming Edition

Garuda Gaming comes with Steam pre-configured:
- SteamVR should work out of the box
- GPU drivers already optimized
- Gaming optimizations pre-applied

### Manjaro Users

Manjaro may need:
```bash
sudo pacman -Syu  # Update system first
sudo pacman -S base-devel  # For building tools
```

---

## 📋 Files Included

```
hachi-arch/
├── hachi_safe_installer_arch.sh  ← Run this!
├── hachi_control_center.py       ← Main GUI
├── enhanced_tracking_arch.py     ← Tracking tools
├── controller_manager.py         ← Controller setup
├── cosmos_monitor.py            ← Device diagnostics
├── display_optimizer.sh         ← Performance tweaks
├── firmware_manager.sh          ← Firmware tools
├── vr_manager.sh                ← VR session manager
├── launch_cosmos_vr.sh          ← Quick VR launcher
├── INSTALL_HACHI_arch.py        ← GUI installer
└── Documentation files
```

---

## ⚠️ Important for Arch Users

### Rolling Release Considerations
- Keep system updated: `sudo pacman -Syu`
- Python packages may need occasional updates: `pip install --user --upgrade pyusb opencv-python numpy`
- If system updates break HACHI, just reinstall (it's safe!)

### Package Conflicts
- HACHI doesn't install system packages
- No conflicts with official repos
- Safe to use with custom kernels

### Graphics Drivers
- **NVIDIA:** Use `nvidia` or `nvidia-dkms` from official repos
- **AMD:** Use `mesa` (usually pre-installed)
- **Intel:** Use `mesa` and `vulkan-intel`
- HACHI will never touch these!

---

## 🆘 Emergency Recovery

### If Something Breaks

**Remove HACHI completely:**
```bash
rm -rf ~/.local/share/hachi
rm -rf ~/.local/bin/hachi*
rm ~/.local/share/applications/hachi.desktop
sudo rm /etc/udev/rules.d/99-hachi-vr.rules
sudo udevadm control --reload-rules
```

**Reinstall:**
```bash
./hachi_safe_installer_arch.sh
```

Your system will be fine - HACHI only touches user space!

---

## 🚀 Advanced Usage

### Custom Monado Build

For better tracking, build Monado from source:
```bash
# Install dependencies
sudo pacman -S cmake ninja meson glslang vulkan-headers vulkan-icd-loader sdl2

# Clone and build
git clone https://gitlab.freedesktop.org/monado/monado.git
cd monado
meson build
ninja -C build
sudo ninja -C build install
```

### Performance Tuning

Run display optimizer:
```bash
~/.local/bin/display_optimizer.sh
```

### Enable Finger Tracking

See `HACHI-FINGER-TRACKING.md` for complete guide.

---

## 📞 Support

**Installation Issues:**
- Check log: `~/.local/share/hachi/install.log`
- Verify Python: `python3 --version`
- Verify tkinter: `python3 -c "import tkinter"`

**Headset Not Working:**
- Verify USB connection: `lsusb | grep 0bb4`
- Check permissions: `groups`
- Try different USB port

**General Questions:**
- See main documentation files
- Check Arch Wiki for VR: https://wiki.archlinux.org/title/Virtual_reality

---

## 🎯 Quick Reference

### Essential Commands
```bash
# Launch HACHI
hachi

# Check headset
lsusb | grep 0bb4

# Test tracking
python3 ~/.local/bin/enhanced_tracking_arch.py

# Monitor devices
python3 ~/.local/bin/cosmos_monitor.py

# Launch VR directly
~/.local/bin/launch_cosmos_vr.sh
```

### Configuration Files
```bash
# HACHI config
~/.local/share/hachi/

# SteamVR config
~/.steam/steam/config/steamvr.vrsettings

# OpenXR runtime
/usr/share/openxr/1/openxr_monado.json
```

---

## 🌟 What Makes This Special

### For Arch Users
- Native pacman integration
- Rolling release compatible
- Works with custom kernels
- AUR-friendly
- Minimal dependencies

### Safe Design
- User-space only installation
- No system modifications
- Easy to remove
- GPU drivers untouched
- Fully reversible

### Complete Solution
- GUI management interface
- Experimental finger tracking
- Device monitoring
- Performance optimization
- All in one package

---

## 📚 Documentation

**Complete guides included:**
- `HACHI-FINGER-TRACKING.md` - Finger tracking setup
- `EMERGENCY-RECOVERY.md` - Recovery procedures
- `START-HERE-APOLOGY.md` - Important safety info
- `HACHI-OVERVIEW.md` - Feature overview

---

## 🎉 Summary

**Installation:**
```bash
./hachi_safe_installer_arch.sh
```

**Usage:**
```bash
hachi
```

**That's it!** Super simple for Arch/Garuda Linux! ✨

---

## ⚡ Pro Tips

1. **Update regularly:** `sudo pacman -Syu`
2. **Keep HACHI updated:** Reinstall when needed (it's safe!)
3. **Use Monado:** Better Linux VR support than SteamVR alone
4. **Good lighting:** Essential for finger tracking
5. **USB 3.0:** Use blue USB ports for headset

---

Made with ❤️ for Arch Linux VR gamers

**Tested on:** Arch Linux, Garuda Linux, Manjaro, EndeavourOS

**Compatible with:** All Arch-based distributions
