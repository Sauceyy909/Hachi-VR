#!/bin/bash

# VR Manager Script for HTC Vive Cosmos on Bazzite Linux
# This script provides a convenient interface for managing VR sessions

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MONADO_BIN="/usr/local/bin/monado-service"
COSMOS_BRIDGE="/usr/local/bin/cosmos_bridge"
COSMOS_MONITOR="/usr/local/bin/cosmos_monitor"
LOG_DIR="$HOME/.local/share/vr-logs"
mkdir -p "$LOG_DIR"

# Functions
print_header() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  HTC Vive Cosmos - Bazzite Linux VR   ║${NC}"
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo ""
}

check_device() {
    echo -e "${YELLOW}Checking for Vive Cosmos...${NC}"
    if lsusb | grep -q "0bb4:0313"; then
        echo -e "${GREEN}✓ Cosmos headset detected${NC}"
        return 0
    else
        echo -e "${RED}✗ Cosmos headset not detected${NC}"
        echo -e "${YELLOW}Please check:${NC}"
        echo "  - Headset is plugged in and powered on"
        echo "  - USB connection is secure"
        echo "  - udev rules are installed"
        return 1
    fi
}

check_services() {
    echo -e "\n${YELLOW}Checking VR services...${NC}"
    
    # Check Monado
    if [ -f "$MONADO_BIN" ]; then
        echo -e "${GREEN}✓ Monado installed${NC}"
    else
        echo -e "${RED}✗ Monado not found${NC}"
        echo "  Run the setup script to install Monado"
    fi
    
    # Check SteamVR
    if [ -d "$HOME/.steam/steam/steamapps/common/SteamVR" ]; then
        echo -e "${GREEN}✓ SteamVR installed${NC}"
    else
        echo -e "${YELLOW}⚠ SteamVR not found${NC}"
        echo "  Install SteamVR from Steam"
    fi
    
    # Check if Monado is running
    if pgrep -x "monado-service" > /dev/null; then
        echo -e "${GREEN}✓ Monado service is running${NC}"
    else
        echo -e "${YELLOW}○ Monado service is not running${NC}"
    fi
}

start_monado() {
    echo -e "\n${YELLOW}Starting Monado service...${NC}"
    
    if pgrep -x "monado-service" > /dev/null; then
        echo -e "${YELLOW}Monado is already running${NC}"
        return 0
    fi
    
    export XR_RUNTIME_JSON=/usr/share/openxr/1/openxr_monado.json
    
    "$MONADO_BIN" > "$LOG_DIR/monado.log" 2>&1 &
    MONADO_PID=$!
    
    sleep 2
    
    if pgrep -x "monado-service" > /dev/null; then
        echo -e "${GREEN}✓ Monado started successfully (PID: $MONADO_PID)${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to start Monado${NC}"
        echo "Check logs: cat $LOG_DIR/monado.log"
        return 1
    fi
}

stop_monado() {
    echo -e "\n${YELLOW}Stopping Monado service...${NC}"
    
    if pgrep -x "monado-service" > /dev/null; then
        killall monado-service
        sleep 1
        echo -e "${GREEN}✓ Monado stopped${NC}"
    else
        echo -e "${YELLOW}Monado is not running${NC}"
    fi
}

start_steamvr() {
    echo -e "\n${YELLOW}Starting SteamVR...${NC}"
    
    # Make sure Monado is running first
    if ! pgrep -x "monado-service" > /dev/null; then
        echo -e "${YELLOW}Starting Monado first...${NC}"
        start_monado
    fi
    
    # Launch SteamVR
    export XR_RUNTIME_JSON=/usr/share/openxr/1/openxr_monado.json
    steam -applaunch 250820 > "$LOG_DIR/steamvr.log" 2>&1 &
    
    echo -e "${GREEN}✓ SteamVR launched${NC}"
    echo -e "${YELLOW}Note: Check SteamVR window for status${NC}"
}

start_bridge() {
    echo -e "\n${YELLOW}Starting Cosmos bridge driver...${NC}"
    
    if [ ! -f "$COSMOS_BRIDGE" ]; then
        echo -e "${RED}✗ Cosmos bridge not found${NC}"
        echo "Run: make && sudo make install"
        return 1
    fi
    
    sudo "$COSMOS_BRIDGE" --stream > "$LOG_DIR/bridge.log" 2>&1 &
    BRIDGE_PID=$!
    
    sleep 1
    
    if ps -p $BRIDGE_PID > /dev/null; then
        echo -e "${GREEN}✓ Bridge driver started (PID: $BRIDGE_PID)${NC}"
    else
        echo -e "${RED}✗ Bridge driver failed to start${NC}"
        echo "Check logs: cat $LOG_DIR/bridge.log"
    fi
}

