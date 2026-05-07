import os
import re
import base64
import joblib
import requests
import smtplib
from urllib.parse import urlparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ==========================================
# CONFIGURATION & GLOBALS
# ==========================================
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
MALICIOUS_LABEL = 1 

vectorizer = None
classifier = None


def load_ai_models():
    """Loads the trained machine learning models into memory."""
    global vectorizer, classifier
    try:
        vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
        classifier = joblib.load('models/phishing_rf_model.pkl')
    except Exception:
        vectorizer, classifier = None, None


# ==========================================
# GMAIL API AUTHENTICATION
# ==========================================
def authenticate_gmail(username):
    """Handles the OAuth2 flow and generates user-specific tokens."""
    creds = None
    token_path = f'config/token_{username}.json'
    creds_path = 'config/credentials.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        os.makedirs('config', exist_ok=True)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def check_connection(username):
    """Silently checks if a valid token exists for the given user."""
    token_path = f'config/token_{username}.json'
    
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if creds and creds.valid:
                return True
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                return True
        except Exception:
            pass
            
    return False


def connect_gmail_account(username):
    """Triggered by the UI to explicitly start the connection process."""
    creds_path = 'config/credentials.json'
    if not os.path.exists(creds_path):
        return False, "Missing config/credentials.json!"
    
    try:
        authenticate_gmail(username)
        return True, "Successfully connected to Gmail API!"
    except Exception as e:
        return False, f"Connection failed:\n{e}"


def disconnect_gmail_account(username):
    """Deletes the user's specific token to revoke local API access."""
    token_path = f'config/token_{username}.json'
    try:
        if os.path.exists(token_path):
            os.remove(token_path) 
        return True, "Successfully disconnected. You can now connect a different account."
    except Exception as e:
        return False, f"Failed to disconnect:\n{e}"


# ==========================================
# DATA PARSING & FORENSICS
# ==========================================
def get_email_body(payload):
    """Recursively extracts the plain-text body from the Gmail payload."""
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            elif 'parts' in part:
                body += get_email_body(part)
    elif payload['mimeType'] == 'text/plain':
        data = payload['body'].get('data', '')
        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
    return body


def clean_text(text):
    """Must be identical to the cleaner in email_handler.py!"""
    if not isinstance(text, str):
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # 🚀 THE FIX: Extract the domain from URLs before masking them
    def extract_domain(match):
        url = match.group(0)
        try:
            # Parse the URL to isolate just the domain (e.g., google.com)
            domain = urlparse(url).netloc
            if not domain:
                domain = url.split('/')[2] if '//' in url else url.split('/')[0]
            
            # Replace dots with spaces so TF-IDF treats 'google' and 'com' as words
            clean_domain = domain.replace('.', ' ')
            return f" httpaddr {clean_domain} "
        except:
            return " httpaddr "

    # Find all URLs and apply the domain extraction
    text = re.sub(r'(https?://[^\s]+)', extract_domain, text)
    
    # Mask email addresses
    text = re.sub(r'[^\s]+@[^\s]+', 'emailaddr', text)
    
    # Remove all non-alphabet characters
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = text.lower()
    
    # Collapse multiple spaces into one
    return re.sub(r'\s+', ' ', text).strip()


def get_geoip(ip):
    """Fetches the geographic location of an IP address using a free API."""
    if ip == "Unknown" or not ip:
        return "Unknown Location"
    
    # Ignore internal/private IPs
    if ip.startswith(("10.", "192.168.", "127.")) or (ip.startswith("172.") and 16 <= int(ip.split('.')[1]) <= 31):
        return "Private/Internal Network"

    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = response.json()
        
        if data.get("status") == "success":
            country = data.get("country", "Unknown")
            city = data.get("city", "Unknown")
            isp = data.get("isp", "Unknown")
            return f"{city}, {country} (ISP: {isp})"
    except Exception:
        pass
    
    return "Location Lookup Failed"

