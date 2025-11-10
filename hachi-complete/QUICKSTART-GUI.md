# 🚀 Cosmos Control Center - Quick Start Guide

## The Ultimate All-in-One Solution

This package includes an **automatic installer** and a **beautiful GUI** that replaces all the complexity with a single interface.

---

## ✨ What You Get

### 🎨 **Cosmos Control Center GUI**
A sleek, HTC-style interface with:
- **Triple Black Theme** - Professional dark UI
- **GPU-Specific Accents** - Green for NVIDIA, Red for AMD
- **Real-time Monitoring** - See device status at a glance
- **One-Click Actions** - Launch VR, configure tracking, pair controllers
- **Integrated Tools** - Everything accessible from one place

### 🤖 **Automatic Installer**
One command installs everything:
- All system dependencies
- Monado OpenXR runtime
- Cosmos drivers
- Python tools
- GPU optimizations
- The GUI application

---

## 📦 Installation (3 Simple Steps)

### Step 1: Run the Installer
```bash
chmod +x cosmos_auto_installer.sh
./cosmos_auto_installer.sh
```

The installer will:
- ✓ Detect your system and GPU
- ✓ Install all dependencies
- ✓ Build drivers
- ✓ Optimize settings
- ✓ Install the GUI
- ✓ Set up everything automatically

**Time: 10-20 minutes**

### Step 2: Reboot
```bash
sudo reboot
```
This is **required** for udev rules and group permissions.

### Step 3: Launch the GUI
```bash
cosmos-control
```

Or find "**Cosmos Control Center**" in your application menu!

---

## 🎮 Using the Control Center

### Dashboard
- View real-time device status
- Quick action buttons
- System information
- GPU detection and theming

### Tracking Configuration
- **Hybrid Mode** - Best quality (Camera + IMU)
- **IMU Only** - Most stable (Rotation only)
- **Auto-Configure** - Automatic detection
- **Room Calibration** - Set up play space

### Controller Management
- **One-Click Pairing** - Automated Bluetooth setup
- **Connectivity Test** - Check signal strength
- **Optimization** - Low-latency settings

### Display Settings
- **Performance Optimizer** - GPU-specific tweaks
- **90Hz Enforcement** - Full refresh rate
- **Monitoring Tools** - Real-time FPS tracking

### Firmware Tools
- **Update Guides** - Windows VM setup
- **Backup Utilities** - Save firmware data
- **Import Tools** - Get files from Windows

---

## 🎨 GUI Theme

The interface automatically detects your GPU and applies matching colors:

**NVIDIA GPU** → **Green Accents** 🟢
```
Triple Black + NVIDIA Green (#76b900)
Professional gaming aesthetic
```

**AMD GPU** → **Red Accents** 🔴
```
Triple Black + AMD Red (#ed1c24)
Bold, powerful look
```

**Unknown GPU** → **Blue Accents** 🔵
```
Triple Black + Neutral Blue
Clean, universal theme
```

---

## 🚀 Quick Actions

### From the Dashboard:

**Launch VR Session**
- Starts Monado
- Opens SteamVR
- Ready to play!

**Configure Tracking**
- Choose tracking mode
- Calibrate room
- Test tracking

**Pair Controllers**
- Scan for devices
- Automatic pairing
- Signal testing

---

## 📊 What The Installer Does

### System Setup
```
✓ Install libusb, hidapi, cmake
✓ Install Python dependencies
✓ Install Bluetooth tools
✓ Install v4l-utils for cameras
✓ Install ntfs-3g for Windows access
```

### Driver Installation
```
✓ Clone and build Monado OpenXR
✓ Compile Cosmos USB bridge
✓ Install Python management tools
✓ Create udev rules
✓ Configure user groups
```

### Optimizations
```
✓ GPU-specific settings (NVIDIA/AMD)
✓ Bluetooth low-latency config
✓ CPU performance governor
✓ SteamVR configuration
```

### GUI Setup
```
✓ Install Control Center
✓ Create desktop entry
✓ Set up launcher command
✓ Configure theme
```

---

## 🖥️ GUI Features

### Navigation Sidebar
```
📊 Dashboard      - Overview and quick actions
🎯 Tracking       - Configuration and calibration
🎮 Controllers    - Pairing and testing
🖥️ Display        - Performance optimization
⚙️ Firmware       - Update guides and tools
🚀 Launch VR      - Start VR session
```

### Menu Bar
```
File > Preferences, Exit
Tools > Device Monitor, Performance Monitor, Logs
Help > Documentation, About
```

### Real-Time Status
```
● Headset Connected/Disconnected
  GPU: NVIDIA/AMD/Unknown
  Live system monitoring
```

---

## 🎯 Typical Workflow

1. **First Time Setup**
   ```bash
   ./cosmos_auto_installer.sh
   # Reboot
   cosmos-control
   ```

2. **Configure Tracking**
   - Open Control Center
   - Go to Tracking
   - Click "Auto-Configure"

3. **Pair Controllers**
   - Go to Controllers
   - Click "Scan & Pair Controllers"
   - Wait for automatic pairing

4. **Optimize Display**
   - Go to Display
   - Click "Run Full Optimization"