monitor_devices() {
    echo -e "\n${YELLOW}Launching device monitor...${NC}"
    
    if [ -f "$COSMOS_MONITOR" ]; then
        sudo python3 "$COSMOS_MONITOR"
    elif [ -f "./cosmos_monitor.py" ]; then
        sudo python3 ./cosmos_monitor.py
    else
        echo -e "${RED}✗ Monitor script not found${NC}"
    fi
}

view_logs() {
    echo -e "\n${YELLOW}Available logs:${NC}"
    echo "1. Monado log"
    echo "2. SteamVR log"
    echo "3. Bridge driver log"
    echo "4. All logs"
    echo "5. Back to menu"
    echo ""
    read -p "Choose log to view: " log_choice
    
    case $log_choice in
        1)
            if [ -f "$LOG_DIR/monado.log" ]; then
                less "$LOG_DIR/monado.log"
            else
                echo "No Monado log found"
            fi
            ;;
        2)
            if [ -f "$LOG_DIR/steamvr.log" ]; then
                less "$LOG_DIR/steamvr.log"
            else
                echo "No SteamVR log found"
            fi
            ;;
        3)
            if [ -f "$LOG_DIR/bridge.log" ]; then
                less "$LOG_DIR/bridge.log"
            else
                echo "No bridge log found"
            fi
            ;;
        4)
            echo -e "\n${BLUE}=== Monado Log ===${NC}"
            [ -f "$LOG_DIR/monado.log" ] && tail -n 20 "$LOG_DIR/monado.log"
            echo -e "\n${BLUE}=== SteamVR Log ===${NC}"
            [ -f "$LOG_DIR/steamvr.log" ] && tail -n 20 "$LOG_DIR/steamvr.log"
            echo -e "\n${BLUE}=== Bridge Log ===${NC}"
            [ -f "$LOG_DIR/bridge.log" ] && tail -n 20 "$LOG_DIR/bridge.log"
            echo ""
            read -p "Press Enter to continue..."
            ;;
        5)
            return
            ;;
    esac
}

full_vr_session() {
    echo -e "\n${YELLOW}Starting full VR session...${NC}"
    
    if ! check_device; then
        echo -e "${RED}Cannot start VR session without detected device${NC}"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    start_monado
    sleep 2
    start_steamvr
    
    echo -e "\n${GREEN}VR session started!${NC}"
    echo -e "${YELLOW}When finished, choose 'Stop All Services' from the menu${NC}"
    read -p "Press Enter to continue..."
}

stop_all() {
    echo -e "\n${YELLOW}Stopping all VR services...${NC}"
    
    # Stop SteamVR
    killall steam 2>/dev/null || true
    killall vrserver 2>/dev/null || true
    killall vrcompositor 2>/dev/null || true
    
    # Stop Monado
    stop_monado
    
    # Stop bridge
    sudo killall cosmos_bridge 2>/dev/null || true
    
    echo -e "${GREEN}✓ All services stopped${NC}"
    sleep 1
}

print_menu() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}1.${NC} Quick Start VR Session"
    echo -e "${GREEN}2.${NC} Start Monado Only"
    echo -e "${GREEN}3.${NC} Start SteamVR"
    echo -e "${GREEN}4.${NC} Start Bridge Driver"
    echo -e "${GREEN}5.${NC} Monitor Devices"
    echo -e "${GREEN}6.${NC} Check Status"
    echo -e "${GREEN}7.${NC} View Logs"
    echo -e "${GREEN}8.${NC} Stop All Services"
    echo -e "${GREEN}9.${NC} Exit"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo ""
}

# Main loop
while true; do
    print_header
    check_services
    print_menu
    read -p "Choose an option: " choice
    
    case $choice in
        1)
            full_vr_session
            ;;
        2)
            start_monado
            read -p "Press Enter to continue..."
            ;;
        3)
            start_steamvr
            read -p "Press Enter to continue..."
            ;;
        4)
            start_bridge
            read -p "Press Enter to continue..."
            ;;
        5)
            monitor_devices
            ;;
        6)
            check_device
            read -p "Press Enter to continue..."
            ;;
        7)
            view_logs
            ;;
        8)
            stop_all
            read -p "Press Enter to continue..."
            ;;
        9)
            echo -e "\n${GREEN}Goodbye!${NC}"
            stop_all
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            sleep 1
            ;;
    esac
done
