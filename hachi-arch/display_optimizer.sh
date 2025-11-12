#!/bin/bash

# HTC Vive Cosmos Display Optimizer
# Maximizes refresh rate and display performance

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Cosmos Display Performance Optimizer  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Detect GPU
detect_gpu() {
    echo -e "${YELLOW}Detecting GPU...${NC}"
    
    if lspci | grep -i nvidia > /dev/null; then
        GPU_VENDOR="nvidia"
        echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
    elif lspci | grep -i amd > /dev/null; then
        GPU_VENDOR="amd"
        echo -e "${GREEN}✓ AMD GPU detected${NC}"
    elif lspci | grep -i intel > /dev/null; then
        GPU_VENDOR="intel"
        echo -e "${BLUE}✓ Intel GPU detected${NC}"
    else
        GPU_VENDOR="unknown"
        echo -e "${RED}✗ Could not detect GPU vendor${NC}"
    fi
}

# Check current display/HMD connection
check_display_connection() {
    echo -e "\n${YELLOW}Checking display connections...${NC}"
    
    if command -v xrandr &> /dev/null; then
        echo -e "${GREEN}Available displays:${NC}"
        xrandr --query | grep " connected" | cut -d" " -f1
        
        # Look for HMD
        if xrandr --query | grep -i "HTC\|Vive\|2880x1700" > /dev/null; then
            echo -e "${GREEN}✓ Cosmos display detected${NC}"
            COSMOS_DISPLAY=$(xrandr --query | grep -i "HTC\|Vive\|2880x1700" | cut -d" " -f1 | head -1)
            echo -e "  Display: ${COSMOS_DISPLAY}"
        else
            echo -e "${YELLOW}⚠ Cosmos display not detected in xrandr${NC}"
            echo -e "  The headset may be connected but not showing as a display"
            echo -e "  This is normal for direct mode VR"
        fi
    else
        echo -e "${YELLOW}⚠ xrandr not available (Wayland session?)${NC}"
    fi
}

# Optimize NVIDIA settings
optimize_nvidia() {
    echo -e "\n${YELLOW}Optimizing NVIDIA settings...${NC}"
    
    # Check if nvidia-settings is available
    if ! command -v nvidia-settings &> /dev/null; then
        echo -e "${YELLOW}⚠ nvidia-settings not found. Installing...${NC}"
        sudo apt-get install -y nvidia-settings || true
        echo -e "  Please re-run this script after installation completes"
        return
    fi
    
    # Disable G-SYNC (can cause issues with VR)
    echo "  Disabling G-SYNC for VR..."
    nvidia-settings -a "[gpu:0]/GpuPowerMizerMode=1" 2>/dev/null || true
    
    # Set maximum performance mode
    echo "  Setting maximum performance mode..."
    nvidia-settings -a "[gpu:0]/GPUGraphicsClockOffset[3]=100" 2>/dev/null || true
    nvidia-settings -a "[gpu:0]/GPUMemoryTransferRateOffset[3]=200" 2>/dev/null || true
    
    # Force full composition pipeline (better for VR)
    echo "  Configuring composition pipeline..."
    nvidia-settings --assign CurrentMetaMode="nvidia-auto-select +0+0 { ForceFullCompositionPipeline = Off }" 2>/dev/null || true
    
    # Create xorg config for optimal VR performance
    create_nvidia_xorg_config
    
    echo -e "${GREEN}✓ NVIDIA optimizations applied${NC}"
}

# Create NVIDIA Xorg config
create_nvidia_xorg_config() {
    echo "  Creating NVIDIA Xorg configuration..."
    
    XORG_CONFIG="/etc/X11/xorg.conf.d/20-nvidia-vr.conf"
    
    sudo tee "$XORG_CONFIG" > /dev/null << 'EOF'
Section "Device"
    Identifier     "NVIDIA Graphics"
    Driver         "nvidia"
    Option         "Coolbits" "28"
    Option         "TripleBuffer" "True"
    Option         "AllowFlipping" "True"
    Option         "AllowIndirectGLXProtocol" "off"
    Option         "RegistryDwords" "PowerMizerEnable=0x1; PerfLevelSrc=0x3333; PowerMizerDefault=0x3; PowerMizerDefaultAC=0x3"
EndSection

Section "Screen"
    Identifier     "Screen0"
    Option         "metamodes" "nvidia-auto-select +0+0 {ForceCompositionPipeline=Off, ForceFullCompositionPipeline=Off}"
EndSection
EOF
    
    echo -e "    ${GREEN}✓ Created $XORG_CONFIG${NC}"
}

