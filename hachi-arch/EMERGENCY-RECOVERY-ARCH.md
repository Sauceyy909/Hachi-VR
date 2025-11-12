# 🆘 HACHI Emergency Recovery - Arch/Garuda Linux

## Quick Recovery Guide for Arch-Based Systems

---

## 🚨 Complete Removal (If Needed)

### Remove HACHI Completely

```bash
# Remove all HACHI files
rm -rf ~/.local/share/hachi
rm -rf ~/.local/bin/hachi*
rm -rf ~/.local/bin/*_manager.py
rm -rf ~/.local/bin/enhanced_tracking_arch.py
rm ~/.local/share/applications/hachi.desktop

# Remove udev rules
sudo rm /etc/udev/rules.d/99-hachi*.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

**Done!** HACHI is completely removed. Your system is clean.

---

## 🔄 Reinstall HACHI

### Clean Reinstall

```bash
# Navigate to HACHI directory
cd hachi-arch

# Run installer
./hachi_safe_installer_arch.sh

# Log out and back in
logout
```

---

## 🛠️ Fix Common Issues

### Issue 1: HACHI Won't Open

**Symptom:** Command `hachi` does nothing or shows error

**Fix:**
```bash
# Install tkinter
sudo pacman -S tk

# Test tkinter
python3 -c "import tkinter"

# Should show no error

# Try HACHI again
hachi
```

### Issue 2: Missing Python Packages

**Symptom:** Error about cv2, numpy, or usb

**Fix:**
```bash
# Install packages
pip install --user opencv-python numpy pyusb

# Or with break-system-packages flag
pip install --user --break-system-packages opencv-python numpy pyusb

# Test
python3 -c "import cv2, numpy, usb"
```

### Issue 3: Permission Denied

**Symptom:** Can't run hachi command

**Fix:**
```bash
# Make executable
chmod +x ~/.local/bin/hachi
chmod +x ~/.local/bin/hachi_control_center.py

# Add to PATH (if needed)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Issue 4: PATH Not Set

**Symptom:** Command 'hachi' not found

**Fix:**
```bash
# Run directly
~/.local/bin/hachi

# Or add to PATH permanently
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# For Zsh users
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Issue 5: Headset Not Detected

**Symptom:** HACHI shows "Headset Not Connected"

**Fix:**
```bash
# Check USB connection
lsusb | grep 0bb4
# Should show: ID 0bb4:0313 HTC Corp. Vive Cosmos

