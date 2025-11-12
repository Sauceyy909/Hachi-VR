# 🚨 HACHI Emergency Recovery Guide

## If Installation Broke Your System

### IMMEDIATE STEPS TO RECOVER

If the old installer broke your system:

#### 1. **Rollback System Changes (If using Bazzite)**

Bazzite uses rpm-ostree which has built-in rollback:

```bash
# See available versions
rpm-ostree status

# Rollback to previous version
rpm-ostree rollback

# Reboot
sudo reboot
```

This will undo ANY system package changes!

#### 2. **Remove HACHI Completely**

```bash
# Remove all HACHI files
rm -rf ~/.local/share/hachi
rm -rf ~/.local/bin/hachi*
rm -rf ~/.local/bin/*_manager.py
rm -rf ~/.local/bin/enhanced_tracking.py
rm ~/.local/share/applications/hachi.desktop

# Remove udev rules
sudo rm /etc/udev/rules.d/99-hachi*.rules
sudo rm /etc/udev/rules.d/99-vive*.rules
sudo udevadm control --reload-rules
```

#### 3. **If GPU Drivers Are Missing**

**For NVIDIA:**
```bash
# Check current status
nvidia-smi

# If broken, reinstall
sudo dnf install akmod-nvidia xorg-x11-drv-nvidia-cuda

# Or use Bazzite's built-in tool
ujust nvidia-install
```

**For AMD:**
```bash
# AMD drivers are usually built-in
# Update system
rpm-ostree upgrade

# Reboot
sudo reboot
```

---

## NEW SAFE INSTALLER

### What's Different

The **NEW** safe installer (`hachi_safe_installer.sh`):

✅ **DOES:**
- Install Python tools (user space only)
- Setup VR device permissions
- Install HACHI GUI
- Create desktop shortcuts

❌ **DOES NOT:**
- Touch GPU drivers AT ALL
- Modify system packages
- Use rpm-ostree
- Change kernel modules
- Affect display drivers

### How to Use Safe Installer

```bash
# 1. Extract fresh package
unzip hachi-safe.zip
cd hachi-safe

# 2. Run SAFE installer
chmod +x hachi_safe_installer.sh
./hachi_safe_installer.sh

# 3. Log out and back in
# (Not reboot, just log out!)

# 4. Launch HACHI
hachi
```

**No reboot needed! Just log out and back in.**

---

## Fixing "HACHI Won't Open"

### Problem 1: Missing Tkinter

**Symptom:** HACHI doesn't open, no error shown

**Fix:**
```bash
# Install tkinter
sudo dnf install python3-tkinter

# Test it
python3 -c "import tkinter"

# If no error, try HACHI again
hachi
```

### Problem 2: Missing Python Packages

**Symptom:** Error about cv2, numpy, or usb

**Fix:**
```bash
# Install packages
pip3 install --user opencv-python numpy pyusb

# Or with break-system-packages flag
pip3 install --user --break-system-packages opencv-python numpy pyusb
```

### Problem 3: Permission Denied

**Symptom:** Can't run hachi command

**Fix:**
```bash
# Make it executable
chmod +x ~/.local/bin/hachi
chmod +x ~/.local/bin/hachi_control_center.py

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Problem 4: PATH Not Set

**Symptom:** Command 'hachi' not found

**Fix:**
```bash
# Run directly
~/.local/bin/hachi

# Or add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Make permanent
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Problem 5: Display Issues

**Symptom:** GUI looks broken or doesn't render

**Fix:**
```bash
# For Wayland issues, try X11
# Log out, at login screen select "GNOME on Xorg" or "Plasma (X11)"

# Or force X11
export GDK_BACKEND=x11
hachi
```

---

## Fixing "Headset Not Detected"

### Check USB Connection

```bash
# See if headset is detected
lsusb | grep 0bb4

# Should show something like:
# Bus 003 Device 005: ID 0bb4:0313 HTC Corp. Vive Cosmos
```

**If not shown:**
- Try different USB port
- Use USB 3.0 port (blue)
- Try front panel USB
- Ensure headset is powered on

### Check Permissions

```bash
# Check udev rules
ls /etc/udev/rules.d/*hachi* /etc/udev/rules.d/*vive*

# Should show rule files

# Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Check groups
groups | grep plugdev

# If not in group, add yourself
sudo usermod -a -G plugdev $USER
# Then LOG OUT and back in
```

### Test Device Access

```bash
# Run monitor tool
python3 ~/.local/bin/cosmos_monitor.py

# Choose option 1 to scan
# Should detect headset if connected
```

---

## Fixing "SteamVR Can't Find Headset"

### Problem: SteamVR doesn't see Cosmos

**This is normal on Linux!** The Cosmos needs special setup.

