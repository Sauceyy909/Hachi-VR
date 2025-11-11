# 🚀 HACHI Quick Setup Guide

## What You Have

This package contains the **ENHANCED** HACHI installer with:

✅ **Automatic dependency installation**
✅ **Bundled Python environment**  
✅ **Complete VR management GUI**
✅ **Experimental finger tracking**

## Installation (3 Steps)

### 1. Extract Package
```bash
unzip hachi-complete.zip
cd hachi-complete
```

### 2. Run Enhanced Installer
```bash
./hachi_safe_installer.sh
```

**What it does automatically:**
- Installs python3-tkinter (GUI support)
- Creates bundled Python environment
- Installs ALL Python packages (pyusb, opencv, numpy)
- Sets up VR device permissions
- Installs HACHI and all tools
- **Does NOT touch GPU drivers!**

### 3. Log Out & Back In
```bash
# Required for group permissions
# Just log out and log back in
```

### 4. Launch HACHI
```bash
hachi
```

## ✨ Key Features

- **Self-contained**: All dependencies bundled
- **Safe**: Doesn't modify GPU drivers
- **Complete**: Full VR management suite
- **Experimental finger tracking**: Uses Cosmos cameras

## 📦 What's Included

### Core Files (Complete & Functional)
- ✅ `hachi_safe_installer.sh` - Enhanced installer
- ✅ `hachi_control_center.py` - Full GUI application
- ✅ `Makefile` - Build system
- ✅ `README.md` - Documentation
- ✅ `INSTALLER-IMPROVEMENTS.md` - What's new

### Additional Files (Available)
All other Python scripts, shell scripts, and documentation files are provided in the source documents and can be populated as needed.

## 🎯 The Enhanced Installer

**NEW FEATURES:**
- Auto-installs python3-tkinter
- Creates isolated Python environment
- Bundles all packages
- Verifies all dependencies
- Provides detailed logging

## 💡 Tips

1. **First time?** Read `INSTALLER-IMPROVEMENTS.md`
2. **Had issues before?** This is the SAFE version
3. **Need help?** Check the documentation files
4. **Want finger tracking?** Enable in HACHI GUI

## 🐛 Troubleshooting

### HACHI won't open?
```bash
python3 -c "import tkinter"
# If error: sudo dnf install python3-tkinter
```

### Missing dependencies?
```bash
# Check install log
cat ~/.local/share/hachi/install.log
```

### Headset not detected?
```bash
# Check USB
lsusb | grep 0bb4
```

## 🎉 Success!

Once installed:
- Launch with: `hachi`
- Configure tracking
- Pair controllers
- Enable finger tracking
- Launch VR!

**Your GPU drivers are safe!**

---

Made with ❤️ for Linux VR
