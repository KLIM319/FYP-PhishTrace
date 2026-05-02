import os
import pandas as pd
import joblib
import datetime
import csv
import re
from urllib.parse import urlparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

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

def train_and_save_model(dataset_path, log_callback=None):
    def log(msg):
        if log_callback: log_callback(msg)
        else: print(msg)

    if not os.path.exists(dataset_path):
        return False, f"Could not find '{dataset_path}'."

    try:
        log(f"[*] Locating dataset at: {dataset_path}...")
        df = pd.read_csv(dataset_path, low_memory=False)
        
        # 🚀 FIX 1: Auto-Detect Columns (Normalize to lowercase and strip spaces)
        df.columns = df.columns.str.lower().str.strip()
        
        # Common names for the email/text column
        text_aliases = ['body', 'text', 'content', 'message', 'email', 'email_text', 'v2']
        # Common names for the target/label column
        label_aliases = ['label', 'target', 'class', 'is_phishing', 'spam', 'phishing', 'v1']

        found_body_col = next((col for col in text_aliases if col in df.columns), None)
        found_label_col = next((col for col in label_aliases if col in df.columns), None)

        if not found_body_col or not found_label_col:
            found_cols = list(df.columns)
            return False, f"Error: Could not identify text or label columns.\nExpected aliases like 'text', 'body', 'label'.\nFound in CSV: {found_cols}"

        log(f"[*] Auto-Mapped Columns: Text -> '{found_body_col}', Label -> '{found_label_col}'")
        
        # Rename columns to standard 'body' and 'label' so the rest of the code works flawlessly
        df = df.rename(columns={found_body_col: 'body', found_label_col: 'label'})

        log("[*] Cleaning blank rows...")
        df = df.dropna(subset=['body', 'label'])

        # 🚀 FIX 2: Handle String Labels (e.g., 'spam'/'ham' instead of 1/0)
        if df['label'].dtype == object:
            log("[*] Converting string labels to numeric (0/1)...")
            df['label'] = df['label'].astype(str).str.lower().str.strip()
            # Map common string variations to 1 (Phishing/Spam) and 0 (Safe/Ham)
            label_mapping = {
                'spam': 1, 'phishing': 1, 'bad': 1, 'malicious': 1, '1': 1,
                'ham': 0, 'safe': 0, 'good': 0, 'legitimate': 0, '0': 0
            }
            df['label'] = df['label'].map(label_mapping)
            
            # Drop any rows where the mapping failed (e.g., weird unmapped values)
            df = df.dropna(subset=['label'])

        log("[*] Sanitizing training data (This ensures it matches the live scanner)...")
        df['body'] = df['body'].apply(clean_text)

        X_raw = df['body']
        y_raw = df['label'].astype(int)

        log("[*] Splitting data into 80% Training and 20% Testing sets...")
        X_train, X_test, y_train, y_test = train_test_split(X_raw, y_raw, test_size=0.2, random_state=42)

        log("[*] Initializing TF-IDF Vectorizer (Vocabulary Limit: 5000 words)...")
        vectorizer = TfidfVectorizer(max_features=5000)
        
        log("[*] Mathematical vectorization in progress...")
        X_train_vectorized = vectorizer.fit_transform(X_train)
        X_test_vectorized = vectorizer.transform(X_test)

        log("[*] Booting Random Forest Classifier (100 Decision Trees)...")
        log("[!] TRAINING IN PROGRESS. Please do not close the application...")
        classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        classifier.fit(X_train_vectorized, y_train)

        log("[*] Training complete! Running accuracy evaluation on test set...")
        predictions = classifier.predict(X_test_vectorized)
        accuracy = accuracy_score(y_test, predictions)
        acc_str = f"{accuracy * 100:.2f}%"
        
        log("[*] Serializing and saving AI brain to models/ folder...")
        os.makedirs('models', exist_ok=True)
        joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')
        joblib.dump(classifier, 'models/phishing_rf_model.pkl')

        # Record history
        try:
            history_file = 'training_history.csv'
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dataset_name = os.path.basename(dataset_path)
            file_exists = os.path.isfile(history_file)
            with open(history_file, mode='a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Timestamp', 'Dataset_Name', 'Accuracy', 'Status'])
                writer.writerow([timestamp, dataset_name, acc_str, 'Success'])
        except Exception as e:
            log(f"Warning: Could not write to history file. {e}")

        return True, f"All models saved and ready! Final Accuracy: {acc_str}"

    except Exception as e:
        return False, f"CRITICAL ERROR:\n{str(e)}"