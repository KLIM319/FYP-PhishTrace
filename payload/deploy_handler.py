import threading
import urllib.parse
import customtkinter as ctk 
from tkinter import messagebox
from modules import email_handler
from payload import server_handler

def deploy_traceback(app):
    """
    Orchestrates a coordinated 'Reverse-Traceback Operation'.
    Features: professional HTML templates and non-blocking API dispatch.
    """
    if not hasattr(app, 'current_target_email'):
        messagebox.showerror("Deployment Failed", "No active target identified in the Threat Feed.")
        return

    # 🚀 STRICT MANUAL INFRASTRUCTURE CHECK
    is_online, current_url = server_handler.check_status()
    
    if not is_online or current_url == "Offline":
        messagebox.showerror(
            "Infrastructure Offline", 
            "The tracking servers are currently offline.\n\nPlease go to the top right dropdown menu and click '▶ Start' before deploying a payload."
        )
        # Ensure the button resets so they can try again
        app.btn_payload.configure(
            text="⚡ Prepare Traceback Payload", 
            state="normal",
            fg_color="transparent",
            border_color="#C62828"
        )
        return

    NGROK_URL = current_url # Use the already running Ngrok link!

    # 🧹 AI STRATEGY CLEANUP
    raw_text = app.ai_box.get("1.0", "end")
    try:
        # Isolate the AI generated text from the GUI headers
        ai_strategy = raw_text.split("==================================================")[1].strip()
    except IndexError:
        ai_strategy = raw_text.strip()

    # Replace placeholder with a context-aware hyperlink
    encoded_target = urllib.parse.quote(app.current_target_email)
    TRAP_LINK = f"{NGROK_URL}/trap?target={encoded_target}"
    PIXEL_LINK = f"{NGROK_URL}/trace_pixel?target={encoded_target}"

    # 🚀 THE FIX: Mask the raw URL with a professional clickable HTML tag
    MASKED_LINK = f'<a href="{TRAP_LINK}" style="color: #0078D4; text-decoration: underline; font-weight: bold;">Here</a>'

    # 📧 BEAUTIFIED HTML TEMPLATE (Mimics a Corporate Security Portal)
    html_payload = f"""
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; margin-top: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <tr>
                <td align="center" style="padding: 40px 0 30px 0; background-color: #1a2634; border-radius: 8px 8px 0 0;">
                    <h1 style="color: #60C6ED; margin: 0; font-size: 24px; letter-spacing: 2px;">SECURE ACCESS GATEWAY</h1>
                </td>
            </tr>
            <tr>
                <td style="padding: 40px 30px 40px 30px;">
                    <p style="font-size: 16px; color: #333333; line-height: 1.6;">
                        {ai_strategy.replace("[INSERT_TRACEBACK_LINK]", MASKED_LINK)}
                    </p>
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 30px;">
                        <tr>
                            <td align="center">
                                <a href="{TRAP_LINK}" style="background-color: #3B99C9; color: #ffffff; padding: 15px 25px; text-decoration: none; font-weight: bold; border-radius: 4px; display: inline-block;">
                                    CLICK HERE TO PROCEED
                                </a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td style="padding: 20px 30px; background-color: #f9f9f9; color: #888888; font-size: 12px; text-align: center; border-radius: 0 0 8px 8px;">
                    This is an automated security measure. PhishTrace &copy; 2026.
                </td>
            </tr>
        </table>
        <img src="{PIXEL_LINK}" width="2" height="2" alt="spacer" style="opacity:0.01; border:0; position:absolute; z-index:-1;" />
    </body>
    </html>
    """

    # 🚀 NEW: Payload Review & Edit Window
    review_win = ctk.CTkToplevel(app)
    review_win.title("Review Traceback Payload")
    review_win.geometry("750x650")
    review_win.transient(app) # Keeps window on top of main app
    review_win.grab_set()     # Blocks interaction with main app until closed

    lbl_title = ctk.CTkLabel(
        review_win, 
        text=f"Review & Edit HTML Payload for {app.current_target_email}", 
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="#60C6ED"
    )
    lbl_title.pack(pady=(20, 10))

    # The editable text box
    editor_box = ctk.CTkTextbox(
        review_win, 
        width=700, 
        height=450, 
        font=ctk.CTkFont(family="Courier", size=13),
        fg_color="#05080F",
        text_color="#A0B0C0",
        border_width=1,
        border_color="#2A3B4C"
    )
    editor_box.pack(padx=20, pady=10, fill="both", expand=True)
    editor_box.insert("1.0", html_payload.strip())

    def confirm_and_send():
        # Get the final edited HTML from the text box
        final_html = editor_box.get("1.0", "end").strip()
        review_win.destroy()
        
        # Visual feedback on the UI
        app.btn_payload.configure(text="🚀 PAYLOAD IN-FLIGHT...", state="disabled", fg_color="#F2A900")
        
        def background_send():
            success, msg = email_handler.send_reply_via_api(
                app.current_user, 
                app.current_target_email, 
                "RE: Verification Required - Internal Asset Request", 
                final_html
            )
            
            if success:
                # 🚀 THE FIX: Remember that we deployed a payload to this specific target
                if not hasattr(app, 'deployed_targets'):
                    app.deployed_targets = set()
                app.deployed_targets.add(app.current_target_email)

                app.after(0, lambda: messagebox.showinfo("Mission Success", "Traceback payload successfully deployed.\nInitiating Tracking Radar..."))
                
                # Transform the button into a "Reopen Radar" button
                def morph_to_radar_button():
                    app.btn_payload.configure(
                        text="📡 OPEN LIVE RADAR", 
                        fg_color="#2E7D32", 
                        hover_color="#1B5E20",
                        border_color="#2E7D32", 
                        text_color="white",
                        state="normal"
                    )
                app.after(0, morph_to_radar_button)
                
                app.after(0, app.open_live_tracking_window)
            else:
                app.after(0, lambda: messagebox.showerror("Mission Aborted", f"API Error during deployment:\n{msg}"))
                app.after(0, lambda: app.btn_payload.configure(text="⚡ DEPLOY TRACEBACK", state="normal", fg_color="transparent"))

        threading.Thread(target=background_send, daemon=True).start()

    # Deploy Button
    btn_deploy = ctk.CTkButton(
        review_win, 
        text="🚀 CONFIRM & DEPLOY TRACEBACK", 
        height=50, 
        font=ctk.CTkFont(size=15, weight="bold"), 
        fg_color="#C62828", 
        hover_color="#4A1414", 
        command=confirm_and_send
    )
    btn_deploy.pack(pady=(10, 20), fill="x", padx=20)