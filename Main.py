import os
import csv
import re
import threading
from numpy import imag
import tkintermapview
import json


from tkinter import messagebox
from customtkinter import filedialog
from PIL import Image

import customtkinter as ctk

# Local modules
from modules import email_handler
from modules import login_handler
from modules import user_handler
from modules import train_model
from modules import animation
from payload import deploy_handler
from payload import server_handler
from modules import report_generator

# ==========================================
# 🎨 CUSTOM THEME CONTROL PANEL
# ==========================================
MAIN_BG_COLOR = "#0B111A"       
APP_BG_COLOR = "#151E2B"        
PRIMARY_BTN_COLOR = "#3B99C9"   
HOVER_BTN_COLOR = "#286D94"     
SECONDARY_BTN_COLOR = "transparent" 
SECONDARY_BORDER = "#3B99C9"    
SECONDARY_HOVER = "#122538"     
TEXT_HIGHLIGHT = "#60C6ED"      
# ==========================================

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")


class PhishTraceApp(ctk.CTk):
    """Main application class for the PhishTrace SOC Dashboard."""
    
    def __init__(self):
        super().__init__()

        self.title("PhishTrace: Reverse-Traceback Tool")
        self.geometry("1000x700") 
        self.resizable(True, True)
        self.minsize(900, 600)
        self.configure(fg_color=APP_BG_COLOR)
        
        self.current_user = None 
        self.selected_dataset_path = None
        
        # Initialize Frames
        self.login_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.admin_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.user_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.manage_users_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.train_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.investigation_frame = ctk.CTkFrame(self, fg_color="transparent") 
        self.prompt_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.show_login_page()

    def hide_all_frames(self):
        """Hides all application frames to clear the screen for a new view."""
        self.login_frame.pack_forget()
        self.admin_frame.pack_forget()
        self.user_frame.pack_forget()
        self.manage_users_frame.pack_forget()
        self.train_frame.pack_forget()
        self.investigation_frame.pack_forget() 
        self.prompt_frame.pack_forget()

    # ================= LOGIN PORTAL =================
    def show_login_page(self):
        self.hide_all_frames()
        self.current_user = None
        self.login_frame.pack(pady=20, padx=20, fill="both", expand=True)

        for widget in self.login_frame.winfo_children():
            widget.destroy()

        logo_path = "logo_single.jpg"  
        if os.path.exists(logo_path):
            raw_image = Image.open(logo_path)
            my_logo = ctk.CTkImage(
                light_image=raw_image,
                dark_image=raw_image,
                size=(50, 50)
            )
            label_logo = ctk.CTkLabel(
                self.login_frame, 
                text=" PhishTrace", 
                text_color=TEXT_HIGHLIGHT, 
                image=my_logo, 
                compound="left", 
                font=ctk.CTkFont(size=32, weight="bold")
            )
        else:
            label_logo = ctk.CTkLabel(
                self.login_frame, 
                text="🛡️ PhishTrace", 
                text_color=TEXT_HIGHLIGHT, 
                font=ctk.CTkFont(size=32, weight="bold")
            )
        label_logo.pack(pady=(60, 10))

        label_title = ctk.CTkLabel(
            self.login_frame, 
            text="System Authentication", 
            font=ctk.CTkFont(size=14), 
            text_color="#A0B0C0"
        )
        label_title.pack(pady=(0, 30))

        self.entry_username = ctk.CTkEntry(
            self.login_frame, 
            placeholder_text="Username", 
            width=250, 
            height=40, 
            border_color=SECONDARY_BORDER
        )
        self.entry_username.pack(pady=10)
        self.entry_username.bind("<Return>", self.process_login)

        self.entry_password = ctk.CTkEntry(
            self.login_frame, 
            placeholder_text="Password", 
            show="*", 
            width=250, 
            height=40, 
            border_color=SECONDARY_BORDER
        )
        self.entry_password.pack(pady=10)
        self.entry_password.bind("<Return>", self.process_login)

        btn_login = ctk.CTkButton(
            self.login_frame, 
            text="Login", 
            fg_color=PRIMARY_BTN_COLOR, 
            hover_color=HOVER_BTN_COLOR, 
            font=ctk.CTkFont(weight="bold"), 
            corner_radius=8, 
            command=self.process_login, 
            width=250, 
            height=40
        )
        btn_login.pack(pady=20)

    def process_login(self, event=None):
        username = self.entry_username.get()
        password = self.entry_password.get()

        success, role = login_handler.authenticate(username, password)

        if success:
            self.current_user = username.lower().strip()
            
            # Figure out which page to load NEXT
            if role == 'admin':
                next_page = self.show_admin_portal
            else:
                next_page = self.show_user_portal
                
            # 🚀 Trigger the transition animation INSTEAD of loading the page instantly
            animation.play_auth_success_animation(
                root=self,
                container_frame=self.login_frame,
                bg_color=APP_BG_COLOR,
                on_complete_callback=next_page
            )
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    # ================= ADMIN PORTAL =================
    def show_admin_portal(self):
        self.hide_all_frames()
        self.admin_frame.pack(pady=0, padx=0, fill="both", expand=True)

        for widget in self.admin_frame.winfo_children():
            widget.destroy()

        header_bar = ctk.CTkFrame(self.admin_frame, height=60, corner_radius=0, fg_color=MAIN_BG_COLOR)
        header_bar.pack(fill="x", side="top")
        
        logo_path = "logo_single.jpg" 
        if os.path.exists(logo_path):
            raw_image = Image.open(logo_path)
            my_logo = ctk.CTkImage(
                light_image=raw_image,
                dark_image=raw_image,
                size=(30, 30)
            )
            lbl_logo = ctk.CTkLabel(
                header_bar, 
                text=" PhishTrace", 
                text_color=TEXT_HIGHLIGHT, 
                image=my_logo, 
                compound="left", 
                font=ctk.CTkFont(size=22, weight="bold")
            )
        else:
            lbl_logo = ctk.CTkLabel(
                header_bar, 
                text="🛡️ PhishTrace", 
                text_color=TEXT_HIGHLIGHT, 
                font=ctk.CTkFont(size=22, weight="bold")
            )
        lbl_logo.pack(side="left", padx=20, pady=15)
        
        right_menu = ctk.CTkFrame(header_bar, fg_color="transparent")
        right_menu.pack(side="right", padx=20, pady=15)
        
        lbl_user = ctk.CTkLabel(
            right_menu, 
            text=f"👤 {self.current_user}", 
            text_color="white", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_user.pack(side="left", padx=(0, 20))

        btn_pass = ctk.CTkButton(
            right_menu, 
            text="Change Password", 
            width=120, 
            fg_color="#2E7D32", 
            hover_color="#1B5E20", 
            corner_radius=6, 
            command=self.change_password_window
        )
        btn_pass.pack(side="left", padx=(0, 15))

        btn_logout = ctk.CTkButton(
            right_menu, 
            text="Logout", 
            width=80, 
            fg_color="#C62828", 
            hover_color="#b71c1c", 
            corner_radius=6, 
            command=self.show_login_page
        )
        btn_logout.pack(side="left")
        
        # 🚀 THE FIX: Draw the bottom dock FIRST so it never gets cut off!
        dock = ctk.CTkFrame(self.admin_frame, height=80, fg_color="#0A1520", corner_radius=10, border_width=1, border_color="#2A3B4C")
        dock.pack(side="bottom", fill="x", padx=20, pady=(0, 20))
        dock.pack_propagate(False)

        # Center the buttons inside the dock
        btn_container = ctk.CTkFrame(dock, fg_color="transparent")
        btn_container.pack(expand=True)

        btn_scan = ctk.CTkButton(btn_container, text="▶ Start Live Investigation", fg_color="transparent", border_width=2, border_color="#388E3C", text_color="#81C784", hover_color="#1B5E20", height=40, font=ctk.CTkFont(size=14, weight="bold"), command=self.show_investigation_page)
        btn_scan.pack(side="left", padx=15, pady=15)

        btn_manage_users = ctk.CTkButton(btn_container, text="👪 Manage Users", height=40, fg_color=SECONDARY_BTN_COLOR, border_width=1, border_color=SECONDARY_BORDER, text_color=TEXT_HIGHLIGHT, hover_color=SECONDARY_HOVER, command=self.show_manage_users_page)
        btn_manage_users.pack(side="left", padx=15, pady=15)

        btn_train = ctk.CTkButton(btn_container, text="🧠 Train ML Model", height=40, fg_color=SECONDARY_BTN_COLOR, border_width=1, border_color=SECONDARY_BORDER, text_color=TEXT_HIGHLIGHT, hover_color=SECONDARY_HOVER, command=self.show_train_page)
        btn_train.pack(side="left", padx=15, pady=15)

        btn_prompt = ctk.CTkButton(btn_container, text="⚙️ AI Strategy", height=40, fg_color=SECONDARY_BTN_COLOR, border_width=1, border_color=SECONDARY_BORDER, text_color=TEXT_HIGHLIGHT, hover_color=SECONDARY_HOVER, command=self.show_prompt_page)
        btn_prompt.pack(side="left", padx=15, pady=15)

        # 🚀 NOW draw the content area (It will automatically fill whatever vertical space is left)
        content = ctk.CTkFrame(self.admin_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        self.build_home_dashboard(content)

    # ================= USER PORTAL =================
    def show_user_portal(self):
        self.hide_all_frames()
        self.user_frame.pack(pady=0, padx=0, fill="both", expand=True)

        for widget in self.user_frame.winfo_children():
            widget.destroy()

        header_bar = ctk.CTkFrame(self.user_frame, height=60, corner_radius=0, fg_color=MAIN_BG_COLOR)
        header_bar.pack(fill="x", side="top")
        
        logo_path = "logo_single.jpg"
        if os.path.exists(logo_path):
            raw_image = Image.open(logo_path)
            my_logo = ctk.CTkImage(
                light_image=raw_image,
                dark_image=raw_image,
                size=(30, 30)
            )
            lbl_logo = ctk.CTkLabel(
                header_bar, 
                text=" PhishTrace", 
                text_color=TEXT_HIGHLIGHT, 
                image=my_logo, 
                compound="left", 
                font=ctk.CTkFont(size=22, weight="bold")
            )
        else:
            lbl_logo = ctk.CTkLabel(
                header_bar, 
                text="🛡️ PhishTrace", 
                text_color=TEXT_HIGHLIGHT, 
                font=ctk.CTkFont(size=22, weight="bold")
            )
        lbl_logo.pack(side="left", padx=20, pady=15)
        
        right_menu = ctk.CTkFrame(header_bar, fg_color="transparent")
        right_menu.pack(side="right", padx=20, pady=15)
        
        lbl_user = ctk.CTkLabel(
            right_menu, 
            text=f"👤 {self.current_user}", 
            text_color="white", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_user.pack(side="left", padx=(0, 20))

        btn_pass = ctk.CTkButton(
            right_menu, 
            text="Change Password", 
            width=120, 
            fg_color="#2E7D32", 
            hover_color="#1B5E20", 
            corner_radius=6, 
            command=self.change_password_window
        )
        btn_pass.pack(side="left", padx=(0, 15))

        btn_logout = ctk.CTkButton(
            right_menu, 
            text="Logout", 
            width=80, 
            fg_color="#C62828", 
            hover_color="#b71c1c", 
            corner_radius=6, 
            command=self.show_login_page
        )
        btn_logout.pack(side="left")

       # 🚀 THE FIX: Draw the bottom dock FIRST!
        dock = ctk.CTkFrame(self.user_frame, height=80, fg_color="#0A1520", corner_radius=10, border_width=1, border_color="#2A3B4C")
        dock.pack(side="bottom", fill="x", padx=20, pady=(0, 20))
        dock.pack_propagate(False)

        btn_container = ctk.CTkFrame(dock, fg_color="transparent")
        btn_container.pack(expand=True)

        btn_scan = ctk.CTkButton(btn_container, text="▶ Start Live Investigation", fg_color="transparent", border_width=2, border_color="#388E3C", text_color="#81C784", hover_color="#1B5E20", height=40, width=300, font=ctk.CTkFont(size=14, weight="bold"), command=self.show_investigation_page)
        btn_scan.pack(side="left", padx=15, pady=15)

        # 🚀 NOW draw the content area
        content = ctk.CTkFrame(self.user_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        self.build_home_dashboard(content)

    # ================= MASSIVE STATIC DASHBOARD ENGINE =================
    def build_home_dashboard(self, content_frame):
        """Builds the embedded Global Map and Active Cards for the main portals."""
        # Main container
        dash_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        dash_container.pack(fill="both", expand=True)

        header_frame = ctk.CTkFrame(dash_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # 🚀 Increased size to 28
        lbl_map_title = ctk.CTkLabel(header_frame, text="GLOBAL ACTIVE THREAT DASHBOARD", font=ctk.CTkFont(size=28, weight="bold"), text_color="#FF4C4C")
        # 🚀 Removed side="left" and added anchor="center"
        lbl_map_title.pack(anchor="center", pady=(5, 10))

        # 🚀 1. The RESPONSIVE Map (Automatically scales to any laptop/desktop screen)
        map_frame = ctk.CTkFrame(dash_container, corner_radius=10, border_width=2, border_color="#3B99C9", fg_color="#151E2B")
        # Added expand=True and fill="both" so it dynamically shares space with the cards below
        map_frame.pack(fill="both", expand=True, pady=(0, 15))

        map_widget = tkintermapview.TkinterMapView(map_frame, corner_radius=10)
        map_widget.pack(fill="both", expand=True, padx=4, pady=4)
        # 🚀 Deleted the dark tile server line here so it uses the default map!
        map_widget.set_position(15.0, 10.0)
        map_widget.set_zoom(2)

        # 🚀 2. The Sleek Scrollable Cards (Expands to fill the remaining space)
        scroll_area = ctk.CTkScrollableFrame(dash_container, height=240, fg_color="transparent")
        scroll_area.pack(fill="x", pady=(10, 0))

        # Gather Intelligence
        target_intel = {}
        if hasattr(self, 'deployed_targets'):
            for t in self.deployed_targets:
                target_intel[t] = {'hits': 0, 'last_seen': 'Awaiting...', 'platform': 'Unknown', 'markers': []}

        if os.path.exists("captured_traces.json"):
            try:
                with open("captured_traces.json", "r") as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            target = data.get('target')
                            if target:
                                if target not in target_intel:
                                    target_intel[target] = {'hits': 0, 'platform': 'Unknown', 'markers': []}
                                target_intel[target]['hits'] += 1
                                target_intel[target]['last_seen'] = data.get('timestamp', 'Unknown')
                                if data.get('platform') and data.get('platform') != 'Unknown':
                                    target_intel[target]['platform'] = data.get('platform')
                                lat, lon = data.get('lat'), data.get('lon')
                                if lat and lon and lat not in ["Pending Click", None, "N/A"]:
                                    try: target_intel[target]['markers'].append((float(lat), float(lon)))
                                    except: pass
                        except: pass
            except: pass

        # 🚀 3. Plot pins and automatically center on the most recent hit
        latest_lat, latest_lon = None, None
        for target, intel in target_intel.items():
            for lat, lon in intel.get('markers', []):
                map_widget.set_marker(lat, lon, text=f"Target: {target.split('@')[0]}")
                latest_lat, latest_lon = lat, lon

        # Snap the camera to the latest target if one exists
        if latest_lat and latest_lon:
            map_widget.set_position(latest_lat, latest_lon)
            map_widget.set_zoom(3)

        # Build the Cards
        if not target_intel:
            ctk.CTkLabel(scroll_area, text="No active tracking operations found.", text_color="gray").pack(pady=10)
            return

        sorted_targets = sorted(target_intel.items(), key=lambda item: item[1]['hits'], reverse=True)
        for target, intel in sorted_targets:
            is_active = intel['hits'] > 0
            card = ctk.CTkFrame(scroll_area, fg_color="#1A0A0A" if is_active else "#1A1505", corner_radius=8, border_width=1, border_color="#FF4C4C" if is_active else "#F2A900")
            card.pack(fill="x", pady=5, ipady=5)

            # 🚀 Left Section: Merged Identity & Metrics Frame
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=15, pady=10)
            
            # Row 1 & 2: Target and Status
            ctk.CTkLabel(info_frame, text=f"🎯 {target}", font=ctk.CTkFont(size=15, weight="bold"), text_color="white").pack(anchor="w")
            ctk.CTkLabel(info_frame, text="🚨 ACTIVE COMPROMISE" if is_active else "⏳ PAYLOAD PENDING", font=ctk.CTkFont(size=11, weight="bold"), text_color="#FF4C4C" if is_active else "#F2A900").pack(anchor="w", pady=(2, 6)) # Added bottom padding

            # Row 3 & 4: Hits, OS, and Last Seen (Stacked beneath status)
            ctk.CTkLabel(info_frame, text=f"Hits: {intel['hits']}  |  OS: {intel['platform']}", font=ctk.CTkFont(size=12), text_color="#A0B0C0").pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Last Seen: {intel['last_seen']}", font=ctk.CTkFont(size=12), text_color="#A0B0C0").pack(anchor="w", pady=(2, 0))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=15, pady=10)
            ctk.CTkButton(btn_frame, text="📡 Open Radar", width=100, height=30, fg_color="#2E7D32", hover_color="#1B5E20", font=ctk.CTkFont(weight="bold"), command=lambda t=target: self.launch_radar_from_home(t)).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="🗑️ Purge", width=60, height=30, fg_color="transparent", border_width=1, border_color="#C62828", text_color="#E57373", hover_color="#4A1414", command=lambda t=target: self.quick_purge_from_home(t)).pack(side="left")

    def launch_radar_from_home(self, target_email):
        self.current_target_email = target_email
        self.open_live_tracking_window()

    def quick_purge_from_home(self, target_email):
        confirm = messagebox.askyesno("Purge Data", f"Permanently delete all tracking data for {target_email}?")
        if confirm:
            self.current_target_email = target_email
            self.clear_map_data()
            self.show_admin_portal() if self.current_user == 'admin' else self.show_user_portal()
    

    # ================= LIVE INVESTIGATION PORTAL =================
    def show_investigation_page(self):
        self.hide_all_frames()
        self.investigation_frame.pack(pady=0, padx=0, fill="both", expand=True)

        for widget in self.investigation_frame.winfo_children():
            widget.destroy()

        # --- HEADER ---
        header = ctk.CTkFrame(self.investigation_frame, height=60, corner_radius=0, fg_color=MAIN_BG_COLOR)
        header.pack(fill="x", side="top")

        back_cmd = self.show_admin_portal if self.current_user == 'admin' else self.show_user_portal
        btn_back = ctk.CTkButton(
            header, 
            text="◀ Back", 
            width=80, 
            fg_color="transparent", 
            border_width=1, 
            border_color=SECONDARY_BORDER, 
            text_color=TEXT_HIGHLIGHT, 
            hover_color=SECONDARY_HOVER, 
            command=back_cmd
        )
        btn_back.pack(side="left", padx=20, pady=15)

        lbl_title = ctk.CTkLabel(
            header, 
            text="Live Threat Interception & Reverse-Traceback", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color=TEXT_HIGHLIGHT
        )
        lbl_title.pack(side="left", padx=20)

        # 🚀 NEW: Compact & Direct Server Dropdown
        from payload import server_handler
        
        server_status_var = ctk.StringVar(value="🔴 Offline")

        def handle_dropdown(choice):
            if choice == "▶ Start":
                dropdown_server.set("⏳ Starting...")
                dropdown_server.configure(values=["⏳ Starting..."])
                
                def bg_start():
                    success, result = server_handler.start_infrastructure()
                    if success:
                        self.after(0, lambda: dropdown_server.configure(
                            values=["⏹ Stop", f"📋 {result}"], # Shows the actual link in the dropdown!
                            fg_color="#2E7D32",
                            button_color="#2E7D32",
                            button_hover_color="#1B5E20"
                        ))
                        self.after(0, lambda: dropdown_server.set("🟢 Online"))
                    else:
                        self.after(0, lambda: dropdown_server.configure(
                            values=["▶ Start"],
                            fg_color="#C62828",
                            button_color="#C62828",
                            button_hover_color="#4A1414"
                        ))
                        self.after(0, lambda: dropdown_server.set("⚠️ Failed"))
                        self.after(2000, lambda: dropdown_server.set("🔴 Offline"))
                        
                threading.Thread(target=bg_start, daemon=True).start()

            # If they click the link inside the dropdown, copy it
            elif choice.startswith("📋"):
                current_url = choice.replace("📋 ", "")
                self.clipboard_clear()
                self.clipboard_append(current_url)
                dropdown_server.set("📋 Copied!")
                self.after(1500, lambda: dropdown_server.set("🟢 Online"))

            elif choice == "⏹ Stop":
                server_handler.stop_infrastructure()
                dropdown_server.configure(
                    values=["▶ Start"],
                    fg_color="#C62828",
                    button_color="#C62828",
                    button_hover_color="#4A1414"
                )
                dropdown_server.set("🔴 Offline")
                
            elif choice in ["🔴 Offline", "🟢 Online"]:
                pass

        # Create the OptionMenu Dropdown (Much less wide now)
        dropdown_server = ctk.CTkOptionMenu(
            header, 
            variable=server_status_var,
            values=["▶ Start"],
            width=130,   # 🚀 FIX: Reduced width to make it compact
            font=ctk.CTkFont(weight="bold", size=13),
            fg_color="#C62828",              
            button_color="#C62828", 
            button_hover_color="#4A1414", 
            dropdown_font=ctk.CTkFont(size=12),
            command=handle_dropdown
        )
        dropdown_server.pack(side="right", padx=20, pady=15)

        # Check status immediately when the page loads
        is_up, current_url = server_handler.check_status()
        if is_up:
            dropdown_server.configure(
                values=["⏹ Stop", f"📋 {current_url}"],
                fg_color="#2E7D32",          
                button_color="#2E7D32",
                button_hover_color="#1B5E20"
            )
            dropdown_server.set("🟢 Online")

        # --- MAIN CONTENT AREA ---
        content = ctk.CTkFrame(self.investigation_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # ==========================================
        # LEFT COLUMN (Threat Feed)
        # ==========================================
        left_col = ctk.CTkFrame(
            content, 
            width=630, 
            fg_color=MAIN_BG_COLOR, 
            corner_radius=10, 
            border_width=1, 
            border_color="#2A3B4C"
        )
        left_col.pack(side="left", fill="y", padx=(0, 10))
        left_col.pack_propagate(False)

        # API CONNECTION STATUS BAR
        from modules import email_handler 

        api_frame = ctk.CTkFrame(left_col, fg_color="#0B111A", corner_radius=8)
        api_frame.pack(fill="x", padx=10, pady=(15, 0), ipady=5)

        lbl_api_status = ctk.CTkLabel(
            api_frame, 
            text="🔴 API: Disconnected", 
            font=ctk.CTkFont(size=12, weight="bold"), 
            text_color="#E57373"
        )
        lbl_api_status.pack(side="left", padx=10)

        def update_api_ui(is_connected):
            if is_connected:
                lbl_api_status.configure(text="🟢 API: Connected", text_color="#00FFCC")
                btn_api_action.configure(
                    text="Disconnect", 
                    fg_color="#C62828", 
                    hover_color="#b71c1c", 
                    border_width=0, 
                    text_color="white", 
                    command=trigger_disconnect
                )
            else:
                lbl_api_status.configure(text="🔴 API: Disconnected", text_color="#E57373")
                btn_api_action.configure(
                    text="Connect Account", 
                    fg_color="transparent", 
                    border_width=1, 
                    border_color=SECONDARY_BORDER, 
                    text_color=TEXT_HIGHLIGHT, 
                    hover_color=SECONDARY_HOVER, 
                    command=trigger_connection
                )

        def trigger_connection():
            btn_api_action.configure(state="disabled", text="Connecting...")
            def bg_connect():
                success, msg = email_handler.connect_gmail_account(self.current_user)
                if success:
                    self.after(0, lambda: update_api_ui(True))
                    self.after(0, lambda: messagebox.showinfo("Connected", msg))
                else:
                    self.after(0, lambda: update_api_ui(False))
                    self.after(0, lambda: messagebox.showerror("Connection Error", msg))
                self.after(0, lambda: btn_api_action.configure(state="normal"))
            threading.Thread(target=bg_connect, daemon=True).start()

        def trigger_disconnect():
            success, msg = email_handler.disconnect_gmail_account(self.current_user)
            if success:
                update_api_ui(False)
                messagebox.showinfo("Disconnected", msg)
            else:
                messagebox.showerror("Error", msg)

        btn_api_action = ctk.CTkButton(
            api_frame, 
            width=100, 
            height=24, 
            font=ctk.CTkFont(size=11, weight="bold")
        )
        btn_api_action.pack(side="right", padx=10)
        
        update_api_ui(email_handler.check_connection(self.current_user))

        # Scan Button Header
        feed_header = ctk.CTkFrame(left_col, fg_color="transparent")
        feed_header.pack(fill="x", padx=10, pady=(15, 5))
        
        lbl_feed = ctk.CTkLabel(
            feed_header, 
            text="Live Inbox", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color="white"
        )
        lbl_feed.pack(side="left")

        # The actual scrolling feed
        feed_scroll = ctk.CTkScrollableFrame(left_col, fg_color="transparent")
        feed_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        # ==========================================
        # RIGHT COLUMN (Forensics, AI, & Map)
        # ==========================================
        right_col = ctk.CTkFrame(content, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # 🚀 2. INTEL & AI SUGGESTION (Reorganized Vertically)
        
        # --- Top Half: Forensic Metadata ---
        intel_card = ctk.CTkFrame(right_col, fg_color="#0A1520", corner_radius=10, border_width=1, border_color="#3B99C9")
        intel_card.pack(fill="both", expand=True, pady=(0, 10))
        
        lbl_intel = ctk.CTkLabel(intel_card, text="📡 Forensic Metadata", font=ctk.CTkFont(size=14, weight="bold"), text_color="#60C6ED")
        lbl_intel.pack(anchor="w", padx=10, pady=(10, 0))
        
        self.intel_box = ctk.CTkTextbox(intel_card, fg_color="#030911", text_color="#FFFFFF", font=ctk.CTkFont(family="Courier", size=14))
        self.intel_box.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.intel_box.insert("end", "[ Awaiting target selection... ]")
        self.intel_box.configure(state="disabled")

        # --- Bottom Half: AI Strategy ---
        ai_card = ctk.CTkFrame(right_col, fg_color="#0A1520", corner_radius=10, border_width=1, border_color="#388E3C")
        ai_card.pack(fill="both", expand=True, pady=(0, 15))
        
        lbl_ai = ctk.CTkLabel(ai_card, text="🤖 AI Traceback Strategy", font=ctk.CTkFont(size=14, weight="bold"), text_color="#81C784")
        lbl_ai.pack(anchor="w", padx=10, pady=(10, 0))

        self.ai_box = ctk.CTkTextbox(ai_card, fg_color="#030911", text_color="#00FFCC", font=ctk.CTkFont(size=14))
        self.ai_box.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.ai_box.insert("end", "Awaiting threat classification...")
        self.ai_box.configure(state="disabled")

        # 🚀 3. Payload Deploy Button
        def payload_btn_router():
            # The button decides what to do based on its current text!
            if "RADAR" in self.btn_payload.cget("text"):
                self.open_live_tracking_window()
            else:
                self.deploy_traceback_logic()

        self.btn_payload = ctk.CTkButton(
            right_col, 
            text="⚡ Prepare Traceback Payload", 
            height=50, 
            font=ctk.CTkFont(size=15, weight="bold"), 
            fg_color="transparent", 
            border_width=2, 
            border_color="#C62828", 
            text_color="#E57373", 
            hover_color="#4A1414", 
            corner_radius=8, 
            state="disabled",
            command=payload_btn_router # <-- Bound to the new router
        )
        self.btn_payload.pack(fill="x", side="bottom", pady=(15, 0))

        # ==========================================
        # FEED LOGIC (Upgraded with API Caching & Event Fixes)
        # ==========================================
        def load_email_details(email_data):
            self.current_email_metadata = email_data

            match = re.search(r'<(.+?)>', email_data['sender'])
            if match:
                self.current_target_email = match.group(1)
            else:
                self.current_target_email = email_data['sender']
                
            # 🚀 THE FIX 1: Robust Hard-Drive Check
            # Check if this target is in memory OR already has data in the JSON logs!
            if not hasattr(self, 'deployed_targets'):
                self.deployed_targets = set()
            
            is_deployed = self.current_target_email in self.deployed_targets

            # Failsafe: If memory was wiped, check the actual log file!
            if not is_deployed and os.path.exists("captured_traces.json"):
                with open("captured_traces.json", "r") as f:
                    for line in f:
                        try:
                            if json.loads(line).get('target') == self.current_target_email:
                                is_deployed = True
                                self.deployed_targets.add(self.current_target_email)
                                break
                        except: pass

            # 🚀 Formatting the metadata for the Intel Tab
            auth_clean = email_data['auth_results'].replace(';', ';\n                  ')
            
            meta_formatted = (
                "=========================================================\n"
                " 📧 STANDARD ROUTING HEADERS\n"
                "=========================================================\n"
                f" Date         : {email_data['date']}\n"
                f" From         : {email_data['sender']}\n"
                f" To           : {email_data['receiver']}\n"
                f" Subject      : {email_data['subject']}\n\n"
                "=========================================================\n"
                " 🔍 FORENSIC TRACEBACK DATA\n"
                "=========================================================\n"
                f" Origin IP    : {email_data['source_ip']}\n"
                f" Geo-Location : {email_data['geo_location']}\n"
                f" Return-Path  : {email_data['return_path']}\n"
                f" Message-ID   : {email_data['message_id']}\n\n"
                "=========================================================\n"
                " 🛡️ SECURITY & PROTOCOL AUTHENTICATION\n"
                "=========================================================\n"
                f" Results      : {auth_clean}\n\n"
                "=========================================================\n"
                " 🤖 CONTENT EXTRACT\n"
                "=========================================================\n"
                f" {email_data['body']}\n"
            )

            self.intel_box.configure(state="normal")
            self.intel_box.delete("1.0", "end")
            self.intel_box.insert("end", meta_formatted)
            self.intel_box.configure(state="disabled")

            self.ai_box.configure(state="normal")
            self.ai_box.delete("1.0", "end")

            if email_data["status"] == "MALICIOUS":
                self.ai_box.configure(text_color="#FF4C4C")
                
                # If we already generated this reply, load it from memory.
                if "generated_reply" in email_data:
                    self.ai_box.insert("end", email_data["generated_reply"])
                    
                    # Decide what the button should look like based on deployment state
                    if is_deployed:
                        self.btn_payload.configure(
                            state="normal", 
                            text="📡 OPEN LIVE RADAR", 
                            fg_color="#2E7D32", 
                            hover_color="#1B5E20",
                            border_color="#2E7D32",
                            text_color="white"
                        )
                    else:
                        self.btn_payload.configure(
                            state="normal", 
                            text="⚡ Prepare Traceback Payload", 
                            text_color="#E57373",
                            fg_color="transparent",
                            border_color="#C62828", 
                            hover_color="#4A1414"
                        )
                    
                    self.ai_box.configure(state="disabled")
                    return 

                # If no cache exists, show loading state and call the API
                self.ai_box.insert("end", f"🚨 MALICIOUS (Confidence: {email_data['confidence']:.1f}%)\n\nGenerating AI Traceback Strategy... Please wait ⏳")
                self.btn_payload.configure(
                    state="disabled", 
                    text="Generating Payload...", 
                    fg_color="#C62828", 
                    border_color="#C62828"
                )
                self.ai_box.configure(state="disabled")

                def fetch_ai_reply():
                    from modules import ai_reply_handler
                    dynamic_reply = ai_reply_handler.generate_traceback_reply(
                        email_data["sender"], 
                        email_data["subject"], 
                        email_data["body"]
                    )
                    
                    final_text = (
                        f"🚨 MALICIOUS (Confidence: {email_data['confidence']:.1f}%) 🚨\n\n"
                        f"Target: {email_data['sender']}\n\n"
                        f"🤖 Dynamic Traceback Strategy Generated:\n"
                        f"==================================================\n"
                        f"{dynamic_reply}\n"
                        f"==================================================\n"
                    )
                    
                    # Save the new AI text to the cache
                    email_data["generated_reply"] = final_text
                    
                    def update_gui():
                        self.ai_box.configure(state="normal")
                        self.ai_box.delete("1.0", "end")
                        self.ai_box.insert("end", final_text)
                        self.ai_box.configure(state="disabled")
                        
                        # 🚀 THE FIX 2: Check is_deployed even after generating the text!
                        if is_deployed:
                            self.btn_payload.configure(
                                state="normal", 
                                text="📡 OPEN LIVE RADAR", 
                                fg_color="#2E7D32", 
                                hover_color="#1B5E20",
                                border_color="#2E7D32",
                                text_color="white"
                            )
                        else:
                            self.btn_payload.configure(
                                state="normal", 
                                text="⚡ Prepare Traceback Payload", 
                                text_color="#E57373",
                                fg_color="transparent",
                                border_color="#C62828", 
                                hover_color="#4A1414"
                            )
                    
                    self.after(0, update_gui)

                threading.Thread(target=fetch_ai_reply, daemon=True).start()

            else:
                self.ai_box.configure(text_color="#00FFCC")
                self.ai_box.insert("end", email_data["ai"])
                self.btn_payload.configure(
                    state="disabled", 
                    text="Traceback Not Required (Safe Email)", 
                    fg_color="transparent", 
                    text_color="#4CAF50", 
                    border_color="#4CAF50"
                )
                self.ai_box.configure(state="disabled")

        def build_feed_cards(email_list):
            for widget in feed_scroll.winfo_children():
                widget.destroy()

            if not email_list:
                ctk.CTkLabel(feed_scroll, text="Inbox is empty or scanning failed.", text_color="gray").pack(pady=20)
                return
            
            if "error" in email_list[0]:
                ctk.CTkLabel(feed_scroll, text=email_list[0]["error"], text_color="#E57373", wraplength=250).pack(pady=20)
                return

            for email in email_list:
                is_malicious = (email["status"] == "MALICIOUS")
                
                card_bg = "#2A0D0D" if is_malicious else "#0D2A14"
                border_c = "#FF3333" if is_malicious else "#33FF33"
                badge_text = "⚠️ MALICIOUS" if is_malicious else "✅ SECURE"
                
                sender_clean = email['sender'].split('<')[0].strip()
                if len(sender_clean) > 40: sender_clean = sender_clean[:40] + "..." # Increased sender limit
                
                sub_clean = email['subject']
                if len(sub_clean) > 120: sub_clean = sub_clean[:120] + "..."

                card = ctk.CTkButton(
                    feed_scroll, 
                    text="", 
                    width=620, 
                    fg_color=card_bg, 
                    hover_color="#333333", 
                    border_width=1, 
                    border_color=border_c, 
                    corner_radius=8, 
                    height=120, 
                    command=lambda e_data=email: load_email_details(e_data)
                )
                card.pack(fill="x", pady=5, padx=(5, 10))
                card.pack_propagate(False)

                lbl_badge = ctk.CTkLabel(
                    card, 
                    text=badge_text, 
                    font=ctk.CTkFont(size=13, weight="bold"), 
                    text_color=border_c, 
                    fg_color="transparent"
                )
                lbl_badge.pack(anchor="w", padx=10, pady=(8, 2))

                lbl_subj = ctk.CTkLabel(
                    card, 
                    text=f"Subj: {sub_clean}", 
                    font=ctk.CTkFont(size=12, weight="bold"), 
                    text_color="white", 
                    fg_color="transparent"
                )
                lbl_subj.pack(anchor="w", padx=10)

                lbl_sender = ctk.CTkLabel(
                    card, 
                    text=f"From: {sender_clean}", 
                    font=ctk.CTkFont(size=11), 
                    text_color="#A0B0C0", 
                    fg_color="transparent"
                )
                lbl_sender.pack(anchor="w", padx=10)

                def pass_click(event, e_data=email):
                    load_email_details(e_data)
                    return "break"  
                
                lbl_badge.bind("<Button-1>", pass_click)
                lbl_subj.bind("<Button-1>", pass_click)
                lbl_sender.bind("<Button-1>", pass_click)

        def trigger_live_scan():
            btn_scan_inbox.configure(state="disabled", text="Scanning...")
            
            def background_task():
                emails = email_handler.fetch_and_analyze_inbox(self.current_user, max_emails=50)
                self.after(0, lambda: build_feed_cards(emails))
                self.after(0, lambda: btn_scan_inbox.configure(state="normal", text="🔄 Scan Live Inbox"))
                
            threading.Thread(target=background_task, daemon=True).start()

        # 🚀 NEW: The Active Radars Hub Button
        btn_active_radars = ctk.CTkButton(
            feed_header,
            text="📡 Active Radars",
            width=110,
            height=28,
            fg_color="#0D2A14", 
            border_width=1,
            border_color="#388E3C",
            hover_color="#1B5E20",
            text_color="#81C784",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.open_active_radars_hub
        )
        btn_active_radars.pack(side="right", padx=(10, 0))

        btn_scan_inbox = ctk.CTkButton(
            feed_header, 
            text="🔄 Scan Live Inbox", 
            width=120, 
            height=28, 
            fg_color="transparent", 
            border_width=1, 
            border_color=SECONDARY_BORDER, 
            hover_color=SECONDARY_HOVER, 
            text_color=TEXT_HIGHLIGHT, 
            font=ctk.CTkFont(size=12, weight="bold"), 
            command=trigger_live_scan
        )
        btn_scan_inbox.pack(side="right")


    # ================= MANAGE USERS PORTAL =================
    def show_manage_users_page(self):
        self.hide_all_frames()
        self.manage_users_frame.pack(pady=0, padx=0, fill="both", expand=True)

        for widget in self.manage_users_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.manage_users_frame, height=60, corner_radius=0, fg_color=MAIN_BG_COLOR)
        header.pack(fill="x", side="top")

        btn_back = ctk.CTkButton(
            header, 
            text="◀ Back", 
            width=80, 
            fg_color="transparent", 
            border_width=1, 
            border_color=SECONDARY_BORDER, 
            text_color=TEXT_HIGHLIGHT, 
            hover_color=SECONDARY_HOVER, 
            command=self.show_admin_portal
        )
        btn_back.pack(side="left", padx=20, pady=15)

        lbl_title = ctk.CTkLabel(
            header, 
            text="Manage System Users", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color=TEXT_HIGHLIGHT
        )
        lbl_title.pack(side="left", padx=20)

        content = ctk.CTkFrame(self.manage_users_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=20)
        
        left_col = ctk.CTkFrame(
            content, 
            fg_color=MAIN_BG_COLOR, 
            corner_radius=10, 
            border_width=1, 
            border_color="#2A3B4C"
        )
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_col = ctk.CTkFrame(
            content, 
            fg_color=MAIN_BG_COLOR, 
            corner_radius=10, 
            border_width=1, 
            border_color="#2A3B4C"
        )
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        def refresh_user_list():
            all_users = list(login_handler.load_users().keys())
            if 'admin' in all_users:
                all_users.remove('admin')
            if not all_users:
                all_users = ["No users available"]
            dropdown_del_user.configure(values=all_users)
            del_user_var.set(all_users[0])

        label_add = ctk.CTkLabel(
            left_col, 
            text="Add New Investigator", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="white"
        )
        label_add.pack(pady=(30, 15))

        entry_new_user = ctk.CTkEntry(
            left_col, 
            placeholder_text="New Username (lowercase)", 
            width=250, 
            height=40, 
            border_color=SECONDARY_BORDER
        )
        entry_new_user.pack(pady=10)

        entry_new_pass = ctk.CTkEntry(
            left_col, 
            placeholder_text="New Password", 
            show="*", 
            width=250, 
            height=40, 
            border_color=SECONDARY_BORDER
        )
        entry_new_pass.pack(pady=10)

        role_var = ctk.StringVar(value="user")
        dropdown_role = ctk.CTkComboBox(
            left_col, 
            variable=role_var, 
            values=["user", "admin"], 
            width=250, 
            height=40, 
            border_color=SECONDARY_BORDER,
            fg_color=MAIN_BG_COLOR,        
            button_color=SECONDARY_BORDER, 
            button_hover_color=SECONDARY_HOVER,
            state="readonly"               
        )
        dropdown_role.pack(pady=10)

        def attempt_add_user():
            username = entry_new_user.get()
            password = entry_new_pass.get()
            role = role_var.get()
            
            success, msg = user_handler.add_user(username, password, role)
            if success:
                messagebox.showinfo("Success", msg)
                entry_new_user.delete(0, 'end')
                entry_new_pass.delete(0, 'end')
                refresh_user_list()
            else:
                messagebox.showerror("Error", msg)

        btn_add = ctk.CTkButton(
            left_col, 
            text="Create Account", 
            fg_color="transparent", 
            border_width=2, 
            border_color="#388E3C",   
            text_color="#81C784",     
            hover_color="#1B5E20",    
            height=40, 
            width=250, 
            font=ctk.CTkFont(weight="bold"), 
            corner_radius=6, 
            command=attempt_add_user
        )

        btn_add.pack(pady=(20, 20))

        label_del = ctk.CTkLabel(
            right_col, 
            text="Remove User", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="white"
        )
        label_del.pack(pady=(30, 10))
        
        lbl_del_instruct = ctk.CTkLabel(
            right_col, 
            text="Select an account to permanently\nremove their system access.", 
            text_color="#A0B0C0"
        )
        lbl_del_instruct.pack(pady=(0, 15))

        del_user_var = ctk.StringVar()
        dropdown_del_user = ctk.CTkComboBox(
            right_col, 
            variable=del_user_var, 
            width=250, 
            height=40, 
            border_color=SECONDARY_BORDER,       
            fg_color=MAIN_BG_COLOR,        
            button_color=SECONDARY_BORDER,        
            button_hover_color=SECONDARY_HOVER,  
            state="readonly"               
        )
        dropdown_del_user.pack(pady=10)
        
        refresh_user_list()

        def attempt_delete_user():
            username = del_user_var.get()
            if username == "No users available":
                messagebox.showerror("Error", "No users to delete.")
                return
            if username == self.current_user:
                messagebox.showerror("Error", "You cannot delete your own account while logged in.")
                return

            confirm = messagebox.askyesno(
                "Confirm Revocation", 
                f"Are you sure you want to completely delete the account for '{username}'?"
            )
            if confirm:
                success, msg = user_handler.delete_user(username)
                if success:
                    messagebox.showinfo("Success", msg)
                    refresh_user_list() 
                else:
                    messagebox.showerror("Error", msg)

        btn_del = ctk.CTkButton(
            right_col, 
            text="Remove Access", 
            fg_color="transparent", 
            border_width=2, 
            border_color="#C62828", 
            text_color="#E57373", 
            hover_color="#4A1414", 
            height=40, 
            width=250, 
            font=ctk.CTkFont(weight="bold"), 
            corner_radius=6, 
            command=attempt_delete_user
        )
        btn_del.pack(pady=(20, 20))

    # ================= ML TRAINING PORTAL =================
    def show_train_page(self):
        self.hide_all_frames()
        self.train_frame.pack(pady=0, padx=0, fill="both", expand=True)

        for widget in self.train_frame.winfo_children():
            widget.destroy()

        self.selected_dataset_path = None

        header = ctk.CTkFrame(self.train_frame, height=60, corner_radius=0, fg_color=MAIN_BG_COLOR)
        header.pack(fill="x", side="top")

        btn_back = ctk.CTkButton(
            header, 
            text="◀ Back", 
            width=80, 
            fg_color="transparent", 
            border_width=1, 
            border_color=SECONDARY_BORDER, 
            text_color=TEXT_HIGHLIGHT, 
            hover_color=SECONDARY_HOVER, 
            command=self.show_admin_portal
        )
        btn_back.pack(side="left", padx=20, pady=15)

        lbl_title = ctk.CTkLabel(
            header, 
            text="Machine Learning Training Module", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color=TEXT_HIGHLIGHT
        )
        lbl_title.pack(side="left", padx=20)

        content = ctk.CTkFrame(self.train_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        left_col = ctk.CTkFrame(content, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_col = ctk.CTkFrame(
            content, 
            fg_color=MAIN_BG_COLOR, 
            corner_radius=10, 
            border_width=1, 
            border_color="#2A3B4C"
        )
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        upload_frame = ctk.CTkFrame(
            left_col, 
            fg_color=MAIN_BG_COLOR, 
            border_width=1, 
            border_color="#2A3B4C"
        )
        upload_frame.pack(fill="x", pady=(0, 20), ipadx=10, ipady=10)

        lbl_instruct = ctk.CTkLabel(
            upload_frame, 
            text="Select Phishing Dataset", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color="white"
        )
        lbl_instruct.pack(side="left", padx=20, pady=10)

        lbl_file_selected = ctk.CTkLabel(upload_frame, text="No file selected.", text_color="gray")

        # --- DATASET REQUIREMENTS CARD ---
        req_frame = ctk.CTkFrame(left_col, fg_color="#0D1A26", corner_radius=8, border_width=1, border_color="#1E3A5F")
        req_frame.pack(fill="x", padx=20, pady=(10, 20))

        # Title
        lbl_req_title = ctk.CTkLabel(
            req_frame, 
            text="📊 CSV Dataset Requirements", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color="#60C6ED"
        )
        lbl_req_title.pack(anchor="w", padx=15, pady=(10, 5))

        # Instructions Text
        instructions = (
            "To train a new Phishing Detection AI, upload a .CSV file containing at least two columns:\n\n"
            "1. The Email Content Column (Must be named one of the following):\n"
            "   • 'text', 'body', 'content', 'message', or 'email'\n\n"
            "2. The Classification Label Column (Must be named one of the following):\n"
            "   • 'label', 'target', 'class', or 'is_phishing'\n\n"
            "💡 Smart Detection: The system automatically accepts numeric labels (1 = Phishing, 0 = Safe) "
            "or text labels ('spam'/'ham', 'bad'/'good')."
        )

        lbl_instructions = ctk.CTkLabel(
            req_frame, 
            text=instructions, 
            font=ctk.CTkFont(size=12), 
            text_color="#A0B0C0",
            justify="left"
        )
        lbl_instructions.pack(anchor="w", padx=15, pady=(0, 15))

        def select_file():
            file_path = filedialog.askopenfilename(
                title="Select Phishing Dataset", 
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            if file_path:
                self.selected_dataset_path = file_path
                filename = os.path.basename(file_path)
                lbl_file_selected.configure(text=f"Ready: {filename}", text_color="#00FFCC")
                btn_start_train.configure(state="normal")

        btn_upload = ctk.CTkButton(
            upload_frame, 
            text="Browse Files", 
            fg_color="transparent", 
            border_width=1, 
            border_color=SECONDARY_BORDER, 
            text_color=TEXT_HIGHLIGHT, 
            hover_color=SECONDARY_HOVER, 
            command=select_file
        )
        btn_upload.pack(side="right", padx=20, pady=10)
        lbl_file_selected.pack(side="right", padx=10, pady=10)

        btn_start_train = ctk.CTkButton(
            left_col, 
            text="▶ START AI TRAINING", 
            fg_color="transparent", 
            border_width=2, 
            border_color="#388E3C",   
            text_color="#81C784",     
            hover_color="#1B5E20",    
            height=50, 
            font=ctk.CTkFont(size=16, weight="bold"), 
            corner_radius=8, 
            state="disabled"
        )
        btn_start_train.pack(fill="x", pady=(0, 10))

        # Delete Models Button
        def trigger_delete_models():
            confirm = messagebox.askyesno(
                "Warning: Deleting AI", 
                "Are you sure you want to delete the active ML models? The scanner will stop working until you train a new dataset."
            )
            if confirm:
                deleted = False
                if os.path.exists('models/tfidf_vectorizer.pkl'):
                    os.remove('models/tfidf_vectorizer.pkl')
                    deleted = True
                if os.path.exists('models/phishing_rf_model.pkl'):
                    os.remove('models/phishing_rf_model.pkl')
                    deleted = True
                
                if deleted:
                    append_log("🗑️ Active Machine Learning models deleted from local storage.")
                    messagebox.showinfo("Models Removed", "AI Models successfully deleted. The system requires retraining.")
                else:
                    messagebox.showinfo("Info", "No active models found in the /models directory.")

        btn_delete_models = ctk.CTkButton(
            left_col, 
            text="🗑️ Delete Active AI Models", 
            height=30, 
            fg_color="transparent", 
            border_width=1, 
            border_color="#C62828", 
            text_color="#E57373", 
            hover_color="#4A1414", 
            corner_radius=8,
            command=trigger_delete_models
        )
        btn_delete_models.pack(fill="x", pady=(0, 20))

        lbl_log = ctk.CTkLabel(
            left_col, 
            text="Live Process Logs:", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color="white"
        )
        lbl_log.pack(anchor="w")

        log_box = ctk.CTkTextbox(
            left_col, 
            height=200, 
            fg_color="#05080F", 
            text_color="#00FF00", 
            border_width=1, 
            border_color="#2A3B4C", 
            font=ctk.CTkFont(family="Courier", size=12)
        )
        log_box.pack(fill="both", expand=True, pady=(5, 0))
        log_box.insert("end", "Awaiting dataset upload...\n")
        log_box.configure(state="disabled")

        # History Header Frame with Clear Button
        hist_header_frame = ctk.CTkFrame(right_col, fg_color="transparent")
        hist_header_frame.pack(fill="x", pady=(15, 5), padx=20)

        lbl_hist_title = ctk.CTkLabel(
            hist_header_frame, 
            text="Training Audit History", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color="white"
        )
        lbl_hist_title.pack(side="left")

        def trigger_clear_history():
            confirm = messagebox.askyesno(
                "Clear History", 
                "Are you sure you want to permanently clear the training audit history?"
            )
            if confirm:
                if os.path.exists("training_history.csv"):
                    os.remove("training_history.csv")
                load_history()
                append_log("🧹 Training history log cleared.")

        btn_clear_hist = ctk.CTkButton(
            hist_header_frame, 
            text="Clear", 
            width=60, 
            height=24, 
            fg_color="#C62828", 
            hover_color="#b71c1c", 
            font=ctk.CTkFont(size=11, weight="bold"), 
            command=trigger_clear_history
        )
        btn_clear_hist.pack(side="right")

        history_scroll = ctk.CTkScrollableFrame(right_col, fg_color="transparent")
        history_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        def load_history():
            for widget in history_scroll.winfo_children():
                widget.destroy()

            headers = ["Date & Time", "Dataset", "Accuracy"]
            for col_idx, text in enumerate(headers):
                lbl = ctk.CTkLabel(
                    history_scroll, 
                    text=text, 
                    font=ctk.CTkFont(weight="bold", size=13), 
                    text_color=TEXT_HIGHLIGHT
                )
                lbl.grid(row=0, column=col_idx, padx=10, pady=(0, 10), sticky="w")

            if not os.path.exists("training_history.csv"):
                lbl = ctk.CTkLabel(history_scroll, text="No training history found.", text_color="gray")
                lbl.grid(row=1, column=0, columnspan=3, pady=20)
                return

            try:
                with open("training_history.csv", "r") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    if len(rows) > 1:
                        for r_idx, row in enumerate(reversed(rows[1:]), start=1):
                            if len(row) >= 3:
                                time_val, name_val, acc_val = row[0], row[1], row[2]
                                time_val = time_val.split(" ")[0] + " " + time_val.split(" ")[1][:5]
                                
                                ctk.CTkLabel(
                                    history_scroll, 
                                    text=time_val, 
                                    font=ctk.CTkFont(size=12), 
                                    text_color="white"
                                ).grid(row=r_idx, column=0, padx=10, pady=5, sticky="w")
                                
                                ctk.CTkLabel(
                                    history_scroll, 
                                    text=name_val[:15]+"...", 
                                    font=ctk.CTkFont(size=12), 
                                    text_color="#A0B0C0"
                                ).grid(row=r_idx, column=1, padx=10, pady=5, sticky="w")
                                
                                ctk.CTkLabel(
                                    history_scroll, 
                                    text=acc_val, 
                                    font=ctk.CTkFont(size=12, weight="bold"), 
                                    text_color="#00FFCC"
                                ).grid(row=r_idx, column=2, padx=10, pady=5, sticky="w")
            except Exception as e:
                print(f"Error reading history: {e}")

        load_history()

        def append_log(msg):
            log_box.configure(state="normal")
            log_box.insert("end", msg + "\n")
            log_box.see("end")
            log_box.configure(state="disabled")

        def run_training_thread():
            btn_start_train.configure(state="disabled")
            btn_upload.configure(state="disabled")
            btn_back.configure(state="disabled")
            btn_delete_models.configure(state="disabled")

            append_log("\n==============================================================================")
            append_log("               [SYSTEM] INITIALIZING MACHINE LEARNING SEQUENCE...")
            append_log("==============================================================================\n")
            
            success, final_msg = train_model.train_and_save_model(self.selected_dataset_path, append_log)

            append_log("\n==============================================================================")
            if success:
                append_log(f"✅ [SYSTEM SUCCESS] \n{final_msg}")
            else:
                append_log(f"❌ [SYSTEM FAILURE] \n{final_msg}")
            append_log("==============================================================================\n")

            self.after(0, load_history)

            btn_back.configure(state="normal")
            btn_upload.configure(state="normal")
            btn_delete_models.configure(state="normal")

        def start_training_process():
            if not self.selected_dataset_path: return
            threading.Thread(target=run_training_thread, daemon=True).start()

        btn_start_train.configure(command=start_training_process)

    # ================= CHANGE PASSWORD WINDOW =================
    def change_password_window(self):
        pass_win = ctk.CTkToplevel(self)
        pass_win.title("Change Password")
        pass_win.geometry("400x300")
        pass_win.resizable(False, False)
        pass_win.grab_set()
        
        pass_win.configure(fg_color=MAIN_BG_COLOR)

        label_title = ctk.CTkLabel(
            pass_win, 
            text="Change Password", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color=TEXT_HIGHLIGHT
        )
        label_title.pack(pady=(20, 20))

        entry_new_pass = ctk.CTkEntry(
            pass_win, 
            placeholder_text="New Password", 
            show="*", 
            width=250, 
            height=40, 
            border_color=SECONDARY_BORDER
        )
        entry_new_pass.pack(pady=10)

        entry_confirm_pass = ctk.CTkEntry(
            pass_win, 
            placeholder_text="Confirm New Password", 
            show="*", 
            width=250, 
            height=40, 
            border_color=SECONDARY_BORDER
        )
        entry_confirm_pass.pack(pady=10)

        def attempt_update():
            new_pass = entry_new_pass.get()
            confirm_pass = entry_confirm_pass.get()

            if not new_pass or not confirm_pass:
                messagebox.showerror("Error", "Fields cannot be empty.")
                return

            if new_pass != confirm_pass:
                messagebox.showerror("Error", "Passwords do not match.")
                return

            success, msg = user_handler.update_password(self.current_user, new_pass)
            if success:
                messagebox.showinfo("Success", msg)
                pass_win.destroy() 
            else:
                messagebox.showerror("Error", msg)

        btn_save = ctk.CTkButton(
            pass_win, 
            text="Save Password", 
            fg_color="transparent", 
            border_width=2, 
            border_color="#388E3C", 
            text_color="#81C784", 
            hover_color="#1B5E20", 
            corner_radius=6, 
            height=40, 
            command=attempt_update, 
            width=250
        )
        btn_save.pack(pady=(20, 10))

    # ================= AI PROMPT CUSTOMIZATION PORTAL =================
    def show_prompt_page(self):
        self.hide_all_frames()
        self.prompt_frame.pack(pady=0, padx=0, fill="both", expand=True)

        for widget in self.prompt_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.prompt_frame, height=60, corner_radius=0, fg_color=MAIN_BG_COLOR)
        header.pack(fill="x", side="top")

        btn_back = ctk.CTkButton(
            header, 
            text="◀ Back", 
            width=80, 
            fg_color="transparent", 
            border_width=1, 
            border_color=SECONDARY_BORDER, 
            text_color=TEXT_HIGHLIGHT, 
            hover_color=SECONDARY_HOVER, 
            command=self.show_admin_portal
        )
        btn_back.pack(side="left", padx=20, pady=15)

        lbl_title = ctk.CTkLabel(
            header, 
            text="AI Defense Strategy Configuration", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color=TEXT_HIGHLIGHT
        )
        lbl_title.pack(side="left", padx=20)

        content = ctk.CTkFrame(self.prompt_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=20)
        
        lbl_instruct = ctk.CTkLabel(
            content, 
            text="Customize the persona and instructions for the Local AI. Do not remove the [INSERT_TRACEBACK_LINK] placeholder.", 
            text_color="#A0B0C0"
        )
        lbl_instruct.pack(anchor="w", pady=(0, 10))

        prompt_box = ctk.CTkTextbox(
            content, 
            fg_color="#05080F", 
            text_color="#00FFCC", 
            border_width=1, 
            border_color="#2A3B4C", 
            font=ctk.CTkFont(family="Courier", size=13)
        )
        prompt_box.pack(fill="both", expand=True, pady=(0, 20))

        # Default fallback prompt
        default_prompt = (
            "You are a busy employee responding to an email. \n"
            "Read the sender's subject and message. Write a highly realistic, 2-to-4 sentence reply with paragraph breaks.\n\n"
            "Strategy: \n"
            "1. Fully accept the premise of their email to bait them.\n"
            "2. Invent a highly plausible, context-specific reason why you cannot complete their request using what they sent.\n"
            "3. Politely ask them to use your secure system to provide the information or verify the details: [INSERT_TRACEBACK_LINK]\n"
            "4. Be conversational and natural. Do not sound like a robot.\n"
            "5. Do not include subject lines or placeholders for names."
        )

        prompt_path = "config/ai_prompt.txt"

        # Load existing prompt if it exists
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                loaded_prompt = f.read()
                prompt_box.insert("end", loaded_prompt)
        else:
            prompt_box.insert("end", default_prompt)

        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.pack(fill="x")

        def save_prompt():
            os.makedirs('config', exist_ok=True)
            new_prompt = prompt_box.get("1.0", "end").strip()
            with open(prompt_path, "w", encoding="utf-8") as f:
                f.write(new_prompt)
            messagebox.showinfo("Success", "AI Defense Strategy successfully updated!")

        def reset_prompt():
            confirm = messagebox.askyesno("Reset Prompt", "Are you sure you want to restore the default AI instructions?")
            if confirm:
                prompt_box.delete("1.0", "end")
                prompt_box.insert("end", default_prompt)

        btn_save = ctk.CTkButton(
            btn_row, 
            text="💾 Save Strategy", 
            fg_color="transparent", 
            border_width=2, 
            border_color="#388E3C",  
            text_color="#81C784",    
            hover_color="#1B5E20",   
            height=40, 
            width=200, 
            font=ctk.CTkFont(weight="bold"), 
            corner_radius=6, 
            command=save_prompt
        )
        btn_save.pack(side="right", padx=(10, 0))

        btn_reset = ctk.CTkButton(
            btn_row, 
            text="🔄 Restore Default", 
            fg_color="transparent", 
            border_width=1, 
            border_color="#C62828", 
            text_color="#E57373", 
            hover_color="#4A1414", 
            height=40, 
            width=150, 
            corner_radius=6, 
            command=reset_prompt
        )
        btn_reset.pack(side="right")

# ================= INVESTIGATION UTILITIES =================
    def open_live_tracking_window(self):
        """Opens a dedicated window to monitor the deployed payload on a map for the specific target."""
        track_win = ctk.CTkToplevel(self)
        track_win.title(f"📡 Active Operation: {self.current_target_email}")
        
        # 🚀 1. Made the window wider to accommodate the detailed intercept panel
        track_win.geometry("1350x750") 
        track_win.configure(fg_color=MAIN_BG_COLOR)
        
        # --- Header & Controls ---
        header_frame = ctk.CTkFrame(track_win, fg_color="transparent")
        header_frame.pack(fill="x", pady=15, padx=20)
        
        lbl_title = ctk.CTkLabel(
            header_frame, 
            text=f"Tracking Target: {self.current_target_email}", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="#FF4C4C"
        )
        lbl_title.pack(side="left")
        
        btn_clear = ctk.CTkButton(
            header_frame, text="🗑️ Purge Target Data", width=140, 
            fg_color="#C62828", hover_color="#b71c1c",
            command=self.clear_map_data
        )
        btn_clear.pack(side="right", padx=(10, 0))
        
        btn_refresh = ctk.CTkButton(
            header_frame, text="🔄 Sync Radar", width=120,
            fg_color="transparent", border_width=1, border_color="#3B99C9", text_color="#60C6ED",
            command=self.update_live_intel
        )
        btn_refresh.pack(side="right")

        # 🚀 NEW: Forensic Report Export Button
        def trigger_export():
            # Pull the full metadata dictionary from memory (using .copy() to protect original)
            metadata_cache = getattr(self, 'current_email_metadata', {}).copy()
            
            # Fallback just in case the memory was cleared (e.g., app was restarted)
            if not metadata_cache:
                metadata_cache = {
                    'sender': self.current_target_email,
                    'receiver': "System User",
                    'date': "Recovered from Session Log",
                    'message_id': "Unavailable (Not Cached)",
                    'subject': "Intercepted via Honeypot Link",
                    'source_ip': "Refer to Interception Telemetry below",
                    'geo_location': "Refer to Interception Telemetry below",
                    'return_path': self.current_target_email,
                    'auth_results': "Original headers wiped from memory cache."
                }
            
            success, result = report_generator.generate_pdf_report(
                self.current_target_email, 
                metadata_cache, 
                investigator_name=self.current_user
            )
            
            if success:
                messagebox.showinfo("Export Success", f"Professional PDF Report generated successfully!\n\nSaved to:\n{result}")
                try: os.startfile(result) 
                except: pass
            else:
                messagebox.showerror("Export Failed", result)

        btn_export = ctk.CTkButton(
            header_frame, text="📄 Export Official Report (PDF)", width=200,
            fg_color="#1E88E5", hover_color="#1565C0", font=ctk.CTkFont(weight="bold"),
            command=trigger_export
        )
        btn_export.pack(side="right", padx=(0, 15))

        # --- Content Area (Map + Intercept Log) ---
        content_frame = ctk.CTkFrame(track_win, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Map Container (Left)
        map_card = ctk.CTkFrame(content_frame, fg_color="#151E2B", corner_radius=10, border_width=2, border_color="#3B99C9")
        map_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.map_widget = tkintermapview.TkinterMapView(map_card, corner_radius=10)
        self.map_widget.pack(fill="both", expand=True, padx=5, pady=5)
        self.map_widget.set_position(3.1390, 101.6869)
        self.map_widget.set_zoom(2)
        
        # 🚀 2. Wider & More Professional Intercept Container (Right)
        intercept_card = ctk.CTkFrame(content_frame, width=550, fg_color="#0A1520", corner_radius=10, border_width=1, border_color="#FF4C4C")
        intercept_card.pack(side="right", fill="y")
        intercept_card.pack_propagate(False) 

        lbl_intercept = ctk.CTkLabel(intercept_card, text="🚨 LIVE TARGET 🚨", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FF4C4C")
        lbl_intercept.pack(anchor="center", pady=(15, 5))

        # CHANGE THIS: Make the camera preview slightly larger to fit the wider box
        self.cam_label = ctk.CTkLabel(
            intercept_card, 
            text="[ No Camera Data ]", 
            width=320, 
            height=240, 
            fg_color="#030911", 
            corner_radius=8
        )

        self.cam_label.pack(pady=(5, 10)) # 🚀 THE FIX: This actually draws the camera on the screen!
        
        self.intercept_box = ctk.CTkTextbox(intercept_card, fg_color="#030911", text_color="#60C6ED", font=ctk.CTkFont(family="Courier", size=13))
        self.intercept_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.intercept_box.insert("end", "[*] LISTENING FOR BEACON...")
        self.intercept_box.configure(state="disabled")

        # Automatically pull data to populate the UI
        self.update_live_intel()

    def update_live_intel(self):
        """Pulls from the Flask JSON log and filters ONLY for the current target."""
        try:
            if not os.path.exists("captured_traces.json"): return

            with open("captured_traces.json", "r") as f:
                lines = f.readlines()
                
            if not lines: return
            
            # 🚀 1. Filter traces for THIS specific target
            target_traces = []
            for line in lines:
                try:
                    data = json.loads(line)
                    if data.get('target') == self.current_target_email:
                        target_traces.append(data)
                except Exception:
                    pass
            
            # Clear map before redrawing
            if hasattr(self, 'map_widget'):
                self.map_widget.delete_all_marker()
            
            # If the target hasn't clicked yet
            if not target_traces:

                if hasattr(self, 'cam_label'):
                    self.cam_label.configure(image="", text="[ No Camera Data ]", text_color="#A0B0C0")

                if hasattr(self, 'intercept_box'):
                    self.intercept_box.configure(state="normal")
                    self.intercept_box.delete("1.0", "end")
                    waiting_text = (
                        "===============================================================\n"
                        "                   ⏳ AWAITING CONNECTION\n"
                        "===============================================================\n\n"
                        f"🎯 TARGET : {self.current_target_email}\n"
                        f"📡 STATUS : Listening for payload interaction...\n"
                    )
                    self.intercept_box.insert("end", waiting_text)
                    self.intercept_box.configure(state="disabled")
                return

            # Plot all hits for this target
            for data in target_traces:
                if 'lat' in data and data['lat'] not in ["Pending Click", None]:
                    try:
                        lat, lon = float(data['lat']), float(data['lon'])
                        if hasattr(self, 'map_widget'):
                            self.map_widget.set_marker(lat, lon, text=f"Target: {data.get('timestamp')}")
                    except ValueError:
                        pass

            # 🚀 3. Professional SOC Layout for the Intercept Box
            last_trace = target_traces[-1]

            # Update the Camera Preview UI Image
            cam_file = last_trace.get('camera_file')
            if hasattr(self, 'cam_label'):
                if cam_file and os.path.exists(cam_file):
                    # Load the image using PIL and format it for CustomTkinter
                    ctk.CTkImage(light_image=Image.open(cam_file), dark_image=Image.open(cam_file), size=(280, 200))
                    self.cam_label.configure(image=imag, text="")
                else:
                    error_msg = last_trace.get('camera_error', '[ No Camera Data ]')
                    self.cam_label.configure(image="", text=error_msg, text_color="#E57373")
            
            if hasattr(self, 'intercept_box'):
                self.intercept_box.configure(state="normal")
                self.intercept_box.delete("1.0", "end")
                
                # 1. Calculate Camera Status for the text log
                if last_trace.get('camera_file'):
                    cam_status = "SUCCESS (Image Captured)"
                elif last_trace.get('camera_error'):
                    cam_status = f"FAILED ({last_trace.get('camera_error')})"
                else:
                    cam_status = "PENDING / UNAVAILABLE"

                # 2. Calculate GPS Status for the text log
                lat_val = last_trace.get('lat', 'N/A')
                lon_val = last_trace.get('lon', 'N/A')
                loc_error = last_trace.get('location_error', '')
                
                if loc_error:
                    gps_status = f"FAILED ({loc_error})"
                elif lat_val == "Pending Click":
                    gps_status = "PENDING (Pixel Opened Only)"
                else:
                    gps_status = "ACTIVE (High Precision)"

                # 3. Formatted Output (Perfectly aligned colons)
                intel_text = (
                    "===============================================================\n"
                    "                   🚨 LIVE TARGET INTERCEPT 🚨\n"
                    "===============================================================\n\n"
                    f"TARGET ID      : {last_trace.get('target', 'N/A')}\n"
                    f"TIMESTAMP      : {last_trace.get('timestamp', 'N/A')}\n"
                    f"EVENT TYPE     : {last_trace.get('type', 'N/A')}\n\n"
                    "---------------------------------------------------------------\n"
                    " 🌐 HARDWARE & SYSTEM FORENSICS\n"
                    "---------------------------------------------------------------\n"
                    f"IP ADDRESS     : {last_trace.get('ip_address', 'N/A')}\n"
                    f"PROCESSOR      : {last_trace.get('cpuCores', 'Unknown')} Cores | ~{last_trace.get('ramGb', 'Unknown')} GB RAM\n"
                    f"GRAPHICS (GPU) : {last_trace.get('gpu', 'Unknown')}\n"
                    f"PLATFORM       : {last_trace.get('platform', 'Unknown')} ({last_trace.get('isTouchDevice', 'Unknown')})\n"
                    f"BATTERY/POWER  : {last_trace.get('batteryLevel', 'Unknown')} | Charging: {last_trace.get('isCharging', 'Unknown')}\n\n"
                    "---------------------------------------------------------------\n"
                    " 📡 DISPLAY & BROWSER STATE\n"
                    "---------------------------------------------------------------\n"
                    f"RESOLUTION     : {last_trace.get('screen_res', 'Unknown')} @ {last_trace.get('colorDepth', 'Unknown')} (Scale: {last_trace.get('pixelRatio', '1')}x)\n"
                    f"OS THEME       : {last_trace.get('prefersDark', 'Unknown')}\n"
                    f"BROWSER        : {last_trace.get('browserVendor', 'Unknown')} (Cookies: {last_trace.get('cookiesEnabled', 'Unknown')})\n"
                    f"PRIVACY MODE   : Do-Not-Track is {last_trace.get('doNotTrack', 'Disabled')}\n"
                    f"CONNECTION     : {last_trace.get('networkType', 'Unknown')}\n"
                    f"TIMEZONE       : {last_trace.get('timezone', 'Unknown')} | Lang: {last_trace.get('language', 'Unknown')}\n"
                    f"USER-AGENT     : {last_trace.get('user_agent', 'Unknown')}\n\n"
                    "---------------------------------------------------------------\n"
                    " 📸 PERIPHERAL & LOCATION METRICS\n"
                    "---------------------------------------------------------------\n"
                    f"WEBCAM STATUS  : {cam_status}\n"
                    f"GPS STATUS     : {gps_status}\n"
                )
                
                # Append precise coordinates only if GPS was successful
                if gps_status == "ACTIVE (High Precision)":
                    intel_text += f"LATITUDE       : {lat_val}\n"
                    intel_text += f"LONGITUDE      : {lon_val}\n"
                    
                intel_text += "\n==============================================================="
                
                self.intercept_box.insert("1.0", intel_text)
                self.intercept_box.configure(state="disabled")

            # Center the map tightly on the latest GPS hit
            if 'lat' in last_trace and last_trace['lat'] not in ["Pending Click", None]:
                try:
                    if hasattr(self, 'map_widget'):
                        self.map_widget.set_position(float(last_trace['lat']), float(last_trace['lon']))
                        self.map_widget.set_zoom(15) # Closer zoom for accuracy
                except ValueError: pass
                    
        except Exception as e:
            print(f"Update Error: {e}")

    def clear_map_data(self):
        """Removes the tracking data ONLY for the current target, preserving others."""
        confirm = messagebox.askyesno(
            "Purge Target Data", 
            f"Are you sure you want to permanently delete all tracking logs for {self.current_target_email}?\n\nThis will not affect other targets."
        )
        if confirm:
            # 🚀 THE FIX 1: Wipe the target from the application's RAM (Memory)
            if hasattr(self, 'deployed_targets'):
                self.deployed_targets.discard(self.current_target_email)
                
            # 🚀 THE FIX 2: Instantly reset the Payload button in the background UI
            if hasattr(self, 'btn_payload'):
                self.btn_payload.configure(
                    state="normal", 
                    text="⚡ Prepare Traceback Payload", 
                    text_color="#E57373",
                    fg_color="transparent",
                    border_color="#C62828", 
                    hover_color="#4A1414"
                )

            # File clearing logic (Hard Drive)
            if os.path.exists("captured_traces.json"):
                with open("captured_traces.json", "r") as f:
                    lines = f.readlines()
                
                # Keep lines that DO NOT belong to the current target
                new_lines = []
                for line in lines:
                    try:
                        data = json.loads(line)
                        if data.get('target') != self.current_target_email:
                            new_lines.append(line)
                    except:
                        pass
                
                # Rewrite the JSON file without this target's traces
                with open("captured_traces.json", "w") as f:
                    f.writelines(new_lines)
                    
            # Refresh the UI to reflect the cleared state
            self.update_live_intel()

    def deploy_traceback_logic(self):
        deploy_handler.deploy_traceback(self)

# ================= REVERTED POPUP HUB (CARDS ONLY) =================
    def open_active_radars_hub(self):
        """Opens a detailed SOC hub popup listing active operations without the map."""
        hub_win = ctk.CTkToplevel(self)
        hub_win.title("Active Operations Hub")
        hub_win.geometry("750x600")
        hub_win.transient(self)
        hub_win.grab_set()
        hub_win.configure(fg_color=MAIN_BG_COLOR)

        header_frame = ctk.CTkFrame(hub_win, fg_color="#0A1520", corner_radius=0)
        header_frame.pack(fill="x", side="top")

        lbl_title = ctk.CTkLabel(header_frame, text="ACTIVE OPERATIONS HUB", font=ctk.CTkFont(size=18, weight="bold"), text_color="#FF4C4C")
        lbl_title.pack(pady=(15, 5))

        lbl_sub = ctk.CTkLabel(header_frame, text="Select an active payload below to monitor its live tracking radar.", text_color="#A0B0C0")
        lbl_sub.pack(pady=(0, 15))

        scroll_area = ctk.CTkScrollableFrame(hub_win, fg_color="transparent")
        scroll_area.pack(fill="both", expand=True, padx=20, pady=20)

        target_intel = {}
        if hasattr(self, 'deployed_targets'):
            for t in self.deployed_targets:
                target_intel[t] = {'hits': 0, 'last_seen': 'Awaiting Connection...', 'platform': 'Unknown'}

        if os.path.exists("captured_traces.json"):
            try:
                with open("captured_traces.json", "r") as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            target = data.get('target')
                            if target:
                                if target not in target_intel:
                                    target_intel[target] = {'hits': 0, 'platform': 'Unknown'}
                                target_intel[target]['hits'] += 1
                                target_intel[target]['last_seen'] = data.get('timestamp', 'Unknown')
                                if data.get('platform') and data.get('platform') != 'Unknown':
                                    target_intel[target]['platform'] = data.get('platform')
                        except: pass
            except: pass

        if not target_intel:
            ctk.CTkLabel(scroll_area, text="No active tracking operations found.", text_color="gray").pack(pady=40)
            return

        sorted_targets = sorted(target_intel.items(), key=lambda item: item[1]['hits'], reverse=True)
        for target, intel in sorted_targets:
            is_active = intel['hits'] > 0
            card = ctk.CTkFrame(scroll_area, fg_color="#1A0A0A" if is_active else "#1A1505", corner_radius=8, border_width=1, border_color="#FF4C4C" if is_active else "#F2A900")
            card.pack(fill="x", pady=5, ipady=5)

            # 🚀 Left Section: Merged Identity & Metrics Frame
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=15, pady=10)
            
            # Row 1 & 2: Target and Status
            ctk.CTkLabel(info_frame, text=f"🎯 {target}", font=ctk.CTkFont(size=15, weight="bold"), text_color="white").pack(anchor="w")
            ctk.CTkLabel(info_frame, text="🚨 ACTIVE COMPROMISE" if is_active else "⏳ PAYLOAD PENDING", font=ctk.CTkFont(size=11, weight="bold"), text_color="#FF4C4C" if is_active else "#F2A900").pack(anchor="w", pady=(2, 6)) # Added bottom padding

            # Row 3 & 4: Hits, OS, and Last Seen (Stacked beneath status)
            ctk.CTkLabel(info_frame, text=f"Hits: {intel['hits']}  |  OS: {intel['platform']}", font=ctk.CTkFont(size=12), text_color="#A0B0C0").pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Last Seen: {intel['last_seen']}", font=ctk.CTkFont(size=12), text_color="#A0B0C0").pack(anchor="w", pady=(2, 0))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=15, pady=10)
            ctk.CTkButton(btn_frame, text="📡 Open Radar", width=100, height=30, fg_color="#2E7D32", hover_color="#1B5E20", font=ctk.CTkFont(weight="bold"), command=lambda t=target: self.launch_radar_from_hub(t, hub_win)).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="🗑️ Purge", width=60, height=30, fg_color="transparent", border_width=1, border_color="#C62828", text_color="#E57373", hover_color="#4A1414", command=lambda t=target: self.quick_purge_from_hub(t, hub_win)).pack(side="left")

    def launch_radar_from_hub(self, target_email, hub_window):
        self.current_target_email = target_email
        hub_window.destroy()
        self.open_live_tracking_window()

    def quick_purge_from_hub(self, target_email, hub_window):
        confirm = messagebox.askyesno("Purge Data", f"Permanently delete all tracking data for {target_email}?")
        if confirm:
            self.current_target_email = target_email
            self.clear_map_data()
            hub_window.destroy()
            self.open_active_radars_hub()


if __name__ == "__main__":
    app = PhishTraceApp()
    app.mainloop()