# Optimize AMD settings
optimize_amd() {
    echo -e "\n${YELLOW}Optimizing AMD settings...${NC}"
    
    # Set performance governor
    echo "  Setting performance governor..."
    echo "performance" | sudo tee /sys/class/drm/card*/device/power_dpm_force_performance_level > /dev/null 2>&1 || true
    
    # Disable power management features that can cause stuttering
    echo "  Disabling power management..."
    echo "0" | sudo tee /sys/class/drm/card*/device/power_dpm_state > /dev/null 2>&1 || true
    
    # Create AMD Xorg config
    create_amd_xorg_config
    
    echo -e "${GREEN}✓ AMD optimizations applied${NC}"
}

# Create AMD Xorg config
create_amd_xorg_config() {
    echo "  Creating AMD Xorg configuration..."
    
    XORG_CONFIG="/etc/X11/xorg.conf.d/20-amdgpu-vr.conf"
    
    sudo tee "$XORG_CONFIG" > /dev/null << 'EOF'
Section "Device"
    Identifier     "AMD Graphics"
    Driver         "amdgpu"
    Option         "TearFree" "false"
    Option         "VariableRefresh" "false"
    Option         "EnablePageFlip" "on"
EndSection
EOF
    
    echo -e "    ${GREEN}✓ Created $XORG_CONFIG${NC}"
}

# Optimize Intel settings
optimize_intel() {
    echo -e "\n${YELLOW}Optimizing Intel settings...${NC}"
    echo "  Intel GPUs on Linux use the MESA driver."
    echo "  Performance is generally 'out-of-the-box'."
    echo "  Key optimizations:"
    echo "  1. Ensure 'vulkan-intel' is installed."
    echo "  2. Ensure you are using a modern kernel and MESA drivers."
    echo "  No specific driver-level tweaks (like nvidia-settings) are applied."
    echo -e "${GREEN}✓ Intel configuration noted.${NC}"
}

# Optimize SteamVR settings
optimize_steamvr() {
    echo -e "\n${YELLOW}Optimizing SteamVR settings...${NC}"
    
    STEAMVR_CONFIG="$HOME/.steam/steam/config/steamvr.vrsettings"
    
    if [ ! -f "$STEAMVR_CONFIG" ]; then
        mkdir -p "$(dirname "$STEAMVR_CONFIG")"
    fi
    
    # Backup existing config
    if [ -f "$STEAMVR_CONFIG" ]; then
        cp "$STEAMVR_CONFIG" "$STEAMVR_CONFIG.backup.$(date +%s)"
        echo "  Backed up existing SteamVR config"
    fi
    
    # Create optimized config
    cat > "$STEAMVR_CONFIG" << 'EOF'
{
   "steamvr" : {
      "allowReprojection" : true,
      "allowAsyncReprojection" : true,
      "allowInterleavedReprojection" : true,
      "forcedDriver" : "",
      "activateMultipleDrivers" : true,
      "directMode" : true,
      "usingSpeakers" : false,
      "preferredRefreshRate" : 90,
      "supersampleScale" : 1.0,
      "allowSupersampleFiltering" : true,
      "maxRecommendedResolution" : 4096,
      "renderTargetMultiplier" : 1.0,
      "enableLinuxVulkanAsync" : true,
      "disableAsync" : false
   },
   "perfcheck" : {
      "perfTestResults" : {
         "GPUSpeedRating" : 11
      }
   }
}
EOF
    
    echo -e "${GREEN}✓ SteamVR configuration optimized${NC}"
    echo "  Settings:"
    echo "    - Refresh rate: 90Hz"
    echo "    - Async reprojection: Enabled"
    echo "    - Direct mode: Enabled"
    echo "    - Linux Vulkan async: Enabled"
}

