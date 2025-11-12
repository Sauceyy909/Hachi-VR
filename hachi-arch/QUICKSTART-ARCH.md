# 🚀 HACHI Quick Start - Arch/Garuda Linux

## Get VR Working in 5 Minutes!

---

## Step 1: Extract Package
```bash
unzip hachi-arch.zip
cd hachi-arch
```

---

## Step 2: Run Installer
```bash
chmod +x hachi_safe_installer_arch.sh
./hachi_safe_installer_arch.sh
```

**What you'll see:**
- ✓ Detecting GPU (for theme)
- ✓ Installing tk (for GUI)
- ✓ Installing Python packages
- ✓ Setting up VR permissions
- ✓ Installing HACHI

**Takes:** ~2-3 minutes

---

## Step 3: Log Out & Back In

```bash
# DON'T reboot, just log out
# Click your user menu → Log Out
# Log back in
```

**Why?** Group permissions need this.

---

## Step 4: Plug In Headset

- Use USB 3.0 port (blue)
- Ensure headset is powered on
- Wait for it to initialize

**Check detection:**
```bash
lsusb | grep 0bb4
```

Should show: `ID 0bb4:0313 HTC Corp.`

---

## Step 5: Launch HACHI

```bash
hachi
```

Or find "HACHI Control Center" in your app menu.

**First time?** May take a few seconds to load.

---

## Step 6: Configure in HACHI

### Dashboard
- Should show "● Headset Connected"
- GPU info displayed
- Status indicators green

### Configure Tracking
1. Click "🎯 Tracking" tab
2. Click "Auto-Configure"
3. Wait for detection
4. Done!

### Optional: Enable Finger Tracking
1. Click "✋ Finger Tracking" tab
2. Click "Enable Finger Tracking"
3. Click "Calibrate Hands"
4. Follow on-screen instructions

---

## Step 7: Launch VR!

In HACHI Dashboard:
1. Click "🚀 Launch VR" button
2. Wait for SteamVR to start
3. Put on headset
4. Enjoy! 🎮

---

## ⚡ Super Quick Method

For experienced users:
```bash
# Install
./hachi_safe_installer_arch.sh && logout

# After re-login
hachi
# Configure → Launch VR → Done!
```

---

## 🛠️ Troubleshooting

### HACHI Won't Open
```bash
sudo pacman -S tk
hachi
```

### Headset Not Showing
```bash
# Check USB
lsusb | grep 0bb4

# Replug headset
# Try different USB port
```

### "Permission Denied"
```bash
# Check groups
groups | grep plugdev

# Not there? Log out and back in
```

### Python Errors
```bash
pip install --user --upgrade pyusb opencv-python numpy
hachi
```

---

## 📋 What Was Installed

**Your Home Directory:**
- `~/.local/bin/hachi` - Launcher
- `~/.local/share/hachi/` - Config & tools
- Desktop shortcut

**System (Minimal):**
- `tk` package (for GUI)
- udev rules (for VR permissions)
- Group memberships (plugdev, video)

**NOT Touched:**
- GPU drivers ✓
- Kernel modules ✓
- System packages ✓
- Display configuration ✓

---

## 🎯 Quick Commands

```bash
# Launch HACHI
hachi

# Check headset
lsusb | grep 0bb4

# Check installation
which hachi

# View logs
cat ~/.local/share/hachi/install.log

# Reinstall (if needed)
./hachi_safe_installer_arch.sh
```

---

## 🎮 Next Steps

### Install SteamVR
1. Open Steam
2. Library → Tools
3. Search "SteamVR"
4. Install

### Optional: Install Monado
For better Linux VR support:
```bash
# From AUR (if using yay)
yay -S monado-git

# Or see README-ARCH.md for building from source
```

### Configure Games
- VRChat: Enable finger tracking in avatar settings
- Job Simulator: Works automatically
- Half-Life: Alyx: Auto-detects finger tracking

---

## 💡 Pro Tips

1. **Use USB 3.0** - Blue ports work best
2. **Good lighting** - Essential for finger tracking
3. **Close apps** - Free up CPU/GPU for VR
4. **Update system** - `sudo pacman -Syu` before VR sessions
5. **Disable compositor** - Run `~/.local/bin/display_optimizer.sh`

---

## 🔍 System Check

Run this to verify everything:
```bash
echo "=== Quick System Check ==="
python3 --version
python3 -c "import tkinter" && echo "✓ GUI OK"
lsusb | grep 0bb4 && echo "✓ Headset OK" || echo "✗ Plug in headset"
which hachi && echo "✓ HACHI OK"
groups | grep plugdev && echo "✓ Permissions OK" || echo "⚠ Log out/in needed"
```

---

## 🆘 Quick Recovery

If something breaks:
```bash
# Remove HACHI
rm -rf ~/.local/share/hachi ~/.local/bin/hachi*

# Reinstall
./hachi_safe_installer_arch.sh
```

Your system stays safe! Everything is in user space.

---

## 📚 Full Documentation

See these files for complete info:
- `README-ARCH.md` - Full Arch guide
- `HACHI-FINGER-TRACKING.md` - Finger tracking details
- `EMERGENCY-RECOVERY.md` - Recovery procedures

---

## 🎉 You're Done!

**Total time:** ~5 minutes  
**Difficulty:** Easy  
**Risk:** None (user space only)  
**Result:** Working VR on Arch Linux!

```bash
hachi  # Let's go! 🚀
```

---

Made with ❤️ for Arch/Garuda Linux gamers

**Questions?** See full documentation or run diagnostic commands above.