#### Option 1: Use Monado Instead

Monado has better Linux support than SteamVR alone.

```bash
# Install Monado (safe, won't affect GPU)
# Check if already installed
which monado-service

# If not found, you'll need to build it
# Or use the enhanced tools
python3 ~/.local/bin/enhanced_tracking.py
```

#### Option 2: Configure SteamVR

```bash
# Create SteamVR config
mkdir -p ~/.steam/steam/config

cat > ~/.steam/steam/config/steamvr.vrsettings <<'EOF'
{
   "steamvr" : {
      "requireHmd" : false,
      "forcedDriver" : "",
      "activateMultipleDrivers" : true,
      "directMode" : true
   }
}
EOF

# Restart SteamVR
```

#### Option 3: Use HACHI's VR Manager

```bash
# Launch VR through HACHI
hachi
# Click "Launch VR"

# Or command line
~/.local/bin/vr_manager.sh
```

---

## Step-by-Step Recovery Process

### If You're Starting Fresh:

**1. Clean Bazzite Installation**
```bash
# If you had to reinstall Bazzite, good
# Now we'll do it right

# Check GPU drivers are working
nvidia-smi  # For NVIDIA
glxinfo | grep "OpenGL renderer"  # For AMD/NVIDIA
```

**2. Download SAFE Package**
```bash
# Get the new safe installer package
# Extract it
unzip hachi-safe.zip
```

**3. Run Safe Installer**
```bash
cd hachi-safe
chmod +x hachi_safe_installer.sh
./hachi_safe_installer.sh
```

**4. Log Out and Back In**
```bash
# Don't reboot! Just log out
# This applies group permissions
```

**5. Test HACHI**
```bash
hachi
```

**6. Check Headset**
```bash
# Plug in Cosmos
# Check detection
lsusb | grep 0bb4

# Should show device
```

**7. Launch VR**
```bash
# In HACHI GUI
# Click "Launch VR"
```

---

## Quick Diagnostic

Run this to check everything:

```bash
#!/bin/bash
echo "=== HACHI Diagnostic ==="
echo ""
echo "Python:"
python3 --version
echo ""
echo "Tkinter:"
python3 -c "import tkinter; print('✓ OK')" 2>&1
echo ""
echo "OpenCV:"
python3 -c "import cv2; print('✓ OK')" 2>&1
echo ""
echo "GPU:"
lspci | grep -i 'vga\|3d'
echo ""
echo "GPU Drivers:"
nvidia-smi 2>/dev/null || echo "Not NVIDIA or driver missing"
echo ""
echo "Headset:"
lsusb | grep 0bb4
echo ""
echo "HACHI installed:"
ls ~/.local/bin/hachi* 2>/dev/null || echo "✗ Not found"
echo ""
echo "Groups:"
groups | grep plugdev && echo "✓ In plugdev" || echo "✗ Not in plugdev"
echo ""
echo "PATH:"
echo $PATH | grep ".local/bin" && echo "✓ PATH OK" || echo "✗ PATH missing ~/.local/bin"
```

Save as `diagnostic.sh`, run with `bash diagnostic.sh`

---

## FAQ

### Q: Will the safe installer break my system?
**A:** No! It only installs user-space Python tools. No system changes.

### Q: Do I need to reinstall Bazzite?
**A:** No! Use the safe installer on your current system.

### Q: What if my GPU drivers are already broken?
**A:** Fix GPU drivers first (see recovery steps), then use safe installer.

### Q: Why did the old installer break things?
**A:** It used `rpm-ostree install` which can conflict with existing drivers. The new one doesn't do that.

### Q: Is my data safe?
**A:** Yes! HACHI only touches VR-related files and your home directory.

### Q: Can I use NVIDIA drivers with HACHI?
**A:** Yes! HACHI doesn't touch GPU drivers at all now.

### Q: What if SteamVR still doesn't work?
**A:** Try Monado instead. The Cosmos has limited Linux support, which is why we provide multiple options.

---

## Contact & Support

**If still broken:**
1. Save diagnostic output: `bash diagnostic.sh > diagnostic.txt`
2. Check install log: `cat ~/.local/share/hachi/install.log`
3. Report issue with both files

**Remember:**
- HACHI is experimental software
- Cosmos has limited Linux support
- Your GPU drivers should never be touched
- The safe installer is truly safe

---

## Prevention

**Next Time:**
1. ✅ Always use `hachi_safe_installer.sh`
2. ✅ Never use installers that modify GPU drivers
3. ✅ Check what an installer does before running
4. ✅ Use rpm-ostree rollback if system breaks
5. ✅ Keep backups of working configurations

---

Made with ❤️ and apologies for the previous version
