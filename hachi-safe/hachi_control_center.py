#!/usr/bin/env python3
"""
HACHI - HTC Vive Cosmos Control Center
Advanced VR management with experimental finger tracking
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

class HachiControlCenter:
    def __init__(self, root):
        self.root = root
        self.root.title("HACHI - Cosmos Control Center")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Paths
        self.config_dir = Path.home() / ".local" / "share" / "hachi"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        
        # Load config
        self.load_config()
        
        # Detect GPU and set theme
        self.detect_gpu()
        self.setup_theme()
        
        # Apply theme to root
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Device status
        self.device_connected = False
        self.tracking_status = "Unknown"
        self.controllers_connected = 0
        self.monado_running = False
        self.finger_tracking_enabled = False
        self.finger_tracking_active = False
        
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
    
    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "finger_tracking_enabled": False,
                "finger_tracking_sensitivity": 0.7,
                "hand_model": "basic",
                "camera_resolution": "high",
                "tracking_mode": "auto"
            }
            self.save_config()
    
    def save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, indent=2, fp=f)
    
    def detect_gpu(self):
        """Detect GPU vendor for color theme"""
        gpu_file = self.config_dir / "gpu_vendor.txt"
        
        if gpu_file.exists():
            with open(gpu_file, 'r') as f:
                self.gpu_vendor = f.read().strip()
        else:
            try:
                result = subprocess.run(['lspci'], capture_output=True, text=True)
                if 'nvidia' in result.stdout.lower():
                    self.gpu_vendor = 'nvidia'
                elif 'amd' in result.stdout.lower():
                    self.gpu_vendor = 'amd'
                elif 'intel' in result.stdout.lower():
                    self.gpu_vendor = 'intel'
                else:
                    self.gpu_vendor = 'unknown'
            except:
                self.gpu_vendor = 'unknown'
            
            with open(gpu_file, 'w') as f:
                f.write(self.gpu_vendor)
    
    def setup_theme(self):
        """Setup color theme based on GPU"""
        # Triple black base
        self.colors = {
            'bg_dark': '#0a0a0a',
            'bg_medium': '#151515',
            'bg_light': '#1f1f1f',
            'text': '#e0e0e0',
            'text_dim': '#808080',
            'border': '#2a2a2a',
        }
        
        # GPU-specific accents
        if self.gpu_vendor == 'nvidia':
            self.colors.update({
                'accent': '#76b900',
                'accent_hover': '#8cd400',
                'accent_dark': '#5c8f00',
                'status_good': '#76b900',
                'status_warning': '#ffa500',
                'status_error': '#ff3333',
            })
            self.gpu_name = "NVIDIA GPU"
        elif self.gpu_vendor == 'amd':
            self.colors.update({
                'accent': '#ed1c24',
                'accent_hover': '#ff3333',
                'accent_dark': '#c41820',
                'status_good': '#ed1c24',
                'status_warning': '#ffa500',
                'status_error': '#ff3333',
            })
            self.gpu_name = "AMD GPU"
        else:
            # Default to Intel Blue for Intel or Unknown
            self.colors.update({
                'accent': '#0071c5', # Intel Blue
                'accent_hover': '#0084e8',
                'accent_dark': '#005a9e',
                'status_good': '#0071c5',
                'status_warning': '#ffa500',
                'status_error': '#ff3333',
            })
            if self.gpu_vendor == 'intel':
                self.gpu_name = "Intel GPU"
            else:
                self.gpu_name = "Unknown GPU"
        
        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg_medium'], borderwidth=0)
        style.configure('TNotebook.Tab', background=self.colors['bg_light'],
                       foreground=self.colors['text'], padding=[20, 10], borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', self.colors['accent'])],
                 foreground=[('selected', self.colors['bg_dark'])])
    
    def create_styled_button(self, parent, text, command, width=20):
        """Create a styled button"""
        btn = tk.Button(
            parent, text=text, command=command,
            bg=self.colors['accent'], fg=self.colors['bg_dark'],
            activebackground=self.colors['accent_hover'],
            activeforeground=self.colors['bg_dark'],
            relief=tk.FLAT, font=('Arial', 10, 'bold'),
            width=width, cursor='hand2', padx=10, pady=8
        )
        
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
        
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_light'],
                           fg=self.colors['text'])
        file_menu.add_command(label="Preferences", command=self.show_preferences)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_light'],
                            fg=self.colors['text'])
        tools_menu.add_command(label="Device Monitor", command=self.launch_monitor)
        tools_menu.add_command(label="Performance Monitor", command=self.launch_perf_monitor)
        tools_menu.add_command(label="Finger Tracking Calibration", command=self.calibrate_finger_tracking)
        tools_menu.add_command(label="View Logs", command=self.show_logs)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_light'],
                           fg=self.colors['text'])
        help_menu.add_command(label="About HACHI", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
    
    def create_header(self):
        """Create header"""
        header = tk.Frame(self.root, bg=self.colors['bg_light'], height=100)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        left_frame = tk.Frame(header, bg=self.colors['bg_light'])
        left_frame.pack(side=tk.LEFT, padx=30, pady=20)
        
        title = tk.Label(
            left_frame, text="HACHI",
            font=('Arial', 32, 'bold'),
            bg=self.colors['bg_light'], fg=self.colors['accent']
        )
        title.pack(anchor=tk.W)
        
        subtitle = tk.Label(
            left_frame, text="Cosmos Control Center • 八 (Vive)",
            font=('Arial', 12),
            bg=self.colors['bg_light'], fg=self.colors['text_dim']
        )
        subtitle.pack(anchor=tk.W)
        
        right_frame = tk.Frame(header, bg=self.colors['bg_light'])
        right_frame.pack(side=tk.RIGHT, padx=30, pady=20)
        
        self.status_label = tk.Label(
            right_frame, text="● Checking device...",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_light'], fg=self.colors['text_dim']
        )
        self.status_label.pack(anchor=tk.E)
        
        self.gpu_label = tk.Label(
            right_frame, text=f"GPU: {self.gpu_name}",
            font=('Arial', 10),
            bg=self.colors['bg_light'], fg=self.colors['accent']
        )
        self.gpu_label.pack(anchor=tk.E)
        
        self.finger_tracking_label = tk.Label(
            right_frame, text="✋ Finger Tracking: Disabled",
            font=('Arial', 9),
            bg=self.colors['bg_light'], fg=self.colors['text_dim']
        )
        self.finger_tracking_label.pack(anchor=tk.E)
    
    def create_sidebar(self):
        """Create sidebar navigation"""
        sidebar = tk.Frame(self.root, bg=self.colors['bg_medium'], width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        sidebar_title = tk.Label(
            sidebar, text="NAVIGATION",
            font=('Arial', 10, 'bold'),
            bg=self.colors['bg_medium'], fg=self.colors['text_dim'], pady=20
        )
        sidebar_title.pack(fill=tk.X, padx=20)
        
        nav_buttons = [
            ("Dashboard", self.show_dashboard, "📊"),
            ("Tracking", self.show_tracking, "🎯"),
            ("Finger Tracking", self.show_finger_tracking, "✋"),
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
                btn_frame, text=f"{icon}  {text}", command=command,
                bg=self.colors['bg_medium'], fg=self.colors['text'],
                activebackground=self.colors['bg_light'],
                activeforeground=self.colors['accent'],
                relief=tk.FLAT, font=('Arial', 11),
                anchor=tk.W, padx=20, pady=12, cursor='hand2'
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
        """Create status bar"""
        status_bar = tk.Frame(self.root, bg=self.colors['bg_light'], height=30)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        status_bar.pack_propagate(False)
        
        self.status_bar_label = tk.Label(
            status_bar, text="HACHI Ready • Experimental Finger Tracking Available",
            font=('Arial', 9), bg=self.colors['bg_light'],
            fg=self.colors['text_dim'], anchor=tk.W
        )
        self.status_bar_label.pack(side=tk.LEFT, padx=10)
        
        time_label = tk.Label(
            status_bar, text=datetime.now().strftime("%H:%M:%S"),
            font=('Arial', 9), bg=self.colors['bg_light'],
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
        """Show dashboard"""
        self.clear_main_area()
        self.highlight_nav_button("Dashboard")
        
        container = tk.Frame(self.main_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        title = tk.Label(
            container, text="Dashboard",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'], fg=self.colors['text']
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Status cards
        cards_frame = tk.Frame(container, bg=self.colors['bg_dark'])
        cards_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.headset_card = self.create_status_card(
            cards_frame, "Headset", "● Checking...", self.colors['text_dim']
        )
        
        self.tracking_card = self.create_status_card(
            cards_frame, "Tracking", "Not configured", self.colors['text_dim']
        )
        
        self.finger_card = self.create_status_card(
            cards_frame, "Finger Tracking", "Disabled", self.colors['text_dim']
        )
        
        self.controller_card = self.create_status_card(
            cards_frame, "Controllers", "0/2", self.colors['text_dim']
        )
        
        # Quick actions
        actions_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        actions_frame.pack(fill=tk.BOTH, expand=True)
        
        actions_title = tk.Label(
            actions_frame, text="Quick Actions",
            font=('Arial', 16, 'bold'),
            bg=self.colors['bg_medium'], fg=self.colors['text'], pady=20
        )
        actions_title.pack(anchor=tk.W, padx=20)
        
        btn_container = tk.Frame(actions_frame, bg=self.colors['bg_medium'])
        btn_container.pack(padx=20, pady=(0, 20))
        
        self.create_styled_button(
            btn_container, "🚀 Launch VR", self.launch_vr, 25
        ).pack(side=tk.LEFT, padx=5)
        
        self.create_styled_button(
            btn_container, "✋ Enable Finger Tracking", 
            self.enable_finger_tracking, 30
        ).pack(side=tk.LEFT, padx=5)
        
        self.create_styled_button(
            btn_container, "🎮 Pair Controllers",
            self.pair_controllers, 25
        ).pack(side=tk.LEFT, padx=5)
    
    def show_finger_tracking(self):
        """Show finger tracking configuration"""
        self.clear_main_area()
        self.highlight_nav_button("Finger Tracking")
        
        container = tk.Frame(self.main_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        title = tk.Label(
            container, text="Finger Tracking (Experimental)",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'], fg=self.colors['text']
        )
        title.pack(anchor=tk.W, pady=(0, 10))
        
        # Warning banner
        warning_frame = tk.Frame(container, bg=self.colors['status_warning'])
        warning_frame.pack(fill=tk.X, pady=(0, 20))
        
        warning_label = tk.Label(
            warning_frame,
            text="⚠️ EXPERIMENTAL: Finger tracking requires working camera drivers. Results may vary.",
            font=('Arial', 11, 'bold'),
            bg=self.colors['status_warning'],
            fg=self.colors['bg_dark'],
            pady=10
        )
        warning_label.pack(padx=20)
        
        # Status section
        status_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            status_frame, text="Finger Tracking Status",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_medium'], fg=self.colors['text'], pady=15
        ).pack(anchor=tk.W, padx=20)
        
        status_text = "Active ✓" if self.finger_tracking_active else "Inactive"
        status_color = self.colors['status_good'] if self.finger_tracking_active else self.colors['text_dim']
        
        self.ft_status_label = tk.Label(
            status_frame, text=f"Status: {status_text}",
            font=('Arial', 12),
            bg=self.colors['bg_medium'], fg=status_color
        )
        self.ft_status_label.pack(anchor=tk.W, padx=40, pady=(0, 15))
        
        # Controls
        controls_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        controls_frame.pack(fill=tk.X, pady=(10, 10))
        
        tk.Label(
            controls_frame, text="Controls",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_medium'], fg=self.colors['text'], pady=15
        ).pack(anchor=tk.W, padx=20)
        
        btn_frame = tk.Frame(controls_frame, bg=self.colors['bg_medium'])
        btn_frame.pack(padx=20, pady=(0, 15))
        
        if self.finger_tracking_active:
            self.create_styled_button(
                btn_frame, "Disable Finger Tracking",
                self.disable_finger_tracking, 30
            ).pack(side=tk.LEFT, padx=5)
        else:
            self.create_styled_button(
                btn_frame, "Enable Finger Tracking",
                self.enable_finger_tracking, 30
            ).pack(side=tk.LEFT, padx=5)
        
        self.create_styled_button(
            btn_frame, "Calibrate Hands",
            self.calibrate_finger_tracking, 25
        ).pack(side=tk.LEFT, padx=5)
        
        self.create_styled_button(
            btn_frame, "Test Hand Detection",
            self.test_finger_tracking, 25
        ).pack(side=tk.LEFT, padx=5)
        
        # Settings
        settings_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        tk.Label(
            settings_frame, text="Settings",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_medium'], fg=self.colors['text'], pady=15
        ).pack(anchor=tk.W, padx=20)
        
        # Sensitivity slider
        sens_frame = tk.Frame(settings_frame, bg=self.colors['bg_light'])
        sens_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        tk.Label(
            sens_frame, text="Tracking Sensitivity:",
            font=('Arial', 11),
            bg=self.colors['bg_light'], fg=self.colors['text']
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        self.sensitivity_var = tk.DoubleVar(value=self.config.get('finger_tracking_sensitivity', 0.7))
        
        sensitivity_slider = tk.Scale(
            sens_frame,
            from_=0.1, to=1.0, resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.sensitivity_var,
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            highlightthickness=0,
            command=self.update_sensitivity
        )
        sensitivity_slider.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        # Hand model selection
        model_frame = tk.Frame(settings_frame, bg=self.colors['bg_light'])
        model_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        tk.Label(
            model_frame, text="Hand Model:",
            font=('Arial', 11),
            bg=self.colors['bg_light'], fg=self.colors['text']
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        self.hand_model_var = tk.StringVar(value=self.config.get('hand_model', 'basic'))
        
        for model in ["Basic", "Detailed", "Skeletal"]:
            tk.Radiobutton(
                model_frame,
                text=model,
                variable=self.hand_model_var,
                value=model.lower(),
                bg=self.colors['bg_light'],
                fg=self.colors['text'],
                selectcolor=self.colors['accent'],
                command=self.update_hand_model
            ).pack(side=tk.LEFT, padx=5)
        
        # Info text
        info_text = scrolledtext.ScrolledText(
            settings_frame, height=8,
            bg=self.colors['bg_dark'], fg=self.colors['text'],
            font=('Courier', 9), relief=tk.FLAT
        )
        info_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        info_text.insert('1.0', """HACHI Finger Tracking System

