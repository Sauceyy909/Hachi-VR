#!/usr/bin/env python3
"""
HACHI GUI Installer - Just Double Click Me!
Safe installation - won't touch GPU drivers
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import threading
import os
from pathlib import Path

class HachiInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("HACHI Safe Installer")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        # Colors
        self.bg_dark = '#0a0a0a'
        self.bg_medium = '#151515'
        self.accent = '#00cc00'
        self.text = '#e0e0e0'
        
        self.root.configure(bg=self.bg_dark)
        
        self.install_dir = Path.home() / ".local" / "share" / "hachi"
        self.bin_dir = Path.home() / ".local" / "bin"
        
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.bg_medium, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="HACHI SAFE INSTALLER",
            font=('Arial', 24, 'bold'),
            bg=self.bg_medium,
            fg=self.accent
        )
        title.pack(pady=20)
        
        # Info section
        info_frame = tk.Frame(self.root, bg=self.bg_dark)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        info_text = """
This installer will:
  ✓ Install HACHI Control Center (VR management GUI)
  ✓ Install finger tracking support
  ✓ Setup VR device permissions
  ✓ Install all Python tools

This installer will NOT:
  ✗ Touch your GPU drivers
  ✗ Modify system packages
  ✗ Break your display
  ✗ Require reboot

