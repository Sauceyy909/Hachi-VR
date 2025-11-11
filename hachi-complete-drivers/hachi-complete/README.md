# 🎮 HACHI - Complete VR Drivers Package

## 八 (Hachi) = Vive in Japanese

**The ultimate HTC Vive Cosmos solution for Bazzite Linux with experimental finger tracking!**

---

## 📦 What's Included

This package contains **everything** you need to run HTC Vive Cosmos on Bazzite Linux:

### Core Application
- **hachi_control_center.py** - Beautiful GUI with finger tracking
- **hachi_safe_installer.sh** - Safe, automatic installation

### Management Tools
- **enhanced_tracking.py** - Advanced tracking configuration
- **controller_manager.py** - Bluetooth controller pairing
- **cosmos_monitor.py** - Device diagnostics
- **display_optimizer.sh** - Performance optimization
- **firmware_manager.sh** - Firmware management tools
- **vr_manager.sh** - VR session manager
- **launch_cosmos_vr.sh** - Quick VR launcher

### Low-Level Drivers
- **cosmos_bridge.cpp** - USB driver bridge
- **Makefile** - Build system

### Documentation
- Complete setup guides
- Troubleshooting documentation
- Feature explanations

---

## 🚀 Quick Start

### 1. Install (One Command!)

```bash
cd hachi-complete
./hachi_safe_installer.sh
```

**What it does:**
- ✅ Installs python3-tkinter (GUI support)
- ✅ Creates bundled Python environment
- ✅ Installs ALL Python packages automatically
- ✅ Sets up VR device permissions
- ✅ Installs HACHI and all tools
- ✅ **Does NOT touch GPU drivers!**

### 2. Log Out & Back In

```bash
# Required for group permissions
# Just log out of your session and log back in
```

### 3. Launch HACHI

```bash
hachi
```

**That's it!** HACHI will open with all dependencies bundled.

---

## ✨ Features

### 🎨 Beautiful GUI
- Triple black theme
- GPU-specific accents (Green for NVIDIA, Red for AMD)
- Professional HTC-style interface
- Real-time monitoring

### ✋ Experimental Finger Tracking
- Uses Cosmos front cameras
- Hand and finger detection
- Compatible with VRChat, Job Simulator, etc.
- Calibration tools included

### 🚀 Complete VR Management
- One-click VR launch
- Automatic tracking setup
- Controller management
- Display optimization
- All-in-one interface

---

## 📋 System Requirements

### Operating System
- **Bazzite Linux** (tested)
- Other rpm-ostree systems may work

### Hardware
- HTC Vive Cosmos headset
- Controllers (optional but recommended)
- GPU: NVIDIA or AMD (Intel may work)

### Software
- Python 3.8 or higher
- USB 3.0 port
- SteamVR (optional, for full VR)

---

## 🔒 Safety

### What the Installer DOES
- ✅ Installs python3-tkinter via dnf
- ✅ Creates bundled Python environment
- ✅ Installs VR device permissions
- ✅ Sets up user groups

### What the Installer DOES NOT Do
- ❌ Touch GPU drivers
- ❌ Modify system Python
- ❌ Change kernel modules
- ❌ Affect display drivers
- ❌ Use rpm-ostree (except tkinter)

**Your system stays safe!**

---

## 📚 Documentation Files

- **EMERGENCY-RECOVERY.md** - System recovery guide
- **HACHI-FINGER-TRACKING.md** - Finger tracking guide
- **HACHI-OVERVIEW.md** - Complete feature overview
- **README-SAFE-VERSION.md** - Safe installer explanation
- **START-HERE-APOLOGY.md** - Important first-time info
- **INSTALLER-IMPROVEMENTS.md** - What's new

---

## 🎯 Usage

### Launch HACHI
```bash
hachi
```

### Enable Finger Tracking
1. Open HACHI
2. Go to "Finger Tracking" tab
3. Click "Enable Finger Tracking"
4. Calibrate hands
5. Launch VR!

### Pair Controllers
1. Open HACHI
2. Go to "Controllers" tab
3. Click "Scan & Pair Controllers"
4. Follow on-screen instructions

### Optimize Display
1. Open HACHI
2. Go to "Display" tab
3. Click "Run Full Optimization"

---

## 🐛 Troubleshooting

### HACHI Won't Open
```bash
# Check if tkinter is installed
python3 -c "import tkinter"

# If error, install it
sudo dnf install python3-tkinter
```

### Headset Not Detected
```bash
# Check USB connection
lsusb | grep 0bb4

# Should show: ID 0bb4:0313 HTC Corp.
```

### Finger Tracking Not Working
- Ensure good lighting
- Check camera permissions
- Try recalibrating
- See HACHI-FINGER-TRACKING.md

---

## 📦 Bundled Dependencies

All Python packages are bundled with HACHI:
- **pyusb** - USB device communication
- **opencv-python** - Computer vision
- **numpy** - Numerical operations

**No manual package installation needed!**

---

## 🔧 Advanced

### Build Cosmos Bridge Driver
```bash
cd hachi-complete
make
sudo make install
```

### Manual VR Launch
```bash
./launch_cosmos_vr.sh
```

### Device Monitoring
```bash
python3 cosmos_monitor.py
```

---

## ❓ FAQ

**Q: Will this break my GPU drivers?**
A: No! The safe installer doesn't touch GPU drivers at all.

**Q: Do I need to install Python packages?**
A: No! All packages are bundled with HACHI automatically.

**Q: Does finger tracking work well?**
A: It's experimental. Results depend on camera drivers and lighting.

**Q: Can I use this with other headsets?**
A: No, HACHI is specifically for the HTC Vive Cosmos.

**Q: Is SteamVR required?**
A: Recommended but not required. Monado also works.

---

## 🎉 What Makes HACHI Special

### Innovation
- First Linux VR solution with finger tracking
- Uses existing Cosmos hardware
- No additional equipment needed
- Completely open source

### Integration
- All-in-one VR management
- Beautiful GUI with theming
- Automatic setup and configuration
- Bundled dependencies

### Safety
- Doesn't modify GPU drivers
- Isolated Python environment
- Easy to uninstall
- Clear documentation

---

## 📞 Support

**If you have issues:**
1. Check the documentation files
2. Read EMERGENCY-RECOVERY.md if system broke
3. Check install log: `~/.local/share/hachi/install.log`
4. Verify dependencies: See troubleshooting section

---

## 🙏 Credits

Made with ❤️ for the Linux VR community

**Special thanks to:**
- Monado OpenXR runtime team
- Bazzite Linux developers
- VR Linux community

---

## 📜 License

This software is provided as-is for educational and personal use.

---

## 🚀 Getting Started Right Now

```bash
# 1. Extract package
unzip hachi-complete.zip
cd hachi-complete

# 2. Run installer
./hachi_safe_installer.sh

# 3. Log out and back in

# 4. Launch HACHI
hachi

# 5. Enjoy VR on Linux! 🎮
```

---

**Welcome to the future of Linux VR!** 🎮🐧✨

**八 (Hachi) - Making Cosmos work on Linux since 2024**
