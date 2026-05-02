import os
# 🚀 THE FIX: Import BOTH the generator and the checker!
from werkzeug.security import generate_password_hash, check_password_hash

CRED_FILE = 'credentials.txt'

def init_db():
    if not os.path.exists(CRED_FILE):
        with open(CRED_FILE, 'w') as f:
            default_hash = generate_password_hash("admin123")
            f.write(f"admin,{default_hash},admin\n")

def load_users():
    """Reads the credentials file and returns a dictionary."""
    init_db()
    users = {}
    with open(CRED_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(',')
                if len(parts) == 3:
                    u, p, r = parts
                    users[u] = {'password': p, 'role': r}
    return users

def authenticate(username, password):
    """Checks if the username and password match."""
    username = username.lower().strip()
    users = load_users()
    
    # Check if user exists AND the password matches the hash
    if username in users and check_password_hash(users[username]['password'], password):
        return True, users[username]['role']
    return False, None