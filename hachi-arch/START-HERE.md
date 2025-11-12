# 🎮 HACHI - START HERE (Arch/Garuda Linux Edition)

## Welcome to HACHI for Arch Linux!

**å…« (Hachi) = Vive in Japanese**

This is the **Arch Linux compatible version** of HACHI, the complete HTC Vive Cosmos VR driver and management system for Linux.

---

## 🚀 Quick Start (Choose Your Method)

### Method 1: GUI Installer (Recommended)

**Just double-click this file:**
```
INSTALL_HACHI_arch.py
```

Click the big green button and you're done!

### Method 2: Terminal Installer

```bash
./hachi_safe_installer_arch.sh
```

Follow the prompts, then log out and back in.

### Method 3: Ultra Quick (One Command)

```bash
./hachi_safe_installer_arch.sh && logout
```

After re-login, run `hachi` and you're ready!

---

## 📚 Documentation Guide

### Start Here
- **QUICKSTART-ARCH.md** ← Read this first!
- **README-ARCH.md** ← Full Arch guide

### Installation Help
- **DOUBLE-CLICK-INSTALL-ARCH.md** ← GUI installer guide
- **EMERGENCY-RECOVERY-ARCH.md** ← If something goes wrong

### Features
- **HACHI-FINGER-TRACKING.md** ← Finger tracking setup
- **HACHI-OVERVIEW.md** ← All features explained

### Recovery
- **EMERGENCY-RECOVERY-ARCH.md** ← Arch-specific recovery
- **EMERGENCY-RECOVERY.md** ← General recovery

---

## ⚡ Super Quick Install

```bash
# 1. Extract (already done if you're reading this!)
cd hachi-arch

# 2. Install
./hachi_safe_installer_arch.sh

# 3. Log out and back in

# 4. Launch
hachi
```

**Total time:** ~3 minutes  
**Difficulty:** Easy  
**Risk:** None (100% user-space)

---

## 🎯 What You Need to Know

### This is SAFE for Arch/Garuda
- ✅ Uses `pacman` (native package manager)
- ✅ Only installs `tk` package (for GUI)
- ✅ Everything else is user-space
- ✅ NO modifications to GPU drivers
- ✅ NO kernel changes
- ✅ Fully reversible

### Compatible with
- ✅ Arch Linux
- ✅ Garuda Linux
- ✅ Manjaro
- ✅ EndeavourOS
- ✅ All Arch-based distributions

### Works With
- ✅ NVIDIA GPUs
- ✅ AMD GPUs
- ✅ Intel GPUs
- ✅ Custom kernels
- ✅ AUR packages

---

## 📦 What's Included

### Main Installer
- `hachi_safe_installer_arch.sh` - Safe terminal installer
- `INSTALL_HACHI_arch.py` - GUI installer

### Core Application
- `hachi_control_center.py` - Main HACHI GUI
- `enhanced_tracking_arch.py` - Tracking manager (Arch-compatible)
- `controller_manager.py` - Controller pairing
- `cosmos_monitor.py` - Device diagnostics

### Tools
- `display_optimizer.sh` - Performance optimization
- `firmware_manager.sh` - Firmware tools
- `vr_manager.sh` - VR session manager
- `launch_cosmos_vr.sh` - Quick VR launcher

### Drivers
- `cosmos_bridge.cpp` - USB driver bridge
- `Cmake` & `Makefile` - Build files

### Documentation
- **Arch-specific guides** (this and more!)
- **Feature documentation**
- **Recovery guides**
- **Troubleshooting**

---

## 🎮 After Installation

### Launch HACHI
```bash
hachi
```

### First Time Setup
1. Dashboard shows status
2. Plug in Cosmos headset
3. Click "Auto-Configure" in Tracking tab
4. (Optional) Enable finger tracking
5. Click "Launch VR"
6. Enjoy!

---

## 🛠️ Troubleshooting

### HACHI Won't Open
```bash
sudo pacman -S tk
hachi
```

### Headset Not Detected
```bash
lsusb | grep 0bb4
# Should show HTC device
```

### Permission Issues
```bash
groups | grep plugdev
# If not there, log out and back in
```

### For More Help
See **EMERGENCY-RECOVERY-ARCH.md** for complete troubleshooting.

---

## 💡 Pro Tips for Arch Users

1. **Keep Updated:** `sudo pacman -Syu` before VR sessions
2. **AUR Helpers:** Consider `yay -S monado-git` for best tracking
3. **Gaming Kernel:** Use `linux-zen` for lower latency
4. **Compositor:** Run display_optimizer.sh for best performance
5. **Garuda Users:** Your system is already optimized!

---

## 🔍 System Requirements

### Minimum
- Arch Linux or derivative
- Python 3.8+
- tk (auto-installed)
- USB 3.0 port
- HTC Vive Cosmos headset