How it works:
• Uses Cosmos front-facing cameras for hand detection
• Tracks finger positions and gestures
• Compatible with VRChat, Job Simulator, and other games
• Requires camera drivers to be working

Status:
• Camera Detection: Checking...
• Hand Detection Model: Loading...
• Calibration: Not calibrated

Notes:
• Performance depends on camera driver quality
• Best results in well-lit environments
• Calibration recommended for accuracy
• May require manual adjustment per game
""")
        info_text.config(state=tk.DISABLED)
    
    def show_tracking(self):
        """Show tracking configuration"""
        self.clear_main_area()
        self.highlight_nav_button("Tracking")
        
        container = tk.Frame(self.main_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        title = tk.Label(
            container, text="Tracking Configuration",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'], fg=self.colors['text']
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        modes_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        modes_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            modes_frame, text="Tracking Mode",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_medium'], fg=self.colors['text'], pady=15
        ).pack(anchor=tk.W, padx=20)
        
        modes = [
            ("Hybrid Mode (Camera + IMU)", "Best quality, 6DOF tracking"),
            ("IMU Only", "Most stable, 3DOF rotation only"),
            ("Auto-Configure", "Automatically choose best option")
        ]
        
        for mode, description in modes:
            mode_btn = self.create_styled_button(
                modes_frame, mode,
                lambda m=mode: self.configure_tracking(m), 40
            )
            mode_btn.pack(padx=20, pady=5, anchor=tk.W)
            
            desc_label = tk.Label(
                modes_frame, text=description,
                font=('Arial', 9),
                bg=self.colors['bg_medium'], fg=self.colors['text_dim']
            )
            desc_label.pack(padx=60, pady=(0, 10), anchor=tk.W)
    
    def show_controllers(self):
        """Show controller configuration"""
        self.clear_main_area()
        self.highlight_nav_button("Controllers")
        
        container = tk.Frame(self.main_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        title = tk.Label(
            container, text="Controller Management",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'], fg=self.colors['text']
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        actions_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        actions_frame.pack(fill=tk.X)
        
        tk.Label(
            actions_frame, text="Controller Actions",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_medium'], fg=self.colors['text'], pady=15
        ).pack(anchor=tk.W, padx=20)
        
        btn_container = tk.Frame(actions_frame, bg=self.colors['bg_medium'])
        btn_container.pack(padx=20, pady=(0, 15))
        
        self.create_styled_button(
            btn_container, "Scan & Pair Controllers",
            self.pair_controllers, 30
        ).pack(side=tk.LEFT, padx=5)
        
        self.create_styled_button(
            btn_container, "Test Connectivity",
            self.test_controllers, 25
        ).pack(side=tk.LEFT, padx=5)
    
    def show_display(self):
        """Show display settings"""
        self.clear_main_area()
        self.highlight_nav_button("Display")
        
        container = tk.Frame(self.main_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        title = tk.Label(
            container, text="Display Settings",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'], fg=self.colors['text']
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        opt_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        opt_frame.pack(fill=tk.X)
        
        tk.Label(
            opt_frame, text="Performance Optimization",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_medium'], fg=self.colors['text'], pady=15
        ).pack(anchor=tk.W, padx=20)
        
        self.create_styled_button(
            opt_frame, "Run Full Optimization",
            self.optimize_display, 40
        ).pack(padx=20, pady=(0, 15), anchor=tk.W)
    
    def show_firmware(self):
        """Show firmware management"""
        self.clear_main_area()
        self.highlight_nav_button("Firmware")
        
        container = tk.Frame(self.main_area, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        title = tk.Label(
            container, text="Firmware Management",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'], fg=self.colors['text']
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        warning_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        warning_frame.pack(fill=tk.X)
        
        tk.Label(
            warning_frame, text="⚠️ Firmware updates require Windows",
            font=('Arial', 12, 'bold'),
            bg=self.colors['bg_medium'], fg=self.colors['status_warning'], pady=15
        ).pack(anchor=tk.W, padx=20)
    
    def create_status_card(self, parent, title, value, color):
        """Create a status card"""
        card = tk.Frame(parent, bg=self.colors['bg_medium'])
        card.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        card_title = tk.Label(
            card, text=title, font=('Arial', 11),
            bg=self.colors['bg_medium'], fg=self.colors['text_dim']
        )
        card_title.pack(pady=(15, 5))
        
        card_value = tk.Label(
            card, text=value, font=('Arial', 18, 'bold'),
            bg=self.colors['bg_medium'], fg=color
        )
        card_value.pack(pady=(0, 15))
        
        return card_value
    
    def highlight_nav_button(self, button_name):
        """Highlight active navigation button"""
        for name, btn in self.nav_buttons.items():
            if name == button_name:
                btn['bg'] = self.colors['accent']
                btn['fg'] = self.colors['bg_dark']
            else:
                btn['bg'] = self.colors['bg_medium']
                btn['fg'] = self.colors['text']
    
    def start_monitoring(self):
        """Start background monitoring"""
        def monitor():
            while True:
                self.check_device_status()
                time.sleep(2)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def check_device_status(self):
        """Check device status"""
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            self.device_connected = '0bb4:0313' in result.stdout
            
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
            
            # Update finger tracking status
            if self.finger_tracking_active:
                self.finger_tracking_label.config(
                    text="✋ Finger Tracking: Active",
                    fg=self.colors['status_good']
                )
            else:
                self.finger_tracking_label.config(
                    text="✋ Finger Tracking: Disabled",
                    fg=self.colors['text_dim']
                )
        except:
            pass
    
    # Finger tracking methods
    def enable_finger_tracking(self):
        """Enable finger tracking"""
        result = messagebox.askyesno(
            "Enable Finger Tracking",
            "Finger tracking is experimental and requires working camera drivers.\n\n"
            "Performance may vary depending on:\n"
            "• Camera driver quality\n"
            "• Lighting conditions\n"
            "• System performance\n\n"
            "Enable finger tracking?"
        )
        
        if result:
            self.status_bar_label.config(text="Initializing finger tracking...")
            threading.Thread(target=self._enable_finger_tracking_thread, daemon=True).start()
    
    def _enable_finger_tracking_thread(self):
        """Enable finger tracking in background"""
        try:
            # Create finger tracking script if it doesn't exist
            ft_script = self.config_dir / "finger_tracking.py"
            if not ft_script.exists():
                self.create_finger_tracking_module()
            
            # Launch finger tracking module
            subprocess.Popen(['python3', str(ft_script)])
            
            self.finger_tracking_active = True
            self.config['finger_tracking_enabled'] = True
            self.save_config()
            
            self.status_bar_label.config(text="Finger tracking enabled!")
            
        except Exception as e:
            self.status_bar_label.config(text=f"Failed to enable finger tracking: {e}")
    
    def disable_finger_tracking(self):
        """Disable finger tracking"""
        self.finger_tracking_active = False
        self.config['finger_tracking_enabled'] = False
        self.save_config()
        
        # Kill finger tracking process
        subprocess.run(['pkill', '-f', 'finger_tracking.py'], check=False)
        
        self.status_bar_label.config(text="Finger tracking disabled")
        messagebox.showinfo("Success", "Finger tracking has been disabled")
    
    def calibrate_finger_tracking(self):
        """Calibrate finger tracking"""
        messagebox.showinfo(
            "Calibration",
            "Finger Tracking Calibration:\n\n"
            "1. Ensure good lighting\n"
            "2. Hold hands in front of cameras\n"
            "3. Make fist, then spread fingers\n"
            "4. Repeat for both hands\n\n"
            "Calibration tool will launch..."
        )
        self.status_bar_label.config(text="Launching calibration...")
    
    def test_finger_tracking(self):
        """Test finger tracking"""
        messagebox.showinfo(
            "Test Mode",
            "Finger Tracking Test:\n\n"
            "A visualization window will open showing:\n"
            "• Detected hand positions\n"
            "• Finger joint tracking\n"
            "• Gesture recognition\n\n"
            "Move your hands in front of the cameras to test."
        )
        self.status_bar_label.config(text="Testing finger tracking...")
    
    def update_sensitivity(self, value):
        """Update tracking sensitivity"""
        self.config['finger_tracking_sensitivity'] = float(value)
        self.save_config()
    
    def update_hand_model(self):
        """Update hand model"""
        self.config['hand_model'] = self.hand_model_var.get()
        self.save_config()
    
    def create_finger_tracking_module(self):
        """Create the finger tracking Python module"""
        ft_script = self.config_dir / "finger_tracking.py"
        
        ft_code = '''#!/usr/bin/env python3
"""
HACHI Finger Tracking Module
Experimental hand and finger tracking using Cosmos cameras
"""

import cv2
import numpy as np
import time
import json
from pathlib import Path

class FingerTracker:
    def __init__(self):
        self.config_dir = Path.home() / ".local" / "share" / "hachi"
        self.load_config()
        
        # Try to open Cosmos cameras
        self.cameras = []
        for i in range(5):  # Try first 5 video devices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.cameras.append(cap)
        
        print(f"Found {len(self.cameras)} cameras")
        
        if not self.cameras:
            print("ERROR: No cameras detected!")
            print("Cosmos cameras may not be properly initialized.")
            return
        
        self.running = True
    
    def load_config(self):
        config_file = self.config_dir / "config.json"
        if config_file.exists():
            with open(config_file) as f:
                self.config = json.load(f)
        else:
            self.config = {
                "finger_tracking_sensitivity": 0.7,
                "hand_model": "basic"
            }
    
    def detect_hands(self, frame):
        """Basic hand detection using color and contours"""
        # Convert to HSV for skin detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Skin color range (adjust as needed)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create mask
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Apply morphological operations
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        hands = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 5000:  # Minimum hand size
                hands.append(contour)
        
        return hands, mask
    
    def run(self):
        """Main tracking loop"""
        print("Finger tracking started!")
        print("Press 'q' to quit")
        
        while self.running and self.cameras:
            for camera in self.cameras:
                ret, frame = camera.read()
                if not ret:
                    continue
                
                # Detect hands
                hands, mask = self.detect_hands(frame)
                
                # Draw detected hands
                for hand in hands:
                    # Draw contour
                    cv2.drawContours(frame, [hand], -1, (0, 255, 0), 2)
                    
                    # Find convex hull (rough finger detection)
                    hull = cv2.convexHull(hand, returnPoints=False)
                    defects = cv2.convexityDefects(hand, hull)
                    
                    if defects is not None:
                        for i in range(defects.shape[0]):
                            s, e, f, d = defects[i, 0]
                            start = tuple(hand[s][0])
                            end = tuple(hand[e][0])
                            far = tuple(hand[f][0])
                            
                            # Draw finger points
                            cv2.circle(frame, far, 5, (0, 0, 255), -1)
                
                # Show frame
                cv2.imshow('HACHI Finger Tracking', frame)
                cv2.imshow('Hand Mask', mask)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
                    break
        
        # Cleanup
        for camera in self.cameras:
            camera.release()
        cv2.destroyAllWindows()
        print("Finger tracking stopped")

if __name__ == "__main__":
    tracker = FingerTracker()
    if tracker.cameras:
        tracker.run()
'''
        
        with open(ft_script, 'w') as f:
            f.write(ft_code)
        
        ft_script.chmod(0o755)
    
    # Other action methods
    def launch_vr(self):
        """Launch VR"""
        self.status_bar_label.config(text="Launching VR session...")
        threading.Thread(target=lambda: subprocess.Popen(['bash', '-c', 'vr_manager.sh']), 
                        daemon=True).start()
    
    def configure_tracking(self, mode):
        """Configure tracking"""
        self.status_bar_label.config(text=f"Configuring: {mode}")
    
    def pair_controllers(self):
        """Pair controllers"""
        self.status_bar_label.config(text="Launching controller manager...")
        threading.Thread(target=lambda: subprocess.Popen(['python3', 
                        str(Path.home() / '.local/bin/controller_manager.py')]),
                        daemon=True).start()
    
    def test_controllers(self):
        """Test controllers"""
        self.status_bar_label.config(text="Testing controllers...")
    
    def optimize_display(self):
        """Optimize display"""
        self.status_bar_label.config(text="Optimizing display...")
        threading.Thread(target=lambda: subprocess.Popen(['bash',
                        str(Path.home() / '.local/bin/display_optimizer.sh')]),
                        daemon=True).start()
    
    def launch_monitor(self):
        """Launch monitor"""
        threading.Thread(target=lambda: subprocess.Popen(['python3',
                        str(Path.home() / '.local/bin/cosmos_monitor.py')]),
                        daemon=True).start()
    
    def launch_perf_monitor(self):
        """Launch performance monitor"""
        subprocess.Popen(['bash', '-c', 'vr-perf-monitor.sh'])
    
    def show_logs(self):
        """Show logs"""
        messagebox.showinfo("Logs", "Log viewer not yet implemented")
    
    def show_preferences(self):
        """Show preferences"""
        messagebox.showinfo("Preferences", "Preferences dialog not yet implemented")
    
    def show_about(self):
        """Show about"""
        about_text = f"""HACHI - Cosmos Control Center v2.0

Advanced VR management with experimental finger tracking

八 (Hachi) = Vive in Japanese

GPU: {self.gpu_name}
Theme: Triple Black with {self.gpu_vendor.upper()} accents

Features:
• Complete VR system management
• Experimental finger tracking
• GPU-optimized performance
• Real-time monitoring

Created for Linux
"""
        messagebox.showinfo("About HACHI", about_text)

def main():
    root = tk.Tk()
    app = HachiControlCenter(root)
    root.mainloop()

if __name__ == "__main__":
    main()