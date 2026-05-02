import os
import random
from PIL import Image
import customtkinter as ctk

def play_auth_success_animation(root, container_frame, bg_color, on_complete_callback, logo_path="logo_single.jpg"):
    """
    Refined Hacker Animation:
    1. Logo/Name at the TOP.
    2. Smooth progress/decryption beat.
    3. Seamless transition directly into the portal.
    """
    # 1. Clear the login fields immediately
    for widget in container_frame.winfo_children():
        widget.destroy()
        
    # 2. Setup a master frame (Top-aligned for the new look)
    anim_frame = ctk.CTkFrame(container_frame, fg_color="transparent")
    anim_frame.pack(pady=(100, 0)) # Positioned towards the top

    # Logo and Text Container (MOVED TO TOP)
    logo_container = ctk.CTkFrame(anim_frame, fg_color="transparent")
    logo_container.pack(pady=(0, 20))
    
    lbl_logo = ctk.CTkLabel(
        logo_container, 
        text="", 
        text_color="#60C6ED", 
        font=ctk.CTkFont(size=45, weight="bold")
    )
    lbl_logo.pack(side="left")

    # Status Label
    lbl_status = ctk.CTkLabel(
        anim_frame, 
        text="[ AUTHENTICATING ]", 
        text_color="#F2A900", 
        font=ctk.CTkFont(family="Courier", size=16, weight="bold")
    )
    lbl_status.pack(pady=(0, 15))

    # Sleek Hacker Progress Bar
    progressbar = ctk.CTkProgressBar(anim_frame, width=350, height=4, fg_color="#0B111A", progress_color="#3B99C9")
    progressbar.pack(pady=(0, 30))
    progressbar.set(0)

    glitch_chars = "01!@#$%^&*<>?~[]{}|ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    target_text = " PhishTrace"
    has_logo = os.path.exists(logo_path)
    
    if has_logo:
        try:
            original_img = Image.open(logo_path).convert("RGBA").resize((70, 70)) 
        except Exception:
            has_logo = False

    def decrypt_text(step=0):
        """Phase 4: Decrypting the 'PhishTrace' text."""
        if step <= len(target_text) + 15:
            display_text = ""
            for i in range(len(target_text)):
                if i < step - 8: 
                    display_text += target_text[i]
                elif i < step: 
                    display_text += random.choice(glitch_chars)
                else:
                    display_text += random.choice(["0", "1", "-", "_", " "])
                    
            lbl_logo.configure(text=display_text)
            root.after(25, lambda: decrypt_text(step + 1))
        else:
            # 🚀 THE LANDING: Show success, then transition immediately
            lbl_logo.configure(text=target_text)
            lbl_status.configure(text="[ ACCESS GRANTED ]", text_color="#00FFCC")
            progressbar.configure(progress_color="#00FFCC")
            
            # ⏱️ SHORT BEAT: Wait just enough to see success, then transition
            root.after(600, lambda: [anim_frame.destroy(), on_complete_callback()])

    def draw_logo(current_h=1):
        """Phase 3: Smooth CRT scanline image reveal."""
        if not has_logo:
            lbl_logo.configure(text="🛡️")
            decrypt_text()
            return

        if current_h <= 70:
            bg = Image.new('RGBA', (70, 70), bg_color)
            cropped = original_img.crop((0, 0, 70, int(current_h)))
            bg.paste(cropped, (0, 0), cropped) 
            
            tk_img = ctk.CTkImage(bg, size=(70, 70))
            lbl_logo.configure(image=tk_img, compound="left")
            
            root.after(10, lambda: draw_logo(current_h + 3)) 
        else:
            decrypt_text()

    def fill_progress(val=0.0):
        """Phase 2: Animate progress bar and spinner."""
        if val < 1.0:
            progress = val + random.uniform(0.01, 0.08)
            if progress > 1.0: progress = 1.0
            progressbar.set(progress)

            spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            spinner_char = spinners[int((val * 100) % len(spinners))]
            lbl_status.configure(text=f"[ {spinner_char} AUTHENTICATING... ]")

            root.after(30, lambda: fill_progress(progress))
        else:
            lbl_status.configure(text="[ SECURING UPLINK ]", text_color="#60C6ED")
            progressbar.set(1.0)
            root.after(200, lambda: draw_logo(1))

    # Phase 1: Start
    root.after(100, fill_progress)