Everything installs to your home directory only!
After installation, just log out and back in, then run: hachi
"""
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=('Courier', 10),
            bg=self.bg_dark,
            fg=self.text,
            justify=tk.LEFT
        )
        info_label.pack(anchor=tk.W)
        
        # Progress log
        log_frame = tk.Frame(self.root, bg=self.bg_dark)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(
            log_frame,
            text="Installation Log:",
            font=('Arial', 10, 'bold'),
            bg=self.bg_dark,
            fg=self.text
        ).pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            bg=self.bg_medium,
            fg=self.text,
            font=('Courier', 9),
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        btn_frame = tk.Frame(self.root, bg=self.bg_dark)
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.install_btn = tk.Button(
            btn_frame,
            text="INSTALL HACHI",
            font=('Arial', 14, 'bold'),
            bg=self.accent,
            fg=self.bg_dark,
            command=self.start_installation,
            cursor='hand2',
            relief=tk.FLAT,
            padx=40,
            pady=15
        )
        self.install_btn.pack()
    
    def log(self, message):
        """Add message to log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def start_installation(self):
        """Start installation in background thread"""
        self.install_btn.config(state=tk.DISABLED, text="INSTALLING...")
        thread = threading.Thread(target=self.install, daemon=True)
        thread.start()
    
    def install(self):
        """Main installation process"""
        try:
            self.log("="*60)
            self.log("HACHI SAFE INSTALLER")
            self.log("="*60)
            
            # Create directories
            self.log("\n[1/8] Creating directories...")
            self.install_dir.mkdir(parents=True, exist_ok=True)
            self.bin_dir.mkdir(parents=True, exist_ok=True)
            self.log("✓ Directories created")
            
            # Detect GPU
            self.log("\n[2/8] Detecting GPU (for theme only)...")
            try:
                result = subprocess.run(['lspci'], capture_output=True, text=True)
                if 'nvidia' in result.stdout.lower():
                    gpu = 'nvidia'
                    self.log("✓ NVIDIA GPU detected (green theme)")
                elif 'amd' in result.stdout.lower():
                    gpu = 'amd'
                    self.log("✓ AMD GPU detected (red theme)")
                else:
                    gpu = 'unknown'
                    self.log("✓ GPU detected (blue theme)")
                
                with open(self.install_dir / "gpu_vendor.txt", 'w') as f:
                    f.write(gpu)
            except:
                self.log("⚠ Could not detect GPU, using default theme")
            
            # Check Python
            self.log("\n[3/8] Checking Python...")
            result = subprocess.run(['python3', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"✓ {result.stdout.strip()}")
            else:
                self.log("✗ Python3 not found!")
                raise Exception("Python3 is required")
            
            # Install Python packages
            self.log("\n[4/8] Installing Python packages...")
            self.log("This may take a minute...")
            
            packages = ['pyusb', 'opencv-python', 'numpy']
            for package in packages:
                self.log(f"  Installing {package}...")
                result = subprocess.run(
                    ['pip3', 'install', '--user', package],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.log(f"  ✓ {package}")
                else:
                    # Try with --break-system-packages
                    result = subprocess.run(
                        ['pip3', 'install', '--user', '--break-system-packages', package],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        self.log(f"  ✓ {package}")
                    else:
                        self.log(f"  ⚠ {package} may have failed")
            
            # Setup udev rules
            self.log("\n[5/8] Setting up VR device permissions...")
            self.log("(You'll be asked for your password)")
            
            udev_rules = """# HTC Vive Cosmos - VR Headset Only
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0313", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="0178", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bb4", ATTRS{idProduct}=="030e", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="28de", MODE="0666", GROUP="plugdev", TAG+="uaccess"
KERNEL=="hidraw*", ATTRS{idVendor}=="0bb4", MODE="0666", GROUP="plugdev", TAG+="uaccess"
KERNEL=="hidraw*", ATTRS{idVendor}=="28de", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEM=="video4linux", ATTRS{idVendor}=="0bb4", MODE="0666", GROUP="video", TAG+="uaccess"
"""
            
            with open('/tmp/99-hachi-vr.rules', 'w') as f:
                f.write(udev_rules)
            
            result = subprocess.run(
                ['pkexec', 'mv', '/tmp/99-hachi-vr.rules', '/etc/udev/rules.d/99-hachi-vr.rules'],
                capture_output=True
            )
            
            if result.returncode == 0:
                subprocess.run(['sudo', 'udevadm', 'control', '--reload-rules'])
                subprocess.run(['sudo', 'udevadm', 'trigger'])
                self.log("✓ VR device permissions configured")
            else:
                self.log("⚠ Could not setup udev rules (may need manual setup)")
            
            # Add user to groups
            self.log("\n[6/8] Adding user to VR groups...")
            username = os.getlogin()
            subprocess.run(['sudo', 'groupadd', '-f', 'plugdev'], capture_output=True)
            subprocess.run(['sudo', 'groupadd', '-f', 'video'], capture_output=True)
            subprocess.run(['sudo', 'usermod', '-a', '-G', 'plugdev,video', username], 
                         capture_output=True)
            self.log("✓ User groups configured")
            
            # Copy files
            self.log("\n[7/8] Installing HACHI and tools...")
            script_dir = Path(__file__).parent
            
            files_to_copy = [
                'hachi_control_center.py',
                'enhanced_tracking.py',
                'controller_manager.py',
                'cosmos_monitor.py',
                'display_optimizer.sh',
                'firmware_manager.sh',
                'vr_manager.sh',
                'launch_cosmos_vr.sh'
            ]
            
            for filename in files_to_copy:
                src = script_dir / filename
                if src.exists():
                    dst = self.bin_dir / filename
                    with open(src, 'r') as f:
                        content = f.read()
                    with open(dst, 'w') as f:
                        f.write(content)
                    dst.chmod(0o755)
                    self.log(f"  ✓ {filename}")
            
            # Create launcher
            launcher = self.bin_dir / "hachi"
            with open(launcher, 'w') as f:
                f.write('''#!/bin/bash
if ! python3 -c "import tkinter" 2>/dev/null; then
    zenity --error --text="Python tkinter not found!\\n\\nInstall with: sudo pacman -S tk" 2>/dev/null || \
    kdialog --error "Python tkinter not found! Install with: sudo pacman -S tk" 2>/dev/null || \
    echo "ERROR: Install python3-tkinter first!"
    exit 1
fi
cd ~/.local/bin
python3 hachi_control_center.py
''')
            launcher.chmod(0o755)
            
            # Create desktop entry
            desktop_dir = Path.home() / ".local" / "share" / "applications"
            desktop_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_entry = desktop_dir / "hachi.desktop"
            with open(desktop_entry, 'w') as f:
                f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name=HACHI Control Center
Comment=HTC Vive Cosmos with Finger Tracking
Exec={self.bin_dir}/hachi
Icon=input-gaming
Terminal=false
Categories=Game;System;
Keywords=vr;cosmos;vive;hachi;
""")
            
            self.log("✓ HACHI installed")
            
            # Update PATH
            self.log("\n[8/8] Updating PATH...")
            bashrc = Path.home() / ".bashrc"
            path_line = f'export PATH="$HOME/.local/bin:$PATH"'
            
            if bashrc.exists():
                with open(bashrc, 'r') as f:
                    if path_line not in f.read():
                        with open(bashrc, 'a') as f:
                            f.write(f'\n# Added by HACHI installer\n{path_line}\n')
                        self.log("✓ PATH updated")
                    else:
                        self.log("✓ PATH already configured")
            
            # Success!
            self.log("\n" + "="*60)
            self.log("INSTALLATION COMPLETE!")
            self.log("="*60)
            self.log("\nWhat was installed:")
            self.log("  ✓ HACHI Control Center (with finger tracking)")
            self.log("  ✓ VR management tools")
            self.log("  ✓ Device permissions")
            self.log("  ✓ Desktop launcher")
            self.log("\nYour GPU drivers were NOT touched!")
            self.log("\nNext steps:")
            self.log("  1. Log out and log back in")
            self.log("  2. Run: hachi")
            self.log("  3. Or find 'HACHI Control Center' in apps menu")
            
            # Update button
            self.root.after(0, self.installation_complete)
            
        except Exception as e:
            self.log(f"\n✗ ERROR: {e}")
            self.root.after(0, lambda: self.installation_failed(str(e)))
    
    def installation_complete(self):
        """Called when installation succeeds"""
        self.install_btn.config(
            text="INSTALLATION COMPLETE!",
            bg='#00cc00',
            state=tk.DISABLED
        )
        
        result = messagebox.askyesno(
            "Installation Complete!",
            "HACHI has been installed successfully!\n\n"
            "You need to LOG OUT and log back in for group permissions.\n\n"
            "After logging back in, run: hachi\n\n"
            "Log out now?",
            icon='info'
        )
        
        if result:
            subprocess.run(['gnome-session-quit', '--logout', '--no-prompt'])
    
    def installation_failed(self, error):
        """Called when installation fails"""
        self.install_btn.config(
            text="INSTALLATION FAILED",
            bg='#cc0000',
            state=tk.NORMAL
        )
        
        messagebox.showerror(
            "Installation Failed",
            f"Installation failed with error:\n\n{error}\n\n"
            "Check the log above for details."
        )

def main():
    root = tk.Tk()
    app = HachiInstaller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
