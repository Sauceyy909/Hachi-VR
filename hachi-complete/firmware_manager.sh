#!/bin/bash

# HTC Vive Cosmos Firmware Manager for Linux
# Handles firmware backup, restore, and update guidance

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

FIRMWARE_DIR="$HOME/.local/share/cosmos-firmware"
BACKUP_DIR="$FIRMWARE_DIR/backups"
DEVICE_INFO_FILE="$FIRMWARE_DIR/device_info.json"

mkdir -p "$FIRMWARE_DIR" "$BACKUP_DIR"

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  HTC Vive Cosmos Firmware Management Tool     ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Check device connection
check_device() {
    echo -e "${YELLOW}Checking for Cosmos device...${NC}"
    
    if lsusb | grep -q "0bb4:0313"; then
        echo -e "${GREEN}✓ Cosmos headset detected${NC}"
        DEVICE_CONNECTED=true
        
        # Get device info
        DEVICE_INFO=$(lsusb -d 0bb4:0313 -v 2>/dev/null)
        return 0
    else
        echo -e "${RED}✗ Cosmos headset not detected${NC}"
        DEVICE_CONNECTED=false
        return 1
    fi
}

# Read firmware version (if possible)
read_firmware_version() {
    echo -e "\n${YELLOW}Attempting to read firmware version...${NC}"
    
    if [ "$DEVICE_CONNECTED" != true ]; then
        echo -e "${RED}Device not connected${NC}"
        return 1
    fi
    
    # This is a placeholder - actual firmware reading would require
    # reverse-engineered protocol knowledge
    echo -e "${YELLOW}Note: Direct firmware reading requires protocol knowledge${NC}"
    echo -e "  Firmware version info may be available in:"
    echo -e "  - Windows Registry (if dual-booting)"
    echo -e "  - Viveport software logs"
    echo -e "  - HTC Vive Console application"
    
    # Save basic device info
    cat > "$DEVICE_INFO_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "device_id": "$(lsusb | grep 0bb4:0313 | cut -d: -f1)",
  "usb_bus": "$(lsusb | grep 0bb4:0313 | awk '{print $2}')",
  "usb_device": "$(lsusb | grep 0bb4:0313 | awk '{print $4}' | tr -d ':')",
  "linux_kernel": "$(uname -r)",
  "firmware_version": "unknown"
}
EOF
    
    echo -e "${GREEN}✓ Device info saved to $DEVICE_INFO_FILE${NC}"
}

