# 🎮 HACHI - Super Easy Installation (Arch/Garuda)

## Just Double-Click to Install!

### Method 1: GUI Installer (Easiest!)

**Just double-click this file:**
```
INSTALL_HACHI_arch.py
```

A window will open. Click the big green "INSTALL HACHI" button!

That's it! 🎉

---

## What If Double-Click Doesn't Work?

### Right-Click Method:

1. **Right-click** on `INSTALL_HACHI_arch.py`
2. Select **"Run as a Program"** or **"Execute"**
3. Click "Install HACHI" button

### Terminal Method (if right-click doesn't work):

```bash
python3 INSTALL_HACHI_arch.py
```

---

## After Installation

1. **Log out and log back in** (not reboot!)
2. Open terminal and type: `hachi`
3. Or find "HACHI Control Center" in your apps menu

---

## The GUI Installer Will:

✅ Show you everything it's doing  
✅ Install HACHI safely  
✅ NOT touch your GPU drivers  
✅ Ask for password only for device permissions  
✅ Tell you when it's done  

---

## Troubleshooting

### "Permission Denied" Error

**In terminal:**
```bash
chmod +x INSTALL_HACHI_arch.py
python3 INSTALL_HACHI_arch.py
```

### "Python Not Found" Error

Python should be pre-installed on Arch/Garuda. If not:
```bash
sudo pacman -S python
python3 INSTALL_HACHI_arch.py
```

### "Tkinter Not Found" Error

Install tkinter:
```bash
sudo pacman -S tk
python3 INSTALL_HACHI_arch.py
```

---

## After Installation - Using HACHI

### Launch HACHI:
```bash
hachi
```

### Or find in apps menu:
- Open application launcher
- Search for "HACHI"
- Click to open

### Enable Finger Tracking:
1. Launch HACHI
2. Click "✋ Finger Tracking" in sidebar
3. Click "Enable Finger Tracking"
4. Click "Calibrate Hands"
5. Done!

---

## What Gets Installed

**Everything goes to your home directory:**
- `~/.local/bin/hachi` - Launcher command
- `~/.local/bin/hachi_control_center.py` - Main GUI
- `~/.local/share/hachi/` - Configuration files
- Desktop shortcut in apps menu

**Nothing touches:**
- ❌ GPU drivers
- ❌ System packages (except tk)
- ❌ Display configuration
- ❌ Kernel modules

**100% Safe! ✅**

---

## Quick Start After Install

```bash
# 1. Log out and back in

# 2. Launch HACHI
hachi

# 3. Plug in your Cosmos headset

# 4. In HACHI:
#    - Dashboard shows status
#    - Auto-configure tracking
#    - Enable finger tracking
#    - Pair controllers
#    - Launch VR!
```

---

## Files in This Package

```
INSTALL_HACHI_arch.py        ← Double-click this!
hachi_control_center.py      ← Main application
enhanced_tracking_arch.py    ← Tracking tools
controller_manager.py        ← Controller setup
display_optimizer.sh         ← Performance tweaks
(and more...)
```

---

## Arch/Garuda Specific Notes

### Package Manager
- Uses `pacman` (native Arch package manager)
- Only installs `tk` package for GUI
- Everything else is user-space

### AUR Compatibility
- HACHI doesn't conflict with AUR packages
- Safe to use with custom kernels
- Works with Garuda's gaming optimizations

### Rolling Release
- Keep system updated: `sudo pacman -Syu`
- HACHI adapts to system updates
- Easy to reinstall if needed

---

## Need Help?

**Installation issues:**
- Run: `python3 INSTALL_HACHI_arch.py`
- Watch the log for errors

**HACHI won't open after install:**
```bash
# Install tkinter
sudo pacman -S tk
hachi
```

**Headset not detected:**
```bash
# Check USB connection
lsusb | grep 0bb4
```

**General questions:**
- See README-ARCH.md
- See HACHI-FINGER-TRACKING.md
- See EMERGENCY-RECOVERY.md

---

## Summary

**Installation:**
1. Double-click `INSTALL_HACHI_arch.py`
2. Click "Install HACHI" button
3. Wait ~2 minutes
4. Log out and back in

**Usage:**
1. Type `hachi` in terminal
2. Configure your VR
3. Launch VR
4. Enjoy! 🎮

**That's it!** Super easy! ✨

---

## Garuda Linux Users

**Extra Easy on Garuda!**
- Gaming optimizations already applied
- Steam likely pre-installed
- GPU drivers already configured
- Just install HACHI and go!

**Garuda Gaming Edition:**
- Everything ready for VR
- Best gaming experience
- Recommended for HACHI

---

## Manjaro Users

**Also Compatible!**
```bash
# Update system first
sudo pacman -Syu

# Then install HACHI
python3 INSTALL_HACHI_arch.py
```

---

## EndeavourOS Users

**Works Great!**
- Pure Arch experience
- Minimal base system
- HACHI adds VR support
- Clean integration

---

Made with ❤️ for easy Arch Linux VR
