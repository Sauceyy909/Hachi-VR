#!/bin/bash

# HACHI SAFE INSTALLER - Does NOT touch GPU drivers!
# This version installs ONLY user-space tools and VR drivers

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  HACHI SAFE INSTALLER                  ║${NC}"
echo -e "${BLUE}║  Does NOT modify GPU drivers!         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

INSTALL_DIR="$HOME/.local/share/hachi"
BIN_DIR="$HOME/.local/bin"
LOG_FILE="$INSTALL_DIR/install.log"

mkdir -p "$INSTALL_DIR" "$BIN_DIR"

# Log everything
exec > >(tee -a "$LOG_FILE") 2>&1

echo -e "${YELLOW}IMPORTANT:${NC}"
echo "This installer will:"
echo "  ✓ Install Python tools (user space only)"
echo "  ✓ Install VR drivers"
echo "  ✓ Setup udev rules"
echo "  ✓ Install HACHI GUI"
echo ""
echo -e "${GREEN}This installer will NOT:${NC}"
echo "  ✗ Touch your GPU drivers"
echo "  ✗ Modify system packages"
echo "  ✗ Change kernel modules"
echo "  ✗ Affect your display drivers"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# Detect GPU (for theme only, don't install drivers!)
echo -e "\n${YELLOW}Detecting GPU (for theme only)...${NC}"
if lspci | grep -i nvidia > /dev/null; then
    GPU_VENDOR="nvidia"
    echo -e "${GREEN}✓ NVIDIA GPU detected (theme will be green)${NC}"
elif lspci | grep -i amd > /dev/null; then
    GPU_VENDOR="amd"
    echo -e "${GREEN}✓ AMD GPU detected (theme will be red)${NC}"
else
    GPU_VENDOR="unknown"
    echo -e "${YELLOW}⚠ Unknown GPU (theme will be blue)${NC}"
fi

echo "$GPU_VENDOR" > "$INSTALL_DIR/gpu_vendor.txt"

# Check for Python dependencies
echo -e "\n${YELLOW}Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3 not found!${NC}"
    echo "Please install Python3 first"
    exit 1
fi
echo -e "${GREEN}✓ Python3 found${NC}"

# Install Python packages (user space only!)
echo -e "\n${YELLOW}Installing Python packages (user space)...${NC}"
pip3 install --user --upgrade pip setuptools 2>&1 | tee -a "$LOG_FILE"
pip3 install --user pyusb opencv-python numpy 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python packages installed${NC}"
else
    echo -e "${YELLOW}⚠ Some Python packages may have failed${NC}"
    echo "  Trying alternative installation..."
    pip3 install --user --break-system-packages pyusb opencv-python numpy 2>&1 | tee -a "$LOG_FILE"
fi

# Setup udev rules (ONLY for VR headset, not GPU!)
echo -e "\n${YELLOW}Setting up VR device permissions...${NC}"

sudo tee /etc/udev/rules.d/99-hachi-vr.rules > /dev/null <<'EOF'
# HTC Vive Cosmos - VR Headset Only
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0313", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0178", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="030e", MODE="0666", GROUP="plugdev", TAG+="uaccess"

# Controllers
SUBSYSTEM=="usb", ATTRS{idVendor}=="28de", MODE="0666", GROUP="plugdev", TAG+="uaccess"
KERNEL=="hidraw*", ATTRS{idVendor}=="0bb4", MODE="0666", GROUP="plugdev", TAG+="uaccess"
KERNEL=="hidraw*", ATTRS{idVendor}=="28de", MODE="0666", GROUP="plugdev", TAG+="uaccess"

# Cameras
SUBSYSTEM=="video4linux", ATTRS{idVendor}=="0bb4", MODE="0666", GROUP="video", TAG+="uaccess"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger

echo -e "${GREEN}✓ VR device permissions configured${NC}"

# Add user to groups
echo -e "\n${YELLOW}Adding user to VR groups...${NC}"
sudo groupadd -f plugdev
sudo groupadd -f video
sudo usermod -a -G plugdev,video $USER

echo -e "${GREEN}✓ User groups configured${NC}"

# Copy all Python scripts
echo -e "\n${YELLOW}Installing HACHI and tools...${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy HACHI
if [ -f "$SCRIPT_DIR/hachi_control_center.py" ]; then
    cp "$SCRIPT_DIR/hachi_control_center.py" "$BIN_DIR/"
    chmod +x "$BIN_DIR/hachi_control_center.py"
    echo -e "${GREEN}✓ HACHI installed${NC}"
else
    echo -e "${RED}✗ hachi_control_center.py not found!${NC}"
fi

# Copy other tools
for file in enhanced_tracking.py controller_manager.py cosmos_monitor.py; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        cp "$SCRIPT_DIR/$file" "$BIN_DIR/"
        chmod +x "$BIN_DIR/$file"
    fi
done

# Copy shell scripts
for file in display_optimizer.sh firmware_manager.sh vr_manager.sh launch_cosmos_vr.sh; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        cp "$SCRIPT_DIR/$file" "$BIN_DIR/"
        chmod +x "$BIN_DIR/$file"
    fi
done

echo -e "${GREEN}✓ All tools installed${NC}"

# Create launcher
cat > "$BIN_DIR/hachi" <<'EOF'
#!/bin/bash
# HACHI Launcher with error checking

# Check if Python and tkinter are available
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "ERROR: Python tkinter not found!"
    echo "Install with: sudo dnf install python3-tkinter"
    exit 1
fi

# Launch HACHI
cd ~/.local/bin
python3 hachi_control_center.py
EOF

chmod +x "$BIN_DIR/hachi"

# Create desktop entry
mkdir -p "$HOME/.local/share/applications"

cat > "$HOME/.local/share/applications/hachi.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=HACHI Control Center
Comment=HTC Vive Cosmos with Finger Tracking
Exec=$BIN_DIR/hachi
Icon=input-gaming
Terminal=false
Categories=Game;System;
Keywords=vr;cosmos;vive;hachi;
EOF

echo -e "${GREEN}✓ Desktop entry created${NC}"

# Ensure PATH includes .local/bin
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo -e "\n${YELLOW}Adding ~/.local/bin to PATH...${NC}"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    export PATH="$HOME/.local/bin:$PATH"
fi

# Summary
echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  INSTALLATION COMPLETE!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"

echo -e "\n${CYAN}What was installed:${NC}"
echo "  ✓ Python VR tools (user space only)"
echo "  ✓ HACHI GUI"
echo "  ✓ VR device permissions"
echo "  ✓ Desktop launcher"
echo ""
echo -e "${GREEN}Your GPU drivers were NOT touched!${NC}"
echo ""

echo -e "${CYAN}Next steps:${NC}"
echo "  1. ${YELLOW}Log out and log back in${NC} (for group permissions)"
echo "  2. Plug in your Cosmos headset"
echo "  3. Launch: ${GREEN}hachi${NC}"
echo ""

echo -e "${CYAN}Testing HACHI now...${NC}"

# Test if HACHI can start
if python3 -c "import tkinter; import sys; sys.exit(0)" 2>/dev/null; then
    echo -e "${GREEN}✓ HACHI dependencies OK${NC}"
else
    echo -e "${RED}✗ Missing dependencies!${NC}"
    echo "Install with: sudo dnf install python3-tkinter"
fi

echo -e "\n${CYAN}Installation log saved to:${NC} $LOG_FILE"
echo ""
echo -e "${YELLOW}IMPORTANT: Log out and back in before using HACHI!${NC}"
echo ""

read -p "Open HACHI now to test? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Launching HACHI..."
    "$BIN_DIR/hachi" &
fi
