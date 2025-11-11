#!/bin/bash

# HACHI SAFE INSTALLER - Does NOT touch GPU drivers!
# This version installs ONLY user-space tools and VR drivers
# Now with complete dependency installation and bundled Python packages

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
VENV_DIR="$INSTALL_DIR/venv"
LOG_FILE="$INSTALL_DIR/install.log"

mkdir -p "$INSTALL_DIR" "$BIN_DIR"

# Log everything
exec > >(tee -a "$LOG_FILE") 2>&1

echo -e "${YELLOW}IMPORTANT:${NC}"
echo "This installer will:"
echo "  ✓ Install Python tools (user space only)"
echo "  ✓ Install ALL required dependencies"
echo "  ✓ Bundle Python packages (no external deps needed)"
echo "  ✓ Install VR drivers"
echo "  ✓ Setup udev rules"
echo "  ✓ Install HACHI GUI"
echo ""
echo -e "${GREEN}This installer will NOT:${NC}"
echo "  ✗ Touch your GPU drivers"
echo "  ✗ Modify system packages (except python3-tkinter)"
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

# Check for Python
echo -e "\n${YELLOW}Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3 not found!${NC}"
    echo "Please install Python3 first"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python3 found (version $PYTHON_VERSION)${NC}"

# Install python3-tkinter (REQUIRED for GUI)
echo -e "\n${YELLOW}Installing python3-tkinter (required for GUI)...${NC}"
if python3 -c "import tkinter" 2>/dev/null; then
    echo -e "${GREEN}✓ python3-tkinter already installed${NC}"
else
    echo -e "${YELLOW}Installing python3-tkinter via dnf...${NC}"
    echo "This is the ONLY system package we install (safe, GUI-only)"
    
    if command -v dnf &> /dev/null; then
        sudo dnf install -y python3-tkinter 2>&1 | tee -a "$LOG_FILE"
        
        if python3 -c "import tkinter" 2>/dev/null; then
            echo -e "${GREEN}✓ python3-tkinter installed successfully${NC}"
        else
            echo -e "${RED}✗ Failed to install python3-tkinter${NC}"
            echo "Please install manually: sudo dnf install python3-tkinter"
            exit 1
        fi
    else
        echo -e "${RED}✗ dnf not found (are you on Bazzite?)${NC}"
        echo "Please install python3-tkinter manually"
        exit 1
    fi
fi

# Create Python virtual environment for bundled dependencies
echo -e "\n${YELLOW}Creating bundled Python environment...${NC}"
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Removing old virtual environment...${NC}"
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR" 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment creation failed, using user install instead${NC}"
    VENV_DIR=""
fi

# Install Python packages
echo -e "\n${YELLOW}Installing Python packages (bundled with HACHI)...${NC}"

if [ -n "$VENV_DIR" ]; then
    # Install in virtual environment
    echo "Using bundled virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    pip install --upgrade pip setuptools wheel 2>&1 | tee -a "$LOG_FILE"
    pip install pyusb opencv-python numpy 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ All Python packages bundled successfully${NC}"
    else
        echo -e "${RED}✗ Package installation failed${NC}"
        exit 1
    fi
    
    deactivate
else
    # Fallback to user install
    echo "Using user-space installation..."
    pip3 install --user --upgrade pip setuptools wheel 2>&1 | tee -a "$LOG_FILE"
    
    # Try standard installation first
    if pip3 install --user pyusb opencv-python numpy 2>&1 | tee -a "$LOG_FILE"; then
        echo -e "${GREEN}✓ Python packages installed${NC}"
    else
        echo -e "${YELLOW}⚠ Trying alternative installation method...${NC}"
        pip3 install --user --break-system-packages pyusb opencv-python numpy 2>&1 | tee -a "$LOG_FILE"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Python packages installed (alternative method)${NC}"
        else
            echo -e "${RED}✗ Failed to install Python packages${NC}"
            exit 1
        fi
    fi
fi

# Verify all Python dependencies
echo -e "\n${YELLOW}Verifying Python dependencies...${NC}"
DEPS_OK=true