def send_html_email(recipient_email, subject, body, beacon_link, user_email, user_password):
    msg = MIMEMultipart()
    msg['From'] = user_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # This is the "Magic" HTML wrapper for your GIF
    html_body = f"""
    <html>
    <body>
        <p>{body}</p>
        <br>
        <p><strong>System Security Link:</strong> <a href="{beacon_link}">{beacon_link}</a></p>
        <br>
        <p><em>Security Image Verification:</em></p>
        <a href="{beacon_link}">
            <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ4eHh4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxxHOGTdzJC/giphy.gif" alt="Click to Verify">
        </a>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html'))

    # Standard SMTP sending logic
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user_email, user_password)
    server.send_message(msg)
    server.quit()
    return True, "Payload dispatched successfully."

def send_reply_via_api(username, to_email, subject, html_content):
    """Sends the HTML payload through the authenticated user's Gmail API."""
    try:
        # 🚀 THE FIX: authenticate_gmail already returns the 'service' object!
        service = authenticate_gmail(username) 
        
        if not service:
            return False, "Gmail API not connected. Please connect your account in the dashboard."

        # 1. Build the HTML Email
        message = MIMEMultipart()
        message['To'] = to_email
        message['Subject'] = subject
        message.attach(MIMEText(html_content, 'html'))
        
        # 2. Google API requires base64url encoding
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # 3. Send it using the pre-built service!
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        
        return True, "Payload dispatched successfully via API."
        
    except Exception as e:
        return False, f"API Error: {str(e)}"

# ==========================================
# CORE INBOX SCANNER
# ==========================================
def fetch_and_analyze_inbox(username, max_emails=5):
    """Fetches recent emails, extracts metadata, and runs ML classification."""
    load_ai_models()
    
    try:
        service = authenticate_gmail(username)
    except Exception as e:
        return [{"error": f"Gmail Authentication Failed:\n{e}"}]

    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_emails).execute()
    messages = results.get('messages', [])
    
    if not messages:
        return []

    processed_emails = []

    for msg_info in messages:
        msg = service.users().messages().get(userId='me', id=msg_info['id'], format='full').execute()
        headers = msg['payload']['headers']
        
        # Default header values
        sender, receiver = "Unknown", "Unknown"
        subject, date = "No Subject", "Unknown"
        return_path, message_id, auth_results = "None", "None", "None"
        received_chain = []

        # Extract specific headers
        for header in headers:
            name = header['name'].lower()
            val = header['value']
            
            if name == 'from': sender = val
            elif name == 'to': receiver = val
            elif name == 'subject': subject = val
            elif name == 'date': date = val
            elif name == 'return-path': return_path = val
            elif name == 'message-id': message_id = val
            elif name == 'authentication-results': auth_results = val
            elif name == 'received': received_chain.append(val)

        # Extract Origin IP from the earliest 'Received' header
        source_ip = "Unknown"
        geo_location = "Unknown Location"
        
        if received_chain:
            earliest_received = received_chain[-1]
            ip_matches = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', earliest_received)
            if ip_matches: 
                source_ip = ip_matches[0]
                geo_location = get_geoip(source_ip)

        # Extract and clean body
        raw_body = get_email_body(msg['payload'])
        if not raw_body: 
            raw_body = msg.get('snippet', '')
            
        content_text = clean_text(raw_body)

        # ==========================================
        # 🧠 RESTORED: MACHINE LEARNING CLASSIFICATION
        # ==========================================
        status = "NORMAL"
        ai_reply = "No traceback action required."
        confidence_score = 0
        
        # Run Machine Learning Classification
        if vectorizer and classifier:
            vectorized_text = vectorizer.transform([content_text])
            
            prediction = classifier.predict(vectorized_text)[0]
            probabilities = classifier.predict_proba(vectorized_text)[0]
            
            prob_0 = probabilities[0] * 100
            prob_1 = probabilities[1] * 100

            if prediction == MALICIOUS_LABEL: 
                status = "MALICIOUS"
                confidence_score = prob_1 if MALICIOUS_LABEL == 1 else prob_0
                ai_reply = "Awaiting Investigator Selection..." 
            else:
                status = "NORMAL"
                confidence_score = prob_0 if MALICIOUS_LABEL == 1 else prob_1
                ai_reply = f"✅ SECURE (Confidence: {confidence_score:.1f}%)\n\nThe AI model has classified this text as benign. No traceback recommended."
        else:
            status = "ERROR"
            ai_reply = "AI Models not found. Please train the dataset first!"


        # We are now passing the RAW variables to the GUI!
        processed_emails.append({
            "date": date,
            "sender": sender,
            "receiver": receiver,
            "subject": subject,
            "source_ip": source_ip,
            "geo_location": geo_location,
            "return_path": return_path,
            "message_id": message_id,
            "auth_results": auth_results,
            "status": status,
            "ai": ai_reply,
            "body": content_text, 
            "confidence": confidence_score
        })

    return processed_emails