### Recommended
- Garuda Linux Gaming Edition
- NVIDIA GTX 1060 / AMD RX 580 / Intel Arc A380
- 16GB RAM
- SSD
- Fast CPU (i5/Ryzen 5 or better)

---

## 📖 Documentation Reading Order

**New Users:**
1. QUICKSTART-ARCH.md (5 min read)
2. README-ARCH.md (full guide)
3. HACHI-FINGER-TRACKING.md (if interested)

**Experienced Users:**
1. README-ARCH.md (skim)
2. Pick specific docs as needed

**Having Issues:**
1. EMERGENCY-RECOVERY-ARCH.md
2. Check logs: `~/.local/share/hachi/install.log`

---

## 🎯 Quick Commands

```bash
# Install
./hachi_safe_installer_arch.sh

# Launch
hachi

# Check headset
lsusb | grep 0bb4

# Reinstall (if needed)
./hachi_safe_installer_arch.sh

# Complete removal
rm -rf ~/.local/share/hachi ~/.local/bin/hachi*
```

---

## 🌟 Why HACHI for Arch?

### Native Integration
- Uses `pacman` natively
- No foreign package managers
- Works with rolling release
- AUR compatible

### Arch Philosophy
- User-space only
- No bloat
- You control it
- Transparent operation

### Gaming Ready
- Optimized for Arch
- Works with gaming kernels
- Low latency
- Maximum performance

---

## ⚠️ Important Notes

### What HACHI Does NOT Touch
- ❌ GPU drivers
- ❌ Kernel modules
- ❌ System packages (except tk)
- ❌ Boot configuration
- ❌ Display settings

### 100% Safe
- Everything in `~/.local`
- Easy to remove
- No system breakage
- Fully reversible

---

## 🎉 Ready to Start?

```bash
# GUI Installer (Easiest)
python3 INSTALL_HACHI_arch.py

# OR Terminal Installer
./hachi_safe_installer_arch.sh

# After install + logout/login
hachi
```

---

## 📞 Need Help?

**Quick Issues:**
- Can't open HACHI? Install tk: `sudo pacman -S tk`
- Headset not found? Check USB: `lsusb | grep 0bb4`
- Permission denied? Log out and back in

**Detailed Help:**
- See EMERGENCY-RECOVERY-ARCH.md
- Check install log: `~/.local/share/hachi/install.log`
- Run diagnostic: See EMERGENCY-RECOVERY-ARCH.md

**Arch Resources:**
- Arch Wiki: https://wiki.archlinux.org/
- Garuda Forum: https://forum.garudalinux.org/

---

## 🚀 Let's Get Started!

**For Quickest Start:**
1. Read **QUICKSTART-ARCH.md** (5 minutes)
2. Run installer
3. Launch HACHI
4. Enjoy VR on Arch!

**For Complete Understanding:**
1. Read **README-ARCH.md** (15 minutes)
2. Understand features
3. Optimize settings
4. Master HACHI!

---

## 📋 Package Contents

```
hachi-arch/
├── START-HERE.md                  ← You are here!
│
├── Installation:
│   ├── hachi_safe_installer_arch.sh  ← Terminal installer
│   └── INSTALL_HACHI_arch.py          ← GUI installer
│
├── Documentation:
│   ├── QUICKSTART-ARCH.md             ← Start here!
│   ├── README-ARCH.md                 ← Full guide
│   ├── DOUBLE-CLICK-INSTALL-ARCH.md   ← GUI help
│   ├── EMERGENCY-RECOVERY-ARCH.md     ← Troubleshooting
│   ├── HACHI-FINGER-TRACKING.md       ← Finger tracking
│   └── HACHI-OVERVIEW.md              ← Features
│
├── Application:
│   ├── hachi_control_center.py        ← Main GUI
│   ├── enhanced_tracking_arch.py      ← Tracking tools
│   ├── controller_manager.py          ← Controllers
│   └── cosmos_monitor.py              ← Diagnostics
│
├── Tools:
│   ├── display_optimizer.sh           ← Performance
│   ├── firmware_manager.sh            ← Firmware
│   ├── vr_manager.sh                  ← VR sessions
│   └── launch_cosmos_vr.sh            ← Quick VR
│
└── Drivers:
    ├── cosmos_bridge.cpp              ← USB driver
    ├── Cmake                          ← Build config
    └── Makefile                       ← Build file
```

---

## 🎮 Final Words

HACHI brings professional VR management to Arch Linux with:
- ✅ Native pacman integration
- ✅ 100% safe user-space installation
- ✅ Experimental finger tracking
- ✅ Complete VR management
- ✅ Arch philosophy: simple, transparent, powerful

**Command to start:**
```bash
./hachi_safe_installer_arch.sh
```

**Welcome to Linux VR on Arch!** 🎮🐧✨

---

Made with ❤️ for the Arch Linux VR community

**Tested on:** Arch Linux, Garuda Linux, Manjaro, EndeavourOS
**Compatible with:** All Arch-based distributions