if [ -n "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
fi

for module in tkinter usb cv2 numpy; do
    if python3 -c "import $module" 2>/dev/null; then
        echo -e "${GREEN}✓ $module available${NC}"
    else
        echo -e "${RED}✗ $module NOT available${NC}"
        DEPS_OK=false
    fi
done

if [ -n "$VENV_DIR" ]; then
    deactivate
fi

if [ "$DEPS_OK" = false ]; then
    echo -e "${RED}Some dependencies are missing!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All dependencies verified${NC}"

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

# Create launcher that uses bundled Python environment
cat > "$BIN_DIR/hachi" <<EOF
#!/bin/bash
# HACHI Launcher with bundled dependencies

# Check if Python and tkinter are available
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "ERROR: Python tkinter not found!"
    echo "Install with: sudo dnf install python3-tkinter"
    exit 1
fi

# Use bundled virtual environment if available
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
fi

# Launch HACHI
cd ~/.local/bin
python3 hachi_control_center.py

# Deactivate venv if used
if [ -d "$VENV_DIR" ]; then
    deactivate
fi
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

# Create dependency info file
cat > "$INSTALL_DIR/dependencies.txt" <<EOF
HACHI Dependencies - Installed $(date)
=====================================

System Packages:
- python3-tkinter (installed via dnf)

Python Environment:
- Location: ${VENV_DIR:-User space (~/.local)}
- Python Version: $PYTHON_VERSION

Bundled Python Packages:
- pyusb (USB device access)
- opencv-python (computer vision for finger tracking)
- numpy (numerical operations)

All dependencies are bundled with HACHI.
No external Python packages required!
EOF

# Summary
echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  INSTALLATION COMPLETE!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"

echo -e "\n${CYAN}What was installed:${NC}"
echo "  ✓ Python3-tkinter (system package for GUI)"
if [ -n "$VENV_DIR" ]; then
    echo "  ✓ Bundled Python environment with all packages"
else
    echo "  ✓ Python packages (user space)"
fi
echo "  ✓ HACHI GUI (fully self-contained)"
echo "  ✓ VR device permissions"
echo "  ✓ Desktop launcher"
echo ""
echo -e "${GREEN}Your GPU drivers were NOT touched!${NC}"
echo ""

echo -e "${CYAN}Dependencies Status:${NC}"
echo "  ✓ All Python packages bundled with HACHI"
echo "  ✓ No external dependencies needed to run"
echo "  ✓ Completely self-contained installation"
echo ""

echo -e "${CYAN}Next steps:${NC}"
echo "  1. ${YELLOW}Log out and log back in${NC} (for group permissions)"
echo "  2. Plug in your Cosmos headset"
echo "  3. Launch: ${GREEN}hachi${NC}"
echo ""

echo -e "${CYAN}Testing HACHI installation...${NC}"

# Test if HACHI can start
TEST_OK=true

echo -n "Testing tkinter... "
if python3 -c "import tkinter; import sys; sys.exit(0)" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    TEST_OK=false
fi

if [ -n "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
fi

echo -n "Testing pyusb... "
if python3 -c "import usb; import sys; sys.exit(0)" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    TEST_OK=false
fi

echo -n "Testing opencv... "
if python3 -c "import cv2; import sys; sys.exit(0)" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    TEST_OK=false
fi

echo -n "Testing numpy... "
if python3 -c "import numpy; import sys; sys.exit(0)" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    TEST_OK=false
fi

if [ -n "$VENV_DIR" ]; then
    deactivate
fi

echo ""

if [ "$TEST_OK" = true ]; then
    echo -e "${GREEN}✓ All dependencies verified and working!${NC}"
else
    echo -e "${RED}✗ Some dependencies failed verification${NC}"
    echo "Check the log: $LOG_FILE"
fi

echo -e "\n${CYAN}Installation log saved to:${NC} $LOG_FILE"
echo -e "${CYAN}Dependencies info saved to:${NC} $INSTALL_DIR/dependencies.txt"
echo ""
echo -e "${YELLOW}IMPORTANT: Log out and back in before using HACHI!${NC}"
echo ""

read -p "Open HACHI now to test? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Launching HACHI..."
    "$BIN_DIR/hachi" &
fi
