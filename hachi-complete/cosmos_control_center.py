#!/usr/bin/env python3
"""
HTC Vive Cosmos Control Center
A graphical interface for managing your Cosmos headset on Linux
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import time
import os
import json
from pathlib import Path
from datetime import datetime

class CosmosControlCenter:
    def __init__(self, root):
        self.root = root
        self.root.title("Cosmos Control Center")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Paths
        self.config_dir = Path.home() / ".local" / "share" / "cosmos-vr"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Detect GPU and set theme colors
        self.detect_gpu()
        self.setup_theme()
        
        # Apply theme to root
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Device status
        self.device_connected = False
        self.tracking_status = "Unknown"
        self.controllers_connected = 0
        self.monado_running = False
        
        # Create UI
        self.create_menu()
        self.create_header()
        self.create_sidebar()
        self.create_main_area()
        self.create_status_bar()
        
        # Start monitoring
        self.start_monitoring()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def detect_gpu(self):
        """Detect GPU vendor for color theme"""
        gpu_file = self.config_dir / "gpu_vendor.txt"
        
        if gpu_file.exists():
            with open(gpu_file, 'r') as f:
                self.gpu_vendor = f.read().strip()
        else:
            # Try to detect
            try:
                result = subprocess.run(['lspci'], capture_output=True, text=True)
                if 'nvidia' in result.stdout.lower():
                    self.gpu_vendor = 'nvidia'
                elif 'amd' in result.stdout.lower():
                    self.gpu_vendor = 'amd'
                else:
                    self.gpu_vendor = 'unknown'
            except:
                self.gpu_vendor = 'unknown'
            
            # Save for next time
            with open(gpu_file, 'w') as f:
                f.write(self.gpu_vendor)
    
    def setup_theme(self):
        """Setup color theme based on GPU"""
        # Triple black base colors
        self.colors = {
            'bg_dark': '#0a0a0a',      # Darkest black
            'bg_medium': '#151515',     # Medium black
            'bg_light': '#1f1f1f',      # Lighter black
            'text': '#e0e0e0',          # Light gray text
            'text_dim': '#808080',      # Dimmed text
            'border': '#2a2a2a',        # Subtle borders
        }
        
        # GPU-specific accent colors
        if self.gpu_vendor == 'nvidia':
            self.colors.update({
                'accent': '#76b900',        # NVIDIA green
                'accent_hover': '#8cd400',  # Lighter green
                'accent_dark': '#5c8f00',   # Darker green
                'status_good': '#76b900',
                'status_warning': '#ffa500',
                'status_error': '#ff3333',
            })
            self.gpu_name = "NVIDIA GPU"
        elif self.gpu_vendor == 'amd':
            self.colors.update({
                'accent': '#ed1c24',        # AMD red
                'accent_hover': '#ff3333',  # Lighter red
                'accent_dark': '#c41820',   # Darker red
                'status_good': '#ed1c24',
                'status_warning': '#ffa500',
                'status_error': '#ff3333',
            })
            self.gpu_name = "AMD GPU"
        else:
            self.colors.update({
                'accent': '#0066cc',        # Blue fallback
                'accent_hover': '#0077ee',
                'accent_dark': '#0055aa',
                'status_good': '#00cc00',
                'status_warning': '#ffa500',
                'status_error': '#ff3333',
            })
            self.gpu_name = "Unknown GPU"
        
        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure notebook (tabs)
        style.configure('TNotebook', background=self.colors['bg_medium'], 
                       borderwidth=0)
        style.configure('TNotebook.Tab', background=self.colors['bg_light'],
                       foreground=self.colors['text'], padding=[20, 10],
                       borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', self.colors['accent'])],
                 foreground=[('selected', self.colors['bg_dark'])])
    
    def create_styled_button(self, parent, text, command, width=20):
        """Create a styled button with accent color"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.colors['accent'],
            fg=self.colors['bg_dark'],
            activebackground=self.colors['accent_hover'],
            activeforeground=self.colors['bg_dark'],
            relief=tk.FLAT,
            font=('Arial', 10, 'bold'),
            width=width,
            cursor='hand2',
            padx=10,
            pady=8
        )
        
        # Hover effects
        def on_enter(e):
            btn['bg'] = self.colors['accent_hover']
        
        def on_leave(e):
            btn['bg'] = self.colors['accent']
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root, bg=self.colors['bg_light'], 
                         fg=self.colors['text'], tearoff=0)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_light'],
                           fg=self.colors['text'])
        file_menu.add_command(label="Preferences", command=self.show_preferences)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_light'],
                            fg=self.colors['text'])
        tools_menu.add_command(label="Device Monitor", command=self.launch_monitor)
        tools_menu.add_command(label="Performance Monitor", command=self.launch_perf_monitor)
        tools_menu.add_command(label="View Logs", command=self.show_logs)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_light'],
                           fg=self.colors['text'])
        help_menu.add_command(label="Documentation", command=self.show_docs)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
    
    def create_header(self):
        """Create header with logo and device status"""
        header = tk.Frame(self.root, bg=self.colors['bg_light'], height=100)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        # Left side - Title
        left_frame = tk.Frame(header, bg=self.colors['bg_light'])
        left_frame.pack(side=tk.LEFT, padx=30, pady=20)
        
        title = tk.Label(
            left_frame,
            text="COSMOS",
            font=('Arial', 32, 'bold'),
            bg=self.colors['bg_light'],
            fg=self.colors['accent']
        )
        title.pack(anchor=tk.W)
        
        subtitle = tk.Label(
            left_frame,
            text="Control Center",
            font=('Arial', 12),
            bg=self.colors['bg_light'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(anchor=tk.W)
        
        # Right side - Device status
        right_frame = tk.Frame(header, bg=self.colors['bg_light'])
        right_frame.pack(side=tk.RIGHT, padx=30, pady=20)
        
        self.status_label = tk.Label(
            right_frame,
            text="● Checking device...",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_light'],
            fg=self.colors['text_dim']
        )
        self.status_label.pack(anchor=tk.E)
        
        self.gpu_label = tk.Label(
            right_frame,
            text=f"GPU: {self.gpu_name}",
            font=('Arial', 10),
            bg=self.colors['bg_light'],
            fg=self.colors['accent']
        )
        self.gpu_label.pack(anchor=tk.E)
    
    def create_sidebar(self):
        """Create sidebar navigation"""
        sidebar = tk.Frame(self.root, bg=self.colors['bg_medium'], width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Sidebar title
        sidebar_title = tk.Label(
            sidebar,
            text="NAVIGATION",
            font=('Arial', 10, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_dim'],
            pady=20
        )
        sidebar_title.pack(fill=tk.X, padx=20)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard, "📊"),
            ("Tracking", self.show_tracking, "🎯"),
            ("Controllers", self.show_controllers, "🎮"),
            ("Display", self.show_display, "🖥️"),
            ("Firmware", self.show_firmware, "⚙️"),
            ("Launch VR", self.launch_vr, "🚀"),
        ]
        
        self.nav_buttons = {}
        for text, command, icon in nav_buttons:
            btn_frame = tk.Frame(sidebar, bg=self.colors['bg_medium'])
            btn_frame.pack(fill=tk.X, padx=10, pady=2)
            
            btn = tk.Button(
                btn_frame,
                text=f"{icon}  {text}",
                command=command,
                bg=self.colors['bg_medium'],
                fg=self.colors['text'],
                activebackground=self.colors['bg_light'],
                activeforeground=self.colors['accent'],
                relief=tk.FLAT,
                font=('Arial', 11),
                anchor=tk.W,
                padx=20,
                pady=12,
                cursor='hand2'
            )
            btn.pack(fill=tk.X)
            
            def on_enter(e, b=btn):
                b['bg'] = self.colors['bg_light']
                b['fg'] = self.colors['accent']
            
            def on_leave(e, b=btn):
                b['bg'] = self.colors['bg_medium']
                b['fg'] = self.colors['text']
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            
            self.nav_buttons[text] = btn
    
    def create_main_area(self):
        """Create main content area"""
        self.main_area = tk.Frame(self.root, bg=self.colors['bg_dark'])
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        status_bar = tk.Frame(self.root, bg=self.colors['bg_light'], height=30)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        status_bar.pack_propagate(False)
        
        self.status_bar_label = tk.Label(
            status_bar,
            text="Ready",
            font=('Arial', 9),
            bg=self.colors['bg_light'],
            fg=self.colors['text_dim'],
            anchor=tk.W
        )
        self.status_bar_label.pack(side=tk.LEFT, padx=10)
        
        time_label = tk.Label(
            status_bar,
            text=datetime.now().strftime("%H:%M:%S"),
            font=('Arial', 9),
            bg=self.colors['bg_light'],
            fg=self.colors['text_dim']
        )
        time_label.pack(side=tk.RIGHT, padx=10)
        
        def update_time():
            time_label.config(text=datetime.now().strftime("%H:%M:%S"))
            self.root.after(1000, update_time)
        
        update_time()
    
    def clear_main_area(self):
        """Clear the main content area"""
        for widget in self.main_area.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show dashboard view"""
        self.clear_main_area()
        self.highlight_nav_button("Dashboard")
        
        # Container
        container = tk.Frame(self.main_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Title
        title = tk.Label(
            container,
            text="Dashboard",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Status cards row
        cards_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        cards_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Device status card
        self.create_status_card(
            cards_frame,
            "Headset Status",
            "● Checking...",
            self.colors['text_dim']
        )
        
        # Tracking card
        self.create_status_card(
            cards_frame,
            "Tracking",
            "Not configured",
            self.colors['text_dim']
        )
        
        # Controllers card
        self.create_status_card(
            cards_frame,
            "Controllers",
            "0/2 Connected",
            self.colors['text_dim']
        )
        
        # Quick actions
        actions_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        actions_frame.pack(fill=tk.BOTH, expand=True)
        
        actions_title = tk.Label(
            actions_frame,
            text="Quick Actions",
            font=('Arial', 16, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            pady=20
        )
        actions_title.pack(anchor=tk.W, padx=20)
        
        # Action buttons
        btn_container = tk.Frame(actions_frame, bg=self.colors['bg_medium'])
        btn_container.pack(padx=20, pady=(0, 20))
        
        self.create_styled_button(
            btn_container,
            "🚀 Launch VR",
            self.launch_vr,
            30
        ).pack(side=tk.LEFT, padx=5)
        
        self.create_styled_button(
            btn_container,
            "🎯 Configure Tracking",
            self.show_tracking,
            25
        ).pack(side=tk.LEFT, padx=5)
        
        self.create_styled_button(
            btn_container,
            "🎮 Pair Controllers",
            self.pair_controllers,
            25
        ).pack(side=tk.LEFT, padx=5)
        
        # System info
        info_frame = tk.Frame(actions_frame, bg=self.colors['bg_light'])
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        info_title = tk.Label(
            info_frame,
            text="System Information",
            font=('Arial', 12, 'bold'),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            pady=10
        )
        info_title.pack(anchor=tk.W, padx=10)
        
        self.system_info_text = scrolledtext.ScrolledText(
            info_frame,
            height=10,
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            font=('Courier', 9),
            relief=tk.FLAT
        )
        self.system_info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.update_system_info()
    
    def create_status_card(self, parent, title, value, color):
        """Create a status card"""
        card = tk.Frame(parent, bg=self.colors['bg_medium'], width=250)
        card.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        card_title = tk.Label(
            card,
            text=title,
            font=('Arial', 11),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_dim']
        )
        card_title.pack(pady=(15, 5))
        
        card_value = tk.Label(
            card,
            text=value,
            font=('Arial', 18, 'bold'),
            bg=self.colors['bg_medium'],
            fg=color
        )
        card_value.pack(pady=(0, 15))
        
        return card_value
    
    def show_tracking(self):
        """Show tracking configuration"""
        self.clear_main_area()
        self.highlight_nav_button("Tracking")
        
        container = tk.Frame(self.main_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        title = tk.Label(
            container,
            text="Tracking Configuration",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Tracking modes
        modes_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        modes_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            modes_frame,
            text="Tracking Mode",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            pady=15
        ).pack(anchor=tk.W, padx=20)
        
        modes = [
            ("Hybrid Mode (Camera + IMU)", "Best quality, 6DOF tracking"),
            ("IMU Only", "Most stable, 3DOF rotation only"),
            ("Auto-Configure", "Automatically choose best option")
        ]
        
        for mode, description in modes:
            mode_btn = self.create_styled_button(
                modes_frame,
                mode,
                lambda m=mode: self.configure_tracking(m),
                40
            )
            mode_btn.pack(padx=20, pady=5, anchor=tk.W)
            
            desc_label = tk.Label(
                modes_frame,
                text=description,
                font=('Arial', 9),
                bg=self.colors['bg_medium'],
                fg=self.colors['text_dim']
            )
            desc_label.pack(padx=60, pady=(0, 10), anchor=tk.W)
        
        # Calibration
        calibration_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        calibration_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(
            calibration_frame,
            text="Room Scale Calibration",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            pady=15
        ).pack(anchor=tk.W, padx=20)
        
        self.create_styled_button(
            calibration_frame,
            "Start Calibration",
            self.calibrate_room,
            40
        ).pack(padx=20, pady=(0, 15), anchor=tk.W)
    
    def show_controllers(self):
        """Show controller configuration"""
        self.clear_main_area()
        self.highlight_nav_button("Controllers")
        
        container = tk.Frame(self.main_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        title = tk.Label(
            container,
            text="Controller Management",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Controller actions
        actions_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        actions_frame.pack(fill=tk.X)
        
        tk.Label(
            actions_frame,
            text="Controller Actions",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            pady=15
        ).pack(anchor=tk.W, padx=20)
        
        btn_container = tk.Frame(actions_frame, bg=self.colors['bg_medium'])
        btn_container.pack(padx=20, pady=(0, 15))
        
        self.create_styled_button(
            btn_container,
            "Scan & Pair Controllers",
            self.pair_controllers,
            30
        ).pack(side=tk.LEFT, padx=5)
        
        self.create_styled_button(
            btn_container,
            "Test Connectivity",
            self.test_controllers,
            25
        ).pack(side=tk.LEFT, padx=5)
        
        self.create_styled_button(
            btn_container,
            "Optimize Bluetooth",
            self.optimize_bluetooth,
            25
        ).pack(side=tk.LEFT, padx=5)
    
    def show_display(self):
        """Show display configuration"""
        self.clear_main_area()
        self.highlight_nav_button("Display")
        
        container = tk.Frame(self.main_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        title = tk.Label(
            container,
            text="Display Settings",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Display optimizations
        opt_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        opt_frame.pack(fill=tk.X)
        
        tk.Label(
            opt_frame,
            text="Performance Optimization",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            pady=15
        ).pack(anchor=tk.W, padx=20)
        
        self.create_styled_button(
            opt_frame,
            "Run Full Optimization",
            self.optimize_display,
            40
        ).pack(padx=20, pady=(0, 10), anchor=tk.W)
        
        tk.Label(
            opt_frame,
            text="Target: 90Hz @ 2880x1700",
            font=('Arial', 10),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent']
        ).pack(anchor=tk.W, padx=60, pady=(0, 15))
    
    def show_firmware(self):
        """Show firmware management"""
        self.clear_main_area()
        self.highlight_nav_button("Firmware")
        
        container = tk.Frame(self.main_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        title = tk.Label(
            container,
            text="Firmware Management",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Warning
        warning_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        warning_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            warning_frame,
            text="⚠️ Firmware updates require Windows",
            font=('Arial', 12, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['status_warning'],
            pady=15
        ).pack(anchor=tk.W, padx=20)
        
        # Actions
        self.create_styled_button(
            warning_frame,
            "View Update Guide",
            self.show_firmware_guide,
            40
        ).pack(padx=20, pady=(0, 15), anchor=tk.W)
    
    def highlight_nav_button(self, button_name):
        """Highlight the active navigation button"""
        for name, btn in self.nav_buttons.items():
            if name == button_name:
                btn['bg'] = self.colors['accent']
                btn['fg'] = self.colors['bg_dark']
            else:
                btn['bg'] = self.colors['bg_medium']
                btn['fg'] = self.colors['text']
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        def monitor():
            while True:
                self.check_device_status()
                time.sleep(2)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def check_device_status(self):
        """Check if Cosmos is connected"""
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            self.device_connected = '0bb4:0313' in result.stdout
            
            # Update status label
            if self.device_connected:
                self.status_label.config(
                    text="● Headset Connected",
                    fg=self.colors['status_good']
                )
            else:
                self.status_label.config(
                    text="● Headset Disconnected",
                    fg=self.colors['status_error']
                )
            
            # Check Monado
            result = subprocess.run(['pgrep', '-x', 'monado-service'],
                                  capture_output=True)
            self.monado_running = result.returncode == 0
            
        except:
            pass
    
    def update_system_info(self):
        """Update system information display"""
        try:
            info = []
            
            # GPU info
            info.append(f"GPU: {self.gpu_name}")
            info.append(f"Theme Accent: {self.colors['accent']}")
            info.append("")
            
            # Device status
            info.append("Device Status:")
            info.append(f"  Headset: {'Connected' if self.device_connected else 'Not found'}")
            info.append(f"  Monado: {'Running' if self.monado_running else 'Stopped'}")
            info.append("")
            
            # System info
            result = subprocess.run(['uname', '-r'], capture_output=True, text=True)
            info.append(f"Kernel: {result.stdout.strip()}")
            
            self.system_info_text.delete('1.0', tk.END)
            self.system_info_text.insert('1.0', '\n'.join(info))
            
        except Exception as e:
            print(f"Error updating system info: {e}")
    
    # Action methods
    def launch_vr(self):
        """Launch VR session"""
        self.status_bar_label.config(text="Launching VR session...")
        threading.Thread(target=self._launch_vr_thread, daemon=True).start()
    
    def _launch_vr_thread(self):
        try:
            subprocess.Popen(['bash', '-c', 'vr_manager.sh'])
            self.status_bar_label.config(text="VR Manager launched")
        except:
            self.status_bar_label.config(text="Failed to launch VR")
    
    def configure_tracking(self, mode):
        """Configure tracking mode"""
        self.status_bar_label.config(text=f"Configuring tracking: {mode}")
        threading.Thread(target=lambda: self._run_tool('enhanced_tracking.py'), 
                        daemon=True).start()
    
    def pair_controllers(self):
        """Pair controllers"""
        self.status_bar_label.config(text="Launching controller manager...")
        threading.Thread(target=lambda: self._run_tool('controller_manager.py'),
                        daemon=True).start()
    
    def test_controllers(self):
        """Test controller connectivity"""
        self.status_bar_label.config(text="Testing controllers...")
        threading.Thread(target=lambda: self._run_tool('controller_manager.py'),
                        daemon=True).start()
    
    def optimize_bluetooth(self):
        """Optimize Bluetooth settings"""
        self.status_bar_label.config(text="Optimizing Bluetooth...")
        threading.Thread(target=lambda: self._run_tool('controller_manager.py'),
                        daemon=True).start()
    
    def calibrate_room(self):
        """Calibrate room scale"""
        self.status_bar_label.config(text="Starting calibration...")
        threading.Thread(target=lambda: self._run_tool('enhanced_tracking.py'),
                        daemon=True).start()
    
    def optimize_display(self):
        """Optimize display settings"""
        self.status_bar_label.config(text="Optimizing display...")
        threading.Thread(target=lambda: self._run_script('display_optimizer.sh'),
                        daemon=True).start()
    
    def show_firmware_guide(self):
        """Show firmware update guide"""
        threading.Thread(target=lambda: self._run_script('firmware_manager.sh'),
                        daemon=True).start()
    
    def launch_monitor(self):
        """Launch device monitor"""
        threading.Thread(target=lambda: self._run_tool('cosmos_monitor.py'),
                        daemon=True).start()
    
    def launch_perf_monitor(self):
        """Launch performance monitor"""
        threading.Thread(target=lambda: self._run_script('vr-perf-monitor.sh'),
                        daemon=True).start()
    
    def _run_tool(self, tool_name):
        """Run a Python tool"""
        try:
            bin_dir = Path.home() / ".local" / "bin"
            tool_path = bin_dir / tool_name
            if tool_path.exists():
                subprocess.Popen(['python3', str(tool_path)])
        except Exception as e:
            print(f"Error running {tool_name}: {e}")
    
    def _run_script(self, script_name):
        """Run a shell script"""
        try:
            bin_dir = Path.home() / ".local" / "bin"
            script_path = bin_dir / script_name
            if script_path.exists():
                subprocess.Popen(['bash', str(script_path)])
        except Exception as e:
            print(f"Error running {script_name}: {e}")
    
    def show_logs(self):
        """Show log viewer"""
        messagebox.showinfo("Logs", "Log viewer not yet implemented")
    
    def show_docs(self):
        """Show documentation"""
        messagebox.showinfo("Documentation", 
                          "Documentation viewer not yet implemented")
    
    def show_preferences(self):
        """Show preferences dialog"""
        messagebox.showinfo("Preferences", 
                          "Preferences dialog not yet implemented")
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""Cosmos Control Center v1.0

HTC Vive Cosmos management tool for Linux

GPU: {self.gpu_name}
Theme: Triple Black with {self.gpu_vendor.upper()} accents

Created for Bazzite Linux
"""
        messagebox.showinfo("About", about_text)

def main():
    root = tk.Tk()
    app = CosmosControlCenter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