5. **Launch VR**
   - Click "Launch VR" from Dashboard
   - Or from sidebar
   - Put on headset and play!

---

## 🔧 Advanced Features

### Command Line Access
Even with the GUI, all command-line tools remain available:

```bash
cosmos-control              # Launch GUI
vr-manager.sh              # CLI VR manager
cosmos-monitor             # Device monitor
enhanced_tracking.py       # Advanced tracking config
controller_manager.py      # Controller tools
display_optimizer.sh       # Display optimization
firmware_manager.sh        # Firmware management
```

### Custom Scripts
The GUI launches these tools in the background. You can also run them manually for more control.

### Log Files
```
~/.local/share/cosmos-vr/install.log
~/.local/share/vr-logs/
```

---

## 💡 Tips for Best Experience

### Tracking
- Start with "Auto-Configure"
- Use IMU-only for seated VR (most stable)
- Calibrate room-scale every few sessions

### Controllers
- Keep within 3 meters of PC
- Use external Bluetooth dongle for best results
- Charge fully before pairing

### Display
- Run optimization after GPU driver updates
- Monitor performance while in VR
- Lower supersampling if frames drop

### General
- Keep firmware updated (requires Windows)
- Check device status before launching VR
- Close background apps for better performance

---

## 🎮 Supported Games

**Excellent (⭐⭐⭐⭐⭐)**
- Beat Saber
- Superhot VR
- Pistol Whip
- Job Simulator
- Most seated/standing games

**Good (⭐⭐⭐⭐)**
- Half-Life: Alyx
- Boneworks
- VRChat (standing)

**Limited (⭐⭐⭐)**
- Room-scale competitive games
- Games requiring precise tracking

---

## 📱 Desktop Integration

After installation, find the Control Center:

**Applications Menu:**
```
System > Settings > Cosmos Control Center
```

**Command Line:**
```bash
cosmos-control
```

**Desktop Shortcut:**
Available in ~/.local/share/applications/

---

## 🆘 Troubleshooting

### GUI Won't Launch
```bash
# Check Python/Tkinter
python3 -m tkinter

# Reinstall
pip3 install --user --upgrade pillow --break-system-packages
```

### Device Not Detected
- Check USB connection
- Verify udev rules: `ls /etc/udev/rules.d/*cosmos*`
- Check groups: `groups | grep plugdev`
- Reboot if just installed

### Colors Look Wrong
- GPU detection automatic
- Manually set: Edit `~/.local/share/cosmos-vr/gpu_vendor.txt`
- Options: `nvidia`, `amd`, `unknown`

### Tools Not Working
```bash
# Check installation
ls ~/.local/bin/

# Reinstall specific tool
cp tool_name.py ~/.local/bin/
chmod +x ~/.local/bin/tool_name.py
```

---

## 🌟 What Makes This Special

### Before
- Multiple terminal windows
- Manual commands
- Complex configuration
- Hard to remember syntax

### After
- One beautiful GUI
- Point and click
- Automatic optimization
- Visual feedback

### The Difference
```
Old way:
$ python3 enhanced_tracking.py
# Navigate menu
# Choose option 1
# ...etc

New way:
Open GUI → Click "Configure Tracking" → Click "Auto-Configure" → Done!
```

---

## 🎨 UI Screenshots

(Imagine these, since I can't show actual screenshots)

**Dashboard:**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  COSMOS         ● Headset Connected ┃
┃  Control Center   GPU: NVIDIA       ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ NAV   │  Dashboard                  ┃
┃ ━━━━━ │  ┌─────┐ ┌─────┐ ┌─────┐  ┃
┃ 📊    │  │ ● ✓ │ │🎯 ○ │ │🎮 0/2│  ┃
┃ 🎯    │  └─────┘ └─────┘ └─────┘  ┃
┃ 🎮    │                             ┃
┃ 🖥️    │  Quick Actions              ┃
┃ ⚙️    │  [🚀 Launch VR]            ┃
┃ 🚀    │  [🎯 Configure] [🎮 Pair]  ┃
┗━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 🎁 Everything Included

**Core System:**
- ✅ cosmos_auto_installer.sh
- ✅ cosmos_control_center.py
- ✅ cosmos_bridge.cpp
- ✅ All Python tools
- ✅ All shell scripts

**Documentation:**
- ✅ This quick start guide
- ✅ Enhanced README
- ✅ Improvements document
- ✅ Original documentation

---

## 🚀 Get Started NOW

```bash
# Extract the package
unzip cosmos-all-in-one.zip
cd cosmos-all-in-one

# Run the installer
./cosmos_auto_installer.sh

# Reboot when prompted
# Then launch the GUI
cosmos-control

# That's it! Enjoy VR on Linux! 🎮
```

---

## 📞 Support

**Log Files:** `~/.local/share/cosmos-vr/install.log`
**Config:** `~/.local/share/cosmos-vr/`
**Tools:** `~/.local/bin/`

**Need Help?**
- Check the troubleshooting section
- Run `make check` in the extracted directory
- Review logs for errors
- Consult the detailed README files

---

## 🎉 Enjoy!

You now have the most complete HTC Vive Cosmos solution for Linux, with a professional GUI that matches HTC's style but works on your favorite OS!

**Happy VR Gaming! 🎮🐧**