# Import firmware from Windows
import_windows_firmware() {
    echo -e "\n${CYAN}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  Import Firmware from Windows Installation     ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo "This tool can import firmware files from a Windows installation."
    echo ""
    echo "Typical Windows firmware locations:"
    echo "  C:\\Program Files\\VIVE\\VivePort\\Firmware\\"
    echo "  C:\\Program Files (x86)\\HTC\\Vive Software\\Firmware\\"
    echo "  C:\\ProgramData\\HTC\\ViveSoftware\\Firmware\\"
    echo ""
    
    read -p "Do you have access to a Windows partition? (y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Firmware import cancelled"
        return
    fi
    
    echo ""
    echo "Available partitions:"
    lsblk -o NAME,FSTYPE,SIZE,LABEL,MOUNTPOINT | grep -E "ntfs|NTFS"
    echo ""
    
    read -p "Enter Windows partition (e.g., /dev/sda1): " WIN_PARTITION
    
    if [ -z "$WIN_PARTITION" ]; then
        echo "No partition specified"
        return
    fi
    
    # Mount Windows partition
    MOUNT_POINT="/mnt/windows-firmware"
    sudo mkdir -p "$MOUNT_POINT"
    
    echo "Mounting $WIN_PARTITION..."
    if sudo mount -o ro "$WIN_PARTITION" "$MOUNT_POINT" 2>/dev/null; then
        echo -e "${GREEN}✓ Partition mounted${NC}"
        
        # Search for firmware files
        echo "Searching for firmware files..."
        
        FIRMWARE_PATHS=(
            "$MOUNT_POINT/Program Files/VIVE/VivePort/Firmware"
            "$MOUNT_POINT/Program Files (x86)/HTC/Vive Software/Firmware"
            "$MOUNT_POINT/ProgramData/HTC/ViveSoftware/Firmware"
        )
        
        FOUND=false
        for path in "${FIRMWARE_PATHS[@]}"; do
            if [ -d "$path" ]; then
                echo -e "${GREEN}✓ Found firmware directory: $path${NC}"
                
                # Copy firmware files
                BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
                BACKUP_PATH="$BACKUP_DIR/windows_import_$BACKUP_TIMESTAMP"
                mkdir -p "$BACKUP_PATH"
                
                echo "Copying firmware files..."
                cp -r "$path"/* "$BACKUP_PATH/" 2>/dev/null || true
                
                if [ "$(ls -A $BACKUP_PATH)" ]; then
                    echo -e "${GREEN}✓ Firmware files imported to $BACKUP_PATH${NC}"
                    
                    # List imported files
                    echo ""
                    echo "Imported files:"
                    ls -lh "$BACKUP_PATH"
                    
                    FOUND=true
                fi
            fi
        done
        
        if [ "$FOUND" = false ]; then
            echo -e "${YELLOW}⚠ No firmware files found in standard locations${NC}"
            echo "You may need to manually copy firmware files"
        fi
        
        # Unmount
        sudo umount "$MOUNT_POINT"
        echo "Partition unmounted"
    else
        echo -e "${RED}✗ Failed to mount partition${NC}"
        echo "Make sure you have ntfs-3g installed:"
        echo "  rpm-ostree install ntfs-3g"
    fi
}

# Create manual firmware backup
create_firmware_backup() {
    echo -e "\n${CYAN}Creating firmware backup...${NC}"
    
    if [ "$DEVICE_CONNECTED" != true ]; then
        echo -e "${RED}Device not connected. Cannot create backup.${NC}"
        return 1
    fi
    
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="$BACKUP_DIR/backup_$BACKUP_TIMESTAMP"
    mkdir -p "$BACKUP_PATH"
    
    echo "Backup location: $BACKUP_PATH"
    
    # Save device information
    cat > "$BACKUP_PATH/device_info.txt" << EOF
Cosmos Firmware Backup
Created: $(date)
Host: $(hostname)
Kernel: $(uname -r)

USB Device Info:
$(lsusb -d 0bb4:0313 -v 2>/dev/null || echo "Could not read detailed info")
EOF
    
    # Note: Actual firmware extraction would require protocol knowledge
    echo -e "${YELLOW}Note: Full firmware extraction not yet implemented${NC}"
    echo "  This backup contains device identification data only"
    echo "  For complete firmware backup, use Windows tools"
    
    echo -e "${GREEN}✓ Device info backed up to $BACKUP_PATH${NC}"
    
    # Create backup manifest
    cat > "$BACKUP_PATH/manifest.json" << EOF
{
  "backup_type": "device_info",
  "timestamp": "$(date -Iseconds)",
  "device": "HTC Vive Cosmos",
  "usb_id": "0bb4:0313",
  "note": "Full firmware extraction requires Windows tools"
}
EOF
}

# List available backups
list_backups() {
    echo -e "\n${CYAN}Available Firmware Backups:${NC}"
    echo ""
    
    if [ ! "$(ls -A $BACKUP_DIR 2>/dev/null)" ]; then
        echo "No backups found"
        return
    fi
    
    for backup in "$BACKUP_DIR"/*; do
        if [ -d "$backup" ]; then
            BACKUP_NAME=$(basename "$backup")
            BACKUP_SIZE=$(du -sh "$backup" | cut -f1)
            
            echo "Backup: $BACKUP_NAME"
            echo "  Size: $BACKUP_SIZE"
            
            if [ -f "$backup/manifest.json" ]; then
                TIMESTAMP=$(grep timestamp "$backup/manifest.json" | cut -d'"' -f4)
                echo "  Date: $TIMESTAMP"
            fi
            
            echo ""
        fi
    done
}

# Firmware update guidance
firmware_update_guide() {
    echo -e "\n${CYAN}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║       Firmware Update Guide for Cosmos         ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${YELLOW}IMPORTANT: Firmware updates REQUIRE Windows${NC}"
    echo ""
    echo "HTC does not provide firmware update tools for Linux."
    echo "You MUST use Windows to update Cosmos firmware."
    echo ""
    echo -e "${BLUE}══ METHOD 1: Dual Boot (Recommended) ══${NC}"
    echo "1. Install Windows on a separate partition"
    echo "2. Download HTC Vive Console from HTC"
    echo "3. Connect Cosmos and run firmware update"
    echo "4. Reboot to Linux"
    echo ""
    echo -e "${BLUE}══ METHOD 2: Virtual Machine ══${NC}"
    echo "Requirements:"
    echo "  - Windows 10/11 VM"
    echo "  - USB passthrough support (IOMMU/VT-d)"
    echo "  - VMware or VirtualBox with USB 3.0 support"
    echo ""
    echo "Steps:"
    echo "1. Create Windows 10/11 VM"
    echo "2. Enable USB passthrough for Cosmos (0bb4:0313)"
    echo "3. Install HTC Vive Console in VM"
    echo "4. Update firmware through VM"
    echo ""
    echo -e "${BLUE}══ METHOD 3: Wine/Proton (Experimental) ══${NC}"
    echo "⚠ Not recommended - USB access through Wine is unreliable"
    echo ""
    echo -e "${YELLOW}HTC Vive Console Download:${NC}"
    echo "https://www.vive.com/us/setup/cosmos/"
    echo ""
    echo -e "${YELLOW}Firmware Update Best Practices:${NC}"
    echo "  ✓ Keep headset plugged in and powered during update"
    echo "  ✓ Don't interrupt the update process"
    echo "  ✓ Update firmware before using on Linux"
    echo "  ✓ Check HTC support site for latest version"
    echo ""
}

# Setup Windows VM for firmware updates
setup_vm_guide() {
    echo -e "\n${CYAN}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║    Windows VM Setup for Firmware Updates       ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${BLUE}══ OPTION A: QEMU/KVM (Recommended) ══${NC}"
    echo ""
    echo "1. Install required packages:"
    echo "   rpm-ostree install qemu-kvm libvirt virt-manager"
    echo ""
    echo "2. Enable IOMMU in BIOS"
    echo "   Intel: Enable VT-d"
    echo "   AMD: Enable AMD-Vi"
    echo ""
    echo "3. Add kernel parameters:"
    echo "   Edit: /etc/default/grub"
    echo "   Add to GRUB_CMDLINE_LINUX:"
    echo "   Intel: intel_iommu=on iommu=pt"
    echo "   AMD: amd_iommu=on iommu=pt"
    echo ""
    echo "4. Create Windows 10 VM:"
    echo "   - Use virt-manager"
    echo "   - Allocate 4GB RAM minimum"
    echo "   - 40GB disk minimum"
    echo "   - Add USB Host Device (0bb4:0313)"
    echo ""
    echo -e "${BLUE}══ OPTION B: VirtualBox ══${NC}"
    echo ""
    echo "1. Install VirtualBox:"
    echo "   Download from: https://www.virtualbox.org/"
    echo ""
    echo "2. Install Extension Pack (required for USB 3.0)"
    echo ""
    echo "3. Create Windows 10 VM:"
    echo "   - Enable USB 3.0 controller"
    echo "   - Add USB filter for Cosmos (0bb4:0313)"
    echo ""
    echo "4. Install guest additions"
    echo ""
    echo -e "${YELLOW}Testing USB Passthrough:${NC}"
    echo "  1. Start VM"
    echo "  2. Connect Cosmos"
    echo "  3. Check Device Manager in Windows"
    echo "  4. Cosmos should appear under USB devices"
    echo ""
    
    read -p "Would you like to save this guide? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        GUIDE_FILE="$FIRMWARE_DIR/windows_vm_setup_guide.txt"
        cat > "$GUIDE_FILE" << 'EOF'
Windows VM Setup Guide for Cosmos Firmware Updates
===================================================

QEMU/KVM Method:
1. Install: rpm-ostree install qemu-kvm libvirt virt-manager
2. Enable IOMMU in BIOS (VT-d for Intel, AMD-Vi for AMD)
3. Add kernel parameters in /etc/default/grub:
   intel_iommu=on iommu=pt (Intel)
   amd_iommu=on iommu=pt (AMD)
4. Update grub: sudo grub2-mkconfig -o /boot/grub2/grub.cfg
5. Reboot
6. Create Windows 10 VM with USB passthrough (0bb4:0313)

VirtualBox Method:
1. Install VirtualBox + Extension Pack
2. Create Windows 10 VM
3. Enable USB 3.0 controller
4. Add USB filter: 0bb4:0313
5. Install Windows and HTC Vive Console
6. Update Cosmos firmware

HTC Vive Console: https://www.vive.com/us/setup/cosmos/
EOF
        echo -e "${GREEN}✓ Guide saved to $GUIDE_FILE${NC}"
    fi
}

# Check firmware version from Windows registry (if dual-boot)
check_windows_firmware_version() {
    echo -e "\n${YELLOW}Checking for Windows firmware version info...${NC}"
    
    echo "Searching for mounted Windows partitions..."
    WIN_MOUNTS=$(mount | grep ntfs | cut -d' ' -f3)
    
    if [ -z "$WIN_MOUNTS" ]; then
        echo "No Windows partitions currently mounted"
        return
    fi
    
    for mount in $WIN_MOUNTS; do
        REG_FILE="$mount/Windows/System32/config/SOFTWARE"
        if [ -f "$REG_FILE" ]; then
            echo "Found Windows registry at: $mount"
            echo "Note: Reading Windows registry from Linux requires 'chntpw'"
            
            if command -v chntpw &> /dev/null; then
                echo "Attempting to read firmware version..."
                # This would require knowledge of exact registry keys
                echo "(Registry reading not yet implemented)"
            else
                echo "Install chntpw to read registry: rpm-ostree install chntpw"
            fi
        fi
    done
}

# Main menu
show_menu() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
    echo -e "${GREEN}1.${NC} Check Device & Firmware Version"
    echo -e "${GREEN}2.${NC} Import Firmware from Windows"
    echo -e "${GREEN}3.${NC} Create Firmware Backup"
    echo -e "${GREEN}4.${NC} List Firmware Backups"
    echo -e "${GREEN}5.${NC} Firmware Update Guide"
    echo -e "${GREEN}6.${NC} Windows VM Setup Guide"
    echo -e "${GREEN}7.${NC} Exit"
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
}

# Main program
main() {
    print_header
    
    while true; do
        show_menu
        read -p "Enter choice: " choice
        
        case $choice in
            1)
                check_device
                read_firmware_version
                read -p "Press Enter to continue..."
                ;;
            2)
                import_windows_firmware
                read -p "Press Enter to continue..."
                ;;
            3)
                check_device
                create_firmware_backup
                read -p "Press Enter to continue..."
                ;;
            4)
                list_backups
                read -p "Press Enter to continue..."
                ;;
            5)
                firmware_update_guide
                read -p "Press Enter to continue..."
                ;;
            6)
                setup_vm_guide
                ;;
            7)
                echo "Goodbye!"
                exit 0
                ;;
            *)
                echo "Invalid choice"
                sleep 1
                ;;
        esac
        
        clear
        print_header
    done
}

main