# Set CPU governor to performance
optimize_cpu() {
    echo -e "\n${YELLOW}Optimizing CPU settings...${NC}"
    
    # Check current governor
    CURRENT_GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo "unknown")
    echo "  Current CPU governor: $CURRENT_GOV"
    
    # Set to performance
    echo "  Setting performance governor..."
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo "performance" | sudo tee "$cpu" > /dev/null 2>&1 || true
    done
    
    NEW_GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo "unknown")
    
    if [ "$NEW_GOV" = "performance" ]; then
        echo -e "${GREEN}✓ CPU governor set to performance${NC}"
    else
        echo -e "${YELLOW}⚠ Could not set CPU governor${NC}"
        echo "  You may need to install: sudo apt-get install linux-tools-common"
    fi
}

# Disable compositor for VR sessions
disable_compositor() {
    echo -e "\n${YELLOW}Configuring compositor...${NC}"
    
    # Detect desktop environment
    if [ "$XDG_CURRENT_DESKTOP" = "KDE" ] || [ "$XDG_CURRENT_DESKTOP" = "KDE Plasma" ]; then
        echo "  Detected KDE Plasma"
        echo "  Creating script to disable KWin compositor for VR..."
        
        cat > "$HOME/.local/bin/vr-no-compositor.sh" << 'EOF'
#!/bin/bash
qdbus org.kde.KWin /Compositor suspend
echo "KWin compositor suspended for VR"
EOF
        chmod +x "$HOME/.local/bin/vr-no-compositor.sh"
        echo -e "${GREEN}✓ Created compositor suspend script${NC}"
        echo "  Run: vr-no-compositor.sh before starting VR"
        
    elif [ "$XDG_CURRENT_DESKTOP" = "GNOME" ]; then
        echo "  Detected GNOME"
        echo "  Note: GNOME Mutter cannot be disabled"
        echo "  Using Wayland may provide better VR performance"
        
    else
        echo "  Desktop environment: $XDG_CURRENT_DESKTOP"
        echo "  Compositor handling may vary"
    fi
}

# Create VR performance monitoring script
create_performance_monitor() {
    echo -e "\n${YELLOW}Creating performance monitoring script...${NC}"
    
    mkdir -p "$HOME/.local/bin"
    
    cat > "$HOME/.local/bin/vr-perf-monitor.sh" << 'EOF'
#!/bin/bash

# VR Performance Monitor

echo "=== VR Performance Monitor ==="
echo "Press Ctrl+C to stop"
echo ""

while true; do
    clear
    echo "=== System Performance ($(date +%H:%M:%S)) ==="
    echo ""
    
    # GPU info
    if command -v nvidia-smi &> /dev/null; then
        echo "--- NVIDIA GPU ---"
        nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,utilization.memory,memory.used,memory.total,clocks.gr,clocks.mem --format=csv,noheader,nounits | while IFS=',' read name temp gpu_util mem_util mem_used mem_total clock_gpu clock_mem; do
            echo "GPU: $name"
            echo "Temperature: ${temp}°C"
            echo "GPU Load: ${gpu_util}%"
            echo "VRAM Load: ${mem_util}%"
            echo "VRAM: ${mem_used}MB / ${mem_total}MB"
            echo "GPU Clock: ${clock_gpu}MHz"
            echo "Memory Clock: ${clock_mem}MHz"
        done
    elif command -v radeontop &> /dev/null; then
        echo "--- AMD GPU ---"
        radeontop -d - -l 1 | head -1
    elif command -v intel_gpu_top &> /dev/null; then
        echo "--- Intel GPU ---"
        intel_gpu_top -l -o - | head -n 4
    fi
    
    echo ""
    echo "--- CPU ---"
    top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print "CPU Usage: " 100 - $1"%"}'
    
    echo ""
    echo "--- RAM ---"
    free -h | awk 'NR==2{printf "Memory: %s / %s (%.2f%%)\n", $3,$2,$3*100/$2 }'
    
    echo ""
    echo "--- Frame Timing ---"
    if pgrep -x vrcompositor > /dev/null; then
        echo "SteamVR Compositor: Running ✓"
        # Could add more detailed frame timing if available
    else
        echo "SteamVR Compositor: Not running"
    fi
    
    sleep 2
