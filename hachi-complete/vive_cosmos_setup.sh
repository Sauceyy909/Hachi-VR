#!/bin/bash

# HTC Vive Cosmos Setup Script for Bazzite Linux
# This script sets up the necessary components for Cosmos support

set -e

echo "=========================================="
echo "HTC Vive Cosmos Setup for Bazzite Linux"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Bazzite
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}Cannot detect OS. Please ensure you're running Bazzite.${NC}"
    exit 1
fi

source /etc/os-release
if [[ ! "$NAME" =~ "Bazzite" ]]; then
    echo -e "${YELLOW}Warning: This script is designed for Bazzite Linux.${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}Step 1: Installing dependencies${NC}"
# Bazzite uses rpm-ostree for system packages
rpm-ostree install --assumeyes --allow-inactive \
    libusb-devel \
    hidapi-devel \
    systemd-devel \
    cmake \
    gcc-c++ \
    git \
    kernel-devel \
    || echo -e "${YELLOW}Some system packages may already be installed${NC}"

echo -e "${GREEN}Step 2: Setting up udev rules for Vive Cosmos${NC}"
sudo tee /etc/udev/rules.d/99-vive-cosmos.rules > /dev/null <<'EOF'
# HTC Vive Cosmos
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0313", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0178", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="28de", ATTRS{idProduct}=="2000", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="28de", ATTRS{idProduct}=="2101", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="030e", MODE="0666", GROUP="plugdev"

# HTC Vive Cosmos Controllers
KERNEL=="hidraw*", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0313", MODE="0666", GROUP="plugdev"
KERNEL=="hidraw*", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0178", MODE="0666", GROUP="plugdev"
EOF

echo -e "${GREEN}Step 3: Adding user to plugdev group${NC}"
sudo groupadd -f plugdev
sudo usermod -a -G plugdev $USER

echo -e "${GREEN}Step 4: Reloading udev rules${NC}"
sudo udevadm control --reload-rules
sudo udevadm trigger

echo -e "${GREEN}Step 5: Installing Monado (OpenXR runtime)${NC}"
# Monado has better Cosmos support than SteamVR on Linux
if [ ! -d "$HOME/monado" ]; then
    cd $HOME
    git clone https://gitlab.freedesktop.org/monado/monado.git
    cd monado
    mkdir -p build
    cd build
    
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DXRT_HAVE_STEAM=ON \
        -DXRT_HAVE_VULKAN=ON \
        -DXRT_HAVE_WAYLAND=ON \
        -DXRT_HAVE_SDL2=ON
    
    make -j$(nproc)
    sudo make install
else
    echo -e "${YELLOW}Monado already cloned. Updating...${NC}"
    cd $HOME/monado
    git pull
    cd build
    make -j$(nproc)
    sudo make install
fi

echo -e "${GREEN}Step 6: Configuring SteamVR${NC}"
STEAMVR_CONFIG="$HOME/.steam/steam/config/steamvr.vrsettings"
mkdir -p "$(dirname "$STEAMVR_CONFIG")"

if [ ! -f "$STEAMVR_CONFIG" ]; then
    cat > "$STEAMVR_CONFIG" <<'EOF'
{
   "steamvr" : {
      "allowReprojection" : false,
      "requireHmd" : false,
      "forcedDriver" : "null",
      "activateMultipleDrivers" : true
   }
}
EOF
fi

echo -e "${GREEN}Step 7: Creating launcher script${NC}"
cat > $HOME/launch_cosmos_vr.sh <<'EOF'
#!/bin/bash

# Set environment variables for VR
export XR_RUNTIME_JSON=/usr/share/openxr/1/openxr_monado.json
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json:/usr/share/vulkan/icd.d/radeon_icd.x86_64.json

# Start Monado service
monado-service &
MONADO_PID=$!

# Give Monado time to initialize
sleep 2

# Launch SteamVR
steam -applaunch 250820

# Cleanup on exit
trap "kill $MONADO_PID 2>/dev/null" EXIT
wait
EOF

chmod +x $HOME/launch_cosmos_vr.sh

echo -e "${GREEN}=========================================="
echo -e "Setup Complete!"
echo -e "==========================================${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT NEXT STEPS:${NC}"
echo "1. Reboot your system for udev rules and group changes to take effect"
echo "2. Install SteamVR from Steam if not already installed"
echo "3. Run './launch_cosmos_vr.sh' to start VR"
echo ""
echo -e "${YELLOW}NOTE:${NC} The Vive Cosmos has limited Linux support."
echo "Inside-out tracking may not work perfectly. Consider:"
echo "- Using Monado's OpenXR runtime (included)"
echo "- Checking for firmware updates on Windows"
echo "- Joining the Monado community for latest developments"
echo ""
echo -e "${RED}You MUST reboot now!${NC}"
read -p "Reboot now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl reboot
fi