# Check udev rules
ls /etc/udev/rules.d/*hachi*

# Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Check groups
groups | grep plugdev

# If not in group
sudo usermod -a -G plugdev,video $USER
# Then LOG OUT and back in
```

---

## 🔍 Arch-Specific Diagnostics

### System Update Issues

**After pacman -Syu, HACHI breaks:**

```bash
# Reinstall Python packages
pip install --user --upgrade opencv-python numpy pyusb

# Or reinstall HACHI
cd hachi-arch
./hachi_safe_installer_arch.sh
```

### Python Version Changes

**Arch upgraded Python:**

```bash
# Rebuild virtual environment
rm -rf ~/.local/share/hachi/venv
cd hachi-arch
./hachi_safe_installer_arch.sh
```

### AUR Package Conflicts

**Something from AUR conflicts:**

HACHI only uses user space, so conflicts are rare. If it happens:

```bash
# Check what's conflicting
pacman -Qo /usr/local/bin/hachi 2>/dev/null

# Remove HACHI
rm -rf ~/.local/bin/hachi*

# Reinstall
./hachi_safe_installer_arch.sh
```

---

## 🖥️ GPU Driver Issues (Arch)

### NVIDIA on Arch

**Check NVIDIA drivers:**
```bash
# Check installation
pacman -Q nvidia

# Test drivers
nvidia-smi

# If broken, reinstall
sudo pacman -S nvidia nvidia-utils
```

**DKMS users:**
```bash
# Reinstall DKMS package
sudo pacman -S nvidia-dkms
sudo mkinitcpio -P
sudo reboot
```

### AMD on Arch

**Check Mesa:**
```bash
# Check installation
pacman -Q mesa

# Test
glxinfo | grep "OpenGL renderer"

# If issues
sudo pacman -S mesa vulkan-radeon lib32-vulkan-radeon
```

### Intel on Arch

**Check drivers:**
```bash
# Install Intel drivers
sudo pacman -S mesa vulkan-intel lib32-vulkan-intel

# Test
glxinfo | grep "OpenGL"
```

**HACHI NEVER touches GPU drivers!** If GPU issues occur, they're unrelated to HACHI.

---

## 📊 Complete Diagnostic

### Run Full Check

```bash
#!/bin/bash
echo "=== HACHI Diagnostic (Arch) ==="
echo ""

echo "System:"
echo "  Distribution: $(cat /etc/os-release | grep '^NAME=' | cut -d'"' -f2)"
echo "  Kernel: $(uname -r)"
echo ""

echo "Python:"
echo "  Version: $(python3 --version)"
python3 -c "import tkinter" 2>/dev/null && echo "  ✓ tkinter OK" || echo "  ✗ tkinter MISSING"
python3 -c "import cv2" 2>/dev/null && echo "  ✓ opencv OK" || echo "  ✗ opencv MISSING"
python3 -c "import numpy" 2>/dev/null && echo "  ✓ numpy OK" || echo "  ✗ numpy MISSING"
python3 -c "import usb" 2>/dev/null && echo "  ✓ pyusb OK" || echo "  ✗ pyusb MISSING"
echo ""

echo "GPU:"
lspci | grep -i 'vga\|3d'
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null && echo "  ✓ NVIDIA OK"
fi
echo ""

echo "Headset:"
lsusb | grep 0bb4 && echo "  ✓ Cosmos Connected" || echo "  ✗ Cosmos Not Found"
echo ""

echo "HACHI:"
ls ~/.local/bin/hachi* &> /dev/null && echo "  ✓ Installed" || echo "  ✗ Not Installed"
which hachi &> /dev/null && echo "  ✓ In PATH" || echo "  ✗ Not in PATH"
echo ""

echo "Permissions:"
groups | grep plugdev &> /dev/null && echo "  ✓ In plugdev" || echo "  ✗ Not in plugdev"
groups | grep video &> /dev/null && echo "  ✓ In video" || echo "  ✗ Not in video"
echo ""

echo "PATH:"
echo $PATH | grep ".local/bin" &> /dev/null && echo "  ✓ PATH OK" || echo "  ✗ PATH missing ~/.local/bin"
```

Save as `diagnostic-arch.sh` and run:
```bash
bash diagnostic-arch.sh
```

---

## 🔄 Garuda-Specific Recovery

### Garuda Assistant

**Use Garuda's tools:**
```bash
# Update system
sudo garuda-update

# Fix common issues
sudo garuda-assistant
```

### Garuda Gaming Fixes

**Gaming setup reset:**
```bash
# Reinstall gaming tools
sudo pacman -S --needed gamemode lib32-gamemode

# Reapply optimizations
sudo garuda-gamer
```

---

## 📦 Manjaro-Specific Recovery

### Manjaro Settings Manager

**Use GUI tools:**
```bash
# Open Manjaro Settings
manjaro-settings-manager

# Check:
# - Kernel
# - Hardware
# - User accounts (groups)
```

### AUR Helper Issues

**If AUR helper breaks:**
```bash
# Rebuild yay (if using yay)
cd /tmp
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si
```

---

## 🆘 Nuclear Option (Complete Reset)

### If Everything Fails

**1. Remove HACHI completely:**
```bash
rm -rf ~/.local/share/hachi
rm -rf ~/.local/bin/hachi*
rm ~/.local/share/applications/hachi.desktop
sudo rm /etc/udev/rules.d/99-hachi*.rules
```

**2. Update system:**
```bash
sudo pacman -Syu
```

**3. Install fresh Python:**
```bash
sudo pacman -S python python-pip tk
```

**4. Clean pip cache:**
```bash
rm -rf ~/.cache/pip
```

**5. Reinstall HACHI:**
```bash
cd hachi-arch
./hachi_safe_installer_arch.sh
```

**6. Reboot:**
```bash
sudo reboot
```

---

## 🎯 Prevention Tips

### Keep System Updated

```bash
# Update weekly
sudo pacman -Syu

# Check for orphans
sudo pacman -Qtdq | sudo pacman -Rns -

# Clear cache occasionally
sudo pacman -Sc
```

### Backup Configuration

```bash
# Backup HACHI config
cp -r ~/.local/share/hachi ~/hachi-backup

# Restore if needed
cp -r ~/hachi-backup ~/.local/share/hachi
```

### Before Major Updates

```bash
# Before kernel updates
sudo pacman -Syu
# Test HACHI
hachi
# If broken, reinstall Python packages
pip install --user --upgrade opencv-python numpy pyusb
```

---

## 📞 Getting Help

### Check Logs

```bash
# Installation log
cat ~/.local/share/hachi/install.log

# System logs
journalctl -b | grep -i hachi

# Pacman logs
cat /var/log/pacman.log | grep -i python
```

### Arch Resources

- **Arch Wiki:** https://wiki.archlinux.org/
- **Forums:** https://bbs.archlinux.org/
- **VR on Arch:** https://wiki.archlinux.org/title/Virtual_reality

### Garuda Resources

- **Forum:** https://forum.garudalinux.org/
- **Telegram:** https://t.me/garudalinux
- **Discord:** Garuda Linux Community

---

## ✅ Recovery Checklist

- [ ] Tried reinstalling: `./hachi_safe_installer_arch.sh`
- [ ] Installed tk: `sudo pacman -S tk`
- [ ] Updated system: `sudo pacman -Syu`
- [ ] Checked groups: `groups | grep plugdev`
- [ ] Logged out and back in
- [ ] Checked headset: `lsusb | grep 0bb4`
- [ ] Ran diagnostic script
- [ ] Checked logs: `cat ~/.local/share/hachi/install.log`

---

## 🎉 Success!

Once HACHI is working:

```bash
hachi  # Launch it!
```

**Remember:** HACHI is 100% user-space. It can't break your system!

---

Made with ❤️ for Arch/Garuda Linux

**Your system is safe. HACHI never touches critical components!**