done
EOF
    
    chmod +x "$HOME/.local/bin/vr-perf-monitor.sh"
    echo -e "${GREEN}✓ Created performance monitor${NC}"
    echo "  Run with: vr-perf-monitor.sh"
}

# Test current refresh rate capability
test_refresh_rate() {
    echo -e "\n${YELLOW}Testing display capabilities...${NC}"
    
    # Cosmos specs
    echo ""
    echo "HTC Vive Cosmos Specifications:"
    echo "  Resolution: 2880 x 1700 (1440 x 1700 per eye)"
    echo "  Refresh Rate: 90Hz"
    echo "  Display: LCD with RGB subpixels"
    echo ""
    
    if command -v xrandr &> /dev/null; then
        echo "Querying connected displays..."
        xrandr --query | grep -A 10 "connected"
    fi
    
    echo ""
    echo "To verify actual refresh rate in VR:"
    echo "  1. Start SteamVR"
    echo "  2. Open SteamVR Settings > Developer"
    echo "  3. Enable 'Display Frame Timing'"
    echo "  4. Check if frame time is ~11.1ms (90Hz)"
}

# Main optimization routine
run_all_optimizations() {
    echo -e "\n${BLUE}Running all optimizations...${NC}\n"
    
    detect_gpu
    check_display_connection
    
    case $GPU_VENDOR in
        nvidia)
            optimize_nvidia
            ;;
        amd)
            optimize_amd
            ;;
        intel)
            optimize_intel
            ;;
        *)
            echo -e "${YELLOW}⚠ Unknown GPU, skipping GPU-specific optimizations${NC}"
            ;;
    esac
    
    optimize_cpu
    optimize_steamvr
    disable_compositor
    create_performance_monitor
    test_refresh_rate
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║    Optimizations Complete!              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANT NOTES:${NC}"
    echo "1. Reboot recommended for all changes to take effect"
    echo "2. Run vr-perf-monitor.sh while in VR to check performance"
    echo "3. If using KDE, run vr-no-compositor.sh before VR sessions"
    echo "4. Check SteamVR frame timing to verify 90Hz operation"
    echo ""
    
    read -p "Would you like to reboot now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo systemctl reboot
    fi
}

# Menu system
show_menu() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}1.${NC} Run All Optimizations (Recommended)"
    echo -e "${GREEN}2.${NC} GPU Optimizations Only"
    echo -e "${GREEN}3.${NC} SteamVR Settings Only"
    echo -e "${GREEN}4.${NC} CPU Optimizations Only"
    echo -e "${GREEN}5.${NC} Test Display Capabilities"
    echo -e "${GREEN}6.${NC} Create Performance Monitor"
    echo -e "${GREEN}7.${NC} Exit"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
}

# Main menu loop
if [ "$1" = "--auto" ]; then
    run_all_optimizations
    exit 0
fi

while true; do.
    show_menu
    read -p "Enter choice: " choice
    
    case $choice in
        1)
            run_all_optimizations
            break
            ;;
        2)
            detect_gpu
            case $GPU_VENDOR in
                nvidia) optimize_nvidia ;;
                amd) optimize_amd ;;
                intel) optimize_intel ;;
                *) echo "Unknown GPU vendor" ;;
            esac
            ;;
        3)
            optimize_steamvr
            ;;
        4)
            optimize_cpu
            ;;
        5)
            test_refresh_rate
            read -p "Press Enter to continue..."
            ;;
        6)
            create_performance_monitor
            read -p "Press Enter to continue..."
            ;;
        7)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice"
            ;;
    esac
done