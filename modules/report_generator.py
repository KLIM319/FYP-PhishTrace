import os
import json
import hashlib
from datetime import datetime
from fpdf import FPDF

class ForensicReport(FPDF):
    def header(self):
        # 🚀 NEW: Diagonal "STRICTLY CONFIDENTIAL" Watermark
        self.set_font("helvetica", "B", 65)
        self.set_text_color(245, 245, 245) # Very faint gray
        
        # Rotate the text 45 degrees across the center of the page
        with self.rotation(45, x=105, y=148):
            self.text(20, 180, "CONFIDENTIAL")
            
        # Standard Header Text (Restoring normal font and color)
        self.set_font("helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, "CONFIDENTIAL - EXPERT FORENSIC TRACEBACK REPORT", border=False, align="C")
        self.ln(10)

    def footer(self):
        # Page numbers and generation timestamp
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        # 🚀 NEW: Added the exact print time to the footer
        footer_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  Page {self.page_no()}"
        self.cell(0, 10, footer_text, align="C")

def generate_pdf_report(target_email, email_metadata, investigator_name="Lead Investigator"):
    """Generates a court-ready PDF report with strict pagination and complete evidence extraction."""
    
    # 1. Gather Target Traces
    target_traces = []
    if os.path.exists("captured_traces.json"):
        with open("captured_traces.json", "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get('target') == target_email:
                        target_traces.append(data)
                except: pass

    if not target_traces:
        return False, "No active telemetry data found for this target."

    last_trace = target_traces[-1]
    case_number = f"CASE-{datetime.now().strftime('%Y%m%d-%H%M')}"
    
    # Generate SHA-256 Hash of the log file for Chain of Custody
    sha256_hash = "FILE_MISSING"
    if os.path.exists("captured_traces.json"):
        with open("captured_traces.json", "rb") as f:
            sha256_hash = hashlib.sha256(f.read()).hexdigest()

    # ==========================================
    # TITLE PAGE (PAGE 1)
    # ==========================================
    pdf = ForensicReport()
    pdf.add_page()
    
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(200, 50, 50) # Dark Red for impact
    pdf.ln(30)
    pdf.cell(0, 10, "DIGITAL FORENSIC INCIDENT REPORT", align="C")
    pdf.ln(20)
    
    pdf.set_font("helvetica", "", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Case Reference : {case_number}", align="C")
    pdf.ln(8)
    pdf.cell(0, 10, f"Target Identity : {target_email}", align="C")
    pdf.ln(8)
    pdf.cell(0, 10, f"Date Extracted : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", align="C")
    pdf.ln(8)
    pdf.cell(0, 10, f"Extracted By : {investigator_name}", align="C")
    
    # ==========================================
    # PART 1: EXECUTIVE SUMMARY (PAGE 2)
    # ==========================================
    pdf.add_page() # 🚀 FORCED NEW PAGE
    pdf.set_font("helvetica", "B", 16)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(0, 10, " PART 1: EXECUTIVE SUMMARY", border=True, fill=True, align="L")
    pdf.ln(15)
    
    pdf.set_font("helvetica", "", 11)
    summary_text = (
        f"On {datetime.now().strftime('%B %d, %Y')}, a reverse-traceback operation was authorized against "
        f"the target known as '{target_email}'. The target interacted with the deployed honeypot payload, "
        f"allowing the system to successfully capture live geographic, network, hardware, and browser telemetry. "
        f"This document serves as the official, unaltered forensic extraction of those events and the associated email metadata."
    )
    pdf.multi_cell(0, 8, summary_text)

    # ==========================================
    # PART 2: EMAIL METADATA (PAGE 3)
    # ==========================================
    pdf.add_page() # 🚀 FORCED NEW PAGE
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, " PART 2: EMAIL FORENSIC METADATA", border=True, fill=True, align="L")
    pdf.ln(10)
    
    if email_metadata:
        # 2.1 Primary Routing & Identity
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(50, 50, 150)
        pdf.cell(0, 8, "2.1 Primary Routing & Identity Indicators", ln=True)
        pdf.set_text_color(0, 0, 0)
        
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "Sender (From):", border=0); pdf.set_font("helvetica", "", 10); pdf.cell(0, 6, str(email_metadata.get('sender', 'N/A')), ln=True)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "Recipient (To):", border=0); pdf.set_font("helvetica", "", 10); pdf.cell(0, 6, str(email_metadata.get('receiver', 'N/A')), ln=True)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "Date/Time:", border=0); pdf.set_font("helvetica", "", 10); pdf.cell(0, 6, str(email_metadata.get('date', 'N/A')), ln=True)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "Message-ID:", border=0); pdf.set_font("helvetica", "", 10); pdf.cell(0, 6, str(email_metadata.get('message_id', 'N/A')), ln=True)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "Subject:", border=0); pdf.set_font("helvetica", "", 10); pdf.multi_cell(0, 6, str(email_metadata.get('subject', 'N/A')))
        pdf.ln(5)

        # 2.2 Security & Protocol Authentication
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(50, 50, 150)
        pdf.cell(0, 8, "2.2 Security & Protocol Authentication", ln=True)
        pdf.set_text_color(0, 0, 0)

        auth_raw = str(email_metadata.get('auth_results', 'N/A'))
        spf_status = "PASS" if "spf=pass" in auth_raw.lower() else ("FAIL" if "spf=fail" in auth_raw.lower() else "UNVERIFIED")
        dkim_status = "PASS" if "dkim=pass" in auth_raw.lower() else ("FAIL" if "dkim=fail" in auth_raw.lower() else "UNVERIFIED")
        dmarc_status = "PASS" if "dmarc=pass" in auth_raw.lower() else ("FAIL" if "dmarc=fail" in auth_raw.lower() else "UNVERIFIED")

        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "SPF Status:", border=0); pdf.set_font("helvetica", "", 10); pdf.cell(0, 6, spf_status, ln=True)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "DKIM Status:", border=0); pdf.set_font("helvetica", "", 10); pdf.cell(0, 6, dkim_status, ln=True)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "DMARC Status:", border=0); pdf.set_font("helvetica", "", 10); pdf.cell(0, 6, dmarc_status, ln=True)
        
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "Raw Headers:", border=0); pdf.set_font("helvetica", "", 9)
        pdf.multi_cell(0, 5, auth_raw.replace(';', ';\n'))
        pdf.ln(5)

        # 2.3 Origin Infrastructure
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(50, 50, 150)
        pdf.cell(0, 8, "2.3 Origin Infrastructure Details", ln=True)
        pdf.set_text_color(0, 0, 0)

        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "Origin IP:", border=0); pdf.set_font("helvetica", "", 10); pdf.cell(0, 6, str(email_metadata.get('source_ip', 'N/A')), ln=True)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "Geo-Location:", border=0); pdf.set_font("helvetica", "", 10); pdf.cell(0, 6, str(email_metadata.get('geo_location', 'N/A')), ln=True)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "Return-Path:", border=0); pdf.set_font("helvetica", "", 10); pdf.cell(0, 6, str(email_metadata.get('return_path', 'N/A')), ln=True)
        pdf.ln(5)

        # 🚀 NEW: 2.4 AI Classification & Content
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(50, 50, 150)
        pdf.cell(0, 8, "2.4 AI Classification & Content Extract", ln=True)
        pdf.set_text_color(0, 0, 0)

        ml_status = str(email_metadata.get('status', 'UNSCANNED'))
        ml_conf = str(email_metadata.get('confidence', 'N/A'))
        body_extract = str(email_metadata.get('body', 'No content extractable.'))
        
        # If body is massively long, truncate it for the PDF
        if len(body_extract) > 1000: body_extract = body_extract[:1000] + "\n\n[... CONTENT TRUNCATED FOR REPORT ...]"

        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "Threat Status:", border=0); pdf.set_font("helvetica", "", 10); pdf.cell(0, 6, ml_status, ln=True)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 6, "AI Confidence:", border=0); pdf.set_font("helvetica", "", 10); pdf.cell(0, 6, f"{ml_conf}%", ln=True)
        
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 6, "Plaintext Body Extraction:", ln=True)
        pdf.set_font("helvetica", "", 9)
        pdf.multi_cell(0, 5, body_extract, border=1)
        
    else:
        pdf.set_font("helvetica", "", 11)
        pdf.multi_cell(0, 8, "Email metadata was missing or unavailable during PDF compilation.")

    # ==========================================
    # PART 3: INTERCEPTION TELEMETRY (PAGE 4)
    # ==========================================
    pdf.add_page() # 🚀 FORCED NEW PAGE
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, " PART 3: LIVE TARGET INTERCEPTION", border=True, fill=True, align="L")
    pdf.ln(10)
    
    # 🚀 ENHANCED: 3.1 Network & Session
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(50, 50, 150)
    pdf.cell(0, 8, "3.1 Network & Session Verification", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(50, 8, "Captured IP:", border=1); pdf.cell(0, 8, f" {last_trace.get('ip_address', 'Unknown')}", border=1, ln=True)
    pdf.cell(50, 8, "Network Type:", border=1); pdf.cell(0, 8, f" {last_trace.get('networkType', 'Unknown')}", border=1, ln=True)
    pdf.cell(50, 8, "Event Timestamp:", border=1); pdf.cell(0, 8, f" {last_trace.get('timestamp', 'Unknown')}", border=1, ln=True)
    pdf.cell(50, 8, "Interaction Type:", border=1); pdf.cell(0, 8, f" {last_trace.get('type', 'Unknown')}", border=1, ln=True)
    pdf.ln(5)

    # 🚀 ENHANCED: 3.2 Hardware Footprint
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(50, 50, 150)
    pdf.cell(0, 8, "3.2 Target Hardware Footprint", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(50, 8, "Operating System:", border=1); pdf.cell(0, 8, f" {last_trace.get('platform', 'Unknown')}", border=1, ln=True)
    pdf.cell(50, 8, "Logical Processors:", border=1); pdf.cell(0, 8, f" {last_trace.get('cpuCores', 'Unknown')} Cores", border=1, ln=True)
    pdf.cell(50, 8, "Estimated RAM:", border=1); pdf.cell(0, 8, f" {last_trace.get('ramGb', 'Unknown')} GB", border=1, ln=True)
    pdf.cell(50, 8, "Graphics (GPU):", border=1); pdf.cell(0, 8, f" {str(last_trace.get('gpu', 'Unknown'))[:70]}", border=1, ln=True) # Trim to fit cell
    pdf.cell(50, 8, "Touchscreen:", border=1); pdf.cell(0, 8, f" {last_trace.get('isTouchDevice', 'Unknown')}", border=1, ln=True)
    pdf.cell(50, 8, "Battery Status:", border=1); pdf.cell(0, 8, f" Level: {last_trace.get('batteryLevel', 'Unknown')} | Charging: {last_trace.get('isCharging', 'Unknown')}", border=1, ln=True)
    pdf.ln(5)

    # 🚀 ENHANCED: 3.3 Display & Browser State
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(50, 50, 150)
    pdf.cell(0, 8, "3.3 Browser & Display Configuration", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(50, 8, "Resolution:", border=1); pdf.cell(0, 8, f" {last_trace.get('screen_res', 'Unknown')} @ {last_trace.get('colorDepth', 'Unknown')}-bit", border=1, ln=True)
    pdf.cell(50, 8, "Pixel Scale / Theme:", border=1); pdf.cell(0, 8, f" {last_trace.get('pixelRatio', '1')}x Scale | Mode: {last_trace.get('prefersDark', 'Unknown')}", border=1, ln=True)
    pdf.cell(50, 8, "Browser Engine:", border=1); pdf.cell(0, 8, f" {last_trace.get('browserVendor', 'Unknown')}", border=1, ln=True)
    pdf.cell(50, 8, "Cookies / DNT:", border=1); pdf.cell(0, 8, f" Cookies: {last_trace.get('cookiesEnabled', 'Unknown')} | DNT: {last_trace.get('doNotTrack', 'Unknown')}", border=1, ln=True)
    pdf.cell(50, 8, "Language & Timezone:", border=1); pdf.cell(0, 8, f" {last_trace.get('language', 'Unknown')} | {last_trace.get('timezone', 'Unknown')}", border=1, ln=True)
    pdf.ln(5)

    # 🚀 ENHANCED: 3.4 Geolocation
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(50, 50, 150)
    pdf.cell(0, 8, "3.4 Geometric Coordinates", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("helvetica", "", 10)
    loc_err = last_trace.get('location_error', '')
    if loc_err:
        pdf.cell(50, 8, "GPS Status:", border=1); pdf.cell(0, 8, f" FAILED: {loc_err}", border=1, ln=True)
    else:
        pdf.cell(50, 8, "GPS Latitude:", border=1); pdf.cell(0, 8, f" {last_trace.get('lat', 'Unknown')}", border=1, ln=True)
        pdf.cell(50, 8, "GPS Longitude:", border=1); pdf.cell(0, 8, f" {last_trace.get('lon', 'Unknown')}", border=1, ln=True)
    pdf.ln(5)
    
    # User Agent Block
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "Raw User-Agent String:")
    pdf.ln(6)
    pdf.set_font("helvetica", "", 10)
    pdf.multi_cell(0, 6, last_trace.get('user_agent', 'Unknown'), border=1)

    # ==========================================
    # PART 4: CHAIN OF CUSTODY (PAGE 5)
    # ==========================================
    pdf.add_page() # 🚀 FORCED NEW PAGE
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, " PART 4: DIGITAL EVIDENCE CHAIN OF CUSTODY", border=True, fill=True, align="L")
    pdf.ln(10)
    
    pdf.set_font("helvetica", "", 11)
    coc_text = (
        "To ensure admissibility under digital evidence frameworks, the raw telemetry logs "
        "have been cryptographically hashed. Any alteration to the original capture file will result "
        "in a different hash value, proving the current data integrity has not been tampered with."
    )
    pdf.multi_cell(0, 8, coc_text)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "File Assessed: captured_traces.json")
    pdf.ln(6)
    pdf.set_font("helvetica", "I", 10)
    pdf.cell(0, 8, f"SHA-256 Hash: {sha256_hash}")

    # ==========================================
    # APPENDIX: CAMERA CAPTURE (PAGE 6 IF EXISTS)
    # ==========================================
    cam_file = last_trace.get('camera_file')
    if cam_file and os.path.exists(cam_file):
        pdf.add_page() # 🚀 FORCED NEW PAGE
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, " APPENDIX A: CAMERA CAPTURE", border=True, fill=True, align="L")
        pdf.ln(15)
        pdf.image(cam_file, x=50, w=110)
        
    # ==========================================
    # 🚀 NEW: APPENDIX: GEOGRAPHIC MAPPING (TRIPLE LOCAL OSM)
    # ==========================================
    lat = last_trace.get('lat')
    lon = last_trace.get('lon')
    
    # Only draw the map if we successfully captured real coordinates
    if lat and lon and lat not in ["Pending Click", "Unknown", None]:
        try:
            pdf.add_page()
            pdf.set_font("helvetica", "B", 16)
            
            app_title = " APPENDIX B: GEOGRAPHIC MAPPING" if (cam_file and os.path.exists(cam_file)) else " APPENDIX A: GEOGRAPHIC MAPPING"
            pdf.cell(0, 10, app_title, border=True, fill=True, align="L")
            pdf.ln(10)
            
            # Use pure OpenStreetMap and render it locally!
            from staticmap import StaticMap, CircleMarker
            
            # 1. Initialize a 600x450 map environment
            m = StaticMap(600, 450, url_template='https://a.tile.openstreetmap.org/{z}/{x}/{y}.png')
            
            # 2. Create the target marker
            marker = CircleMarker((float(lon), float(lat)), '#FF4C4C', 10)
            m.add_marker(marker)
            
            # 3. Render THREE maps at cascading zoom levels
            image_country = m.render(zoom=5)  # Country Level
            image_state   = m.render(zoom=13) # State/Region Level
            image_street  = m.render(zoom=17) # Street/Building Level
            
            os.makedirs("reports", exist_ok=True)
            country_path = f"reports/temp_country_{datetime.now().strftime('%H%M%S')}.png"
            state_path   = f"reports/temp_state_{datetime.now().strftime('%H%M%S')}.png"
            street_path  = f"reports/temp_street_{datetime.now().strftime('%H%M%S')}.png"
            
            image_country.save(country_path)
            image_state.save(state_path)
            image_street.save(street_path)
            
            # 4. Embed the COUNTRY map
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(50, 50, 150)
            pdf.cell(0, 8, "Level 1: Country View (Macro)", ln=True)
            pdf.image(country_path, x=40, w=130) # w=130 and x=40 perfectly centers the image on an A4 page
            pdf.ln(5)
            
            # 5. Embed the STATE map
            pdf.cell(0, 8, "Level 2: State/Regional View (Meso)", ln=True)
            pdf.image(state_path, x=40, w=130)
            pdf.ln(5)
            
            # 🚀 Force a clean page break so the street view doesn't get cut off!
            pdf.add_page() 
            
            # 6. Embed the STREET map
            pdf.set_text_color(50, 50, 150)
            pdf.cell(0, 8, "Level 3: Street View (Micro Precision)", ln=True)
            pdf.image(street_path, x=40, w=130)
            pdf.ln(5)
            
            # Add coordinate label beneath the final map
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 8, f"Confirmed Telemetry Coordinates: Latitude {lat}, Longitude {lon}", align="C")
            
            # Clean up and delete the temporary image files
            if os.path.exists(country_path): os.remove(country_path)
            if os.path.exists(state_path): os.remove(state_path)
            if os.path.exists(street_path): os.remove(street_path)
                
        except ImportError:
            pdf.set_font("helvetica", "", 11)
            pdf.cell(0, 10, "SYSTEM ERROR: Run 'pip install staticmap' in terminal to enable OSM mapping.")
        except Exception as e:
            pdf.set_font("helvetica", "", 11)
            pdf.cell(0, 10, f"Local OpenStreetMap generation failed: {e}")

    # ==========================================
    # 🚀 NEW: PART 5: INVESTIGATOR DECLARATION (FINAL PAGE)
    # ==========================================
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, " PART 5: DECLARATION OF AUTHENTICITY", border=True, fill=True, align="L")
    pdf.ln(15)
    
    pdf.set_font("helvetica", "", 11)
    declaration_text = (
        f"I, {investigator_name}, hereby declare that the digital evidence enclosed within this report "
        f"(Case Reference: {case_number}) was acquired, preserved, and extracted using the PhishTrace "
        f"telemetry framework. \n\n"
        f"I certify that the cryptographic hashes generated for the raw data logs accurately reflect the "
        f"state of the evidence at the time of extraction, and that no unauthorized modifications have "
        f"been made to the telemetry or the associated mapping records. The findings presented herein "
        f"represent a true and accurate technical assessment of the automated traceback operation."
    )
    pdf.multi_cell(0, 8, declaration_text)
    pdf.ln(25)
    
    # Signature Block
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(80, 8, "____________________________________", ln=True)
    pdf.cell(80, 6, "Signature of Lead Investigator", ln=True)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(80, 6, f"Name: {investigator_name}", ln=True)
    pdf.cell(80, 6, f"Date: {datetime.now().strftime('%B %d, %Y')}", ln=True)
    pdf.cell(80, 6, "System User Authority: Admin/SOC Analyst", ln=True)        

    # ==========================================
    # FILE SAVING LOGIC
    # ==========================================
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/Forensic_Report_{target_email.split('@')[0]}_{datetime.now().strftime('%H%M%S')}.pdf"
    pdf.output(filename)
    
    return True, filename