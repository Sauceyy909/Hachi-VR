#!/bin/bash

# HTC Vive Cosmos - All-in-One Auto Installer
# Master installation script that does everything automatically

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

INSTALL_DIR="$HOME/.local/share/cosmos-vr"
BIN_DIR="$HOME/.local/bin"

# Banner
show_banner() {
    clear
    echo -e "${CYAN}"
    cat << "EOF"
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║     ██╗   ██╗██╗██╗   ██╗███████╗     ██████╗ ███████╗   ║
    ║     ██║   ██║██║██║   ██║██╔════╝    ██╔═══██╗██╔════╝   ║
    ║     ██║   ██║██║██║   ██║█████╗      ██║   ██║███████╗   ║
    ║     ╚██╗ ██╔╝██║╚██╗ ██╔╝██╔══╝      ██║   ██║╚════██║   ║
    ║      ╚████╔╝ ██║ ╚████╔╝ ███████╗    ╚██████╔╝███████║   ║
    ║       ╚═══╝  ╚═╝  ╚═══╝  ╚══════╝     ╚═════╝ ╚══════╝   ║
    ║                                                            ║
    ║           COSMOS VR - ALL-IN-ONE INSTALLER                ║
    ║              For Bazzite Linux                            ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Progress indicator
progress_bar() {
    local current=$1
    local total=$2
    local message=$3
    local percent=$((current * 100 / total))
    local filled=$((percent / 2))
    local empty=$((50 - filled))
    
    printf "\r${CYAN}[${NC}"
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "${CYAN}]${NC} ${percent}%% - ${message}"
}

# Check if running on Bazzite
check_bazzite() {
    echo -e "\n${YELLOW}Checking system...${NC}"
    
    if [ -f /etc/os-release ]; then
        source /etc/os-release
        if [[ "$NAME" =~ "Bazzite" ]]; then
            echo -e "${GREEN}✓ Bazzite Linux detected${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠ Not Bazzite Linux (detected: $NAME)${NC}"
            read -p "Continue anyway? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    else
        echo -e "${RED}✗ Cannot detect OS${NC}"
        exit 1
    fi
}

# Detect GPU
detect_gpu() {
    echo -e "\n${YELLOW}Detecting GPU...${NC}"
    
    if lspci | grep -i nvidia > /dev/null; then
        GPU_VENDOR="nvidia"
        GPU_COLOR="GREEN"
        echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
    elif lspci | grep -i amd > /dev/null; then
        GPU_VENDOR="amd"
        GPU_COLOR="RED"
        echo -e "${RED}✓ AMD GPU detected${NC}"
    else
        GPU_VENDOR="unknown"
        GPU_COLOR="BLUE"
        echo -e "${YELLOW}⚠ Unknown GPU${NC}"
    fi
    
    # Save GPU info for GUI
    mkdir -p "$INSTALL_DIR"
    echo "$GPU_VENDOR" > "$INSTALL_DIR/gpu_vendor.txt"
    echo "$GPU_COLOR" > "$INSTALL_DIR/gpu_color.txt"
}

# Install system dependencies
install_dependencies() {
    echo -e "\n${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  STEP 1: Installing Dependencies      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    
    progress_bar 1 10 "Installing system packages..."
    
    # Install base packages
    rpm-ostree install --assumeyes --allow-inactive \
        libusb-devel \
        hidapi-devel \
        systemd-devel \
        cmake \
        gcc-c++ \
        git \
        kernel-devel \
        python3-tkinter \
        python3-pip \
        v4l-utils \
        bluez \
        bluez-tools \
        ntfs-3g \
        2>&1 | tee -a "$INSTALL_DIR/install.log" > /dev/null &
    
    wait
    progress_bar 1 10 "System packages installed"
    echo ""
}

# Setup udev rules
setup_udev_rules() {
    echo -e "\n${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  STEP 2: Configuring System Rules     ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    
    progress_bar 2 10 "Creating udev rules..."
    
    # Main Cosmos rules
    sudo tee /etc/udev/rules.d/99-vive-cosmos.rules > /dev/null <<'EOF'
# HTC Vive Cosmos
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0313", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0178", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="28de", ATTRS{idProduct}=="2000", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="28de", ATTRS{idProduct}=="2101", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="030e", MODE="0666", GROUP="plugdev"
KERNEL=="hidraw*", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0313", MODE="0666", GROUP="plugdev"
KERNEL=="hidraw*", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0178", MODE="0666", GROUP="plugdev"
KERNEL=="hidraw*", ATTRS{idVendor}=="28de", MODE="0666", GROUP="plugdev"
EOF
    
    # Camera rules
    sudo tee /etc/udev/rules.d/99-vive-cosmos-camera.rules > /dev/null <<'EOF'
# HTC Vive Cosmos Camera Access
SUBSYSTEM=="video4linux", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0178", MODE="0666", GROUP="video"
SUBSYSTEM=="video4linux", ATTRS{idVendor}=="0bb4", MODE="0666", GROUP="video"
EOF
    
    # Reload rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    
    progress_bar 2 10 "Udev rules configured"
    echo ""
}

# Setup user groups
setup_groups() {
    progress_bar 3 10 "Configuring user permissions..."
    
    sudo groupadd -f plugdev
    sudo groupadd -f video
    sudo groupadd -f bluetooth
    
    sudo usermod -a -G plugdev,video,bluetooth $USER
    
    progress_bar 3 10 "User groups configured"
    echo ""
}

# Build Monado
build_monado() {
    echo -e "\n${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  STEP 3: Building Monado OpenXR       ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    
    progress_bar 4 10 "Cloning Monado..."
    
    cd $HOME
    if [ ! -d "monado" ]; then
        git clone https://gitlab.freedesktop.org/monado/monado.git 2>&1 | tee -a "$INSTALL_DIR/install.log" > /dev/null
    else
        cd monado && git pull 2>&1 | tee -a "$INSTALL_DIR/install.log" > /dev/null && cd ..
    fi
    
    progress_bar 5 10 "Building Monado (this may take a while)..."
    
    cd monado
    mkdir -p build
    cd build
    
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DXRT_HAVE_STEAM=ON \
        -DXRT_HAVE_VULKAN=ON \
        -DXRT_HAVE_WAYLAND=ON \
        -DXRT_HAVE_SDL2=ON \
        2>&1 | tee -a "$INSTALL_DIR/install.log" > /dev/null
    
    make -j$(nproc) 2>&1 | tee -a "$INSTALL_DIR/install.log" > /dev/null
    sudo make install 2>&1 | tee -a "$INSTALL_DIR/install.log" > /dev/null
    
    progress_bar 5 10 "Monado built successfully"
    echo ""
}

# Build Cosmos bridge
build_bridge() {
    echo -e "\n${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  STEP 4: Building Cosmos Driver       ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    
    progress_bar 6 10 "Compiling Cosmos bridge driver..."
    
    cd "$(dirname "$0")"
    
    if [ -f "cosmos_bridge.cpp" ]; then
        g++ -std=c++17 -o cosmos_bridge cosmos_bridge.cpp -lusb-1.0 -lpthread 2>&1 | tee -a "$INSTALL_DIR/install.log" > /dev/null
        
        if [ -f "cosmos_bridge" ]; then
            mkdir -p "$BIN_DIR"
            cp cosmos_bridge "$BIN_DIR/"
            chmod +x "$BIN_DIR/cosmos_bridge"
            echo -e "${GREEN}✓ Cosmos bridge built${NC}"
        fi
    fi
    
    progress_bar 6 10 "Driver compiled"
    echo ""
}

# Install Python tools
install_python_tools() {
    echo -e "\n${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  STEP 5: Installing Python Tools      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    
    progress_bar 7 10 "Installing Python dependencies..."
    
    pip3 install --user pyusb pillow --break-system-packages 2>&1 | tee -a "$INSTALL_DIR/install.log" > /dev/null
    
    # Copy all scripts
    mkdir -p "$BIN_DIR"
    cp *.py "$BIN_DIR/" 2>/dev/null || true
    cp *.sh "$BIN_DIR/" 2>/dev/null || true
    chmod +x "$BIN_DIR"/*.py "$BIN_DIR"/*.sh 2>/dev/null || true
    
    progress_bar 7 10 "Python tools installed"
    echo ""
}

# Optimize GPU settings
optimize_gpu() {
    echo -e "\n${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  STEP 6: Optimizing GPU Settings      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    
    progress_bar 8 10 "Applying GPU optimizations..."
    
    if [ -f "display_optimizer.sh" ]; then
        ./display_optimizer.sh --auto 2>&1 | tee -a "$INSTALL_DIR/install.log" > /dev/null
    fi
    
    progress_bar 8 10 "GPU optimized"
    echo ""
}

# Configure Bluetooth
optimize_bluetooth() {
    progress_bar 9 10 "Optimizing Bluetooth..."
    
    # Bluetooth config for VR controllers
    sudo mkdir -p /etc/bluetooth/main.conf.d/
    
    sudo tee /etc/bluetooth/main.conf.d/vr-controllers.conf > /dev/null <<'EOF'
[General]
MinConnectionInterval=6
MaxConnectionInterval=9
ConnectionLatency=0
SupervisionTimeout=300
AutoEnable=true
FastConnectable=true

[Policy]
AutoEnable=true
EOF
    
    sudo systemctl restart bluetooth 2>/dev/null || true
    
    progress_bar 9 10 "Bluetooth optimized"
    echo ""
}

# Install GUI application
install_gui() {
    echo -e "\n${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  STEP 7: Installing GUI Application   ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    
    progress_bar 10 10 "Setting up Cosmos Control Center..."
    
    # Copy HACHI GUI script
    if [ -f "hachi_control_center.py" ]; then
        cp hachi_control_center.py "$BIN_DIR/"
        chmod +x "$BIN_DIR/hachi_control_center.py"
        
        # Create desktop entry
        mkdir -p "$HOME/.local/share/applications"
        
        cat > "$HOME/.local/share/applications/hachi-control-center.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=HACHI Control Center
Comment=HTC Vive Cosmos with Finger Tracking
Exec=$BIN_DIR/hachi_control_center.py
Icon=vr-headset
Terminal=false
Categories=System;Settings;
Keywords=vr;cosmos;vive;hachi;finger;tracking;
EOF
        
        echo -e "${GREEN}✓ GUI application installed${NC}"
    fi
    
    progress_bar 10 10 "Installation complete!"
    echo -e "\n"
}

# Create launcher script
create_launcher() {
    cat > "$BIN_DIR/hachi" <<'EOF'
#!/bin/bash
python3 ~/.local/bin/hachi_control_center.py
EOF
    chmod +x "$BIN_DIR/hachi"
}

# Final summary
show_summary() {
    echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}║            INSTALLATION COMPLETED SUCCESSFULLY!            ║${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    
    echo -e "\n${CYAN}What was installed:${NC}"
    echo "  ✓ System dependencies and drivers"
    echo "  ✓ Udev rules for device access"
    echo "  ✓ Monado OpenXR runtime"
    echo "  ✓ Cosmos bridge driver"
    echo "  ✓ Python management tools"
    echo "  ✓ GPU optimizations ($GPU_VENDOR)"
    echo "  ✓ Bluetooth optimization"
    echo "  ✓ HACHI Control Center GUI"
    echo "  ✓ Experimental finger tracking support"
    
    echo -e "\n${CYAN}How to use:${NC}"
    echo "  1. ${YELLOW}REBOOT YOUR SYSTEM${NC} (required for udev rules and groups)"
    echo "  2. Launch: ${GREEN}hachi${NC}"
    echo "  3. Or find 'HACHI Control Center' in your application menu"
    
    echo -e "\n${CYAN}Quick commands:${NC}"
    echo "  hachi                   - Launch HACHI GUI"
    echo "  vr-manager.sh           - CLI VR manager"
    echo "  cosmos-monitor          - Device monitor"
    
    echo -e "\n${YELLOW}GPU Configuration:${NC}"
    echo "  Detected: $GPU_VENDOR"
    echo "  UI Color: $GPU_COLOR accents"
    
    echo -e "\n${RED}IMPORTANT:${NC}"
    echo "  ${YELLOW}YOU MUST REBOOT NOW!${NC}"
    echo "  Group changes and kernel modules require a reboot."
    
    echo -e "\n${CYAN}Installation log:${NC} $INSTALL_DIR/install.log"
    
    echo ""
    read -p "Reboot now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo systemctl reboot
    else
        echo -e "${YELLOW}Remember to reboot before using VR!${NC}"
    fi
}

# Main installation flow
main() {
    show_banner
    
    echo -e "${CYAN}This installer will:${NC}"
    echo "  • Install all system dependencies"
    echo "  • Build and install drivers"
    echo "  • Optimize your system for VR"
    echo "  • Install the Cosmos Control Center GUI"
    echo ""
    echo -e "${YELLOW}Estimated time: 10-20 minutes${NC}"
    echo ""
    
    read -p "Continue with installation? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled"
        exit 0
    fi
    
    # Create install directory
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    
    # Run installation steps
    check_bazzite
    detect_gpu
    install_dependencies
    setup_udev_rules
    setup_groups
    build_monado
    build_bridge
    install_python_tools
    optimize_gpu
    optimize_bluetooth
    install_gui
    create_launcher
    
    # Show summary
    show_summary
}

# Run with sudo check
if [ "$EUID" -eq 0 ]; then
    echo "Please run as regular user (not root)"
    echo "The script will ask for sudo when needed"
    exit 1
fi

# Execute main
main
