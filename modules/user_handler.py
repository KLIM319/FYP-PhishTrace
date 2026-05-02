from modules.login_handler import load_users, CRED_FILE
from werkzeug.security import generate_password_hash

def save_users(users):
    """Writes the dictionary back to the credentials file."""
    with open(CRED_FILE, 'w') as f:
        for u, data in users.items():
            f.write(f"{u},{data['password']},{data['role']}\n")

def format_username(username):
    """Enforces the lowercase and no-space rule."""
    username = username.lower()
    if " " in username:
        return False, "Username cannot contain spaces."
    if not username:
        return False, "Username cannot be empty."
    return True, username

def add_user(username, password, role="user"):
    """Admin function to add a new user."""
    valid, result = format_username(username)
    if not valid: return False, result
    username = result
    
    users = load_users()
    if username in users:
        return False, f"User '{username}' already exists."
    
    # 🚀 THE FIX: Generate the hash before saving it to the dictionary!
    hashed_password = generate_password_hash(password)
    users[username] = {'password': hashed_password, 'role': role}
    
    save_users(users)
    return True, f"User '{username}' added successfully."

def delete_user(username):
    """Admin function to delete a user."""
    username = username.lower().strip()
    users = load_users()
    
    if username == 'admin':
        return False, "Cannot delete the default system admin."
        
    if username in users:
        del users[username]
        save_users(users)
        return True, f"User '{username}' deleted."
    return False, "User not found."

def update_password(username, new_password):
    """Allows any user to change their own password."""
    username = username.lower().strip()
    users = load_users()
    
    if username in users:
        # 🚀 THE FIX: Generate the hash before updating the dictionary!
        hashed_password = generate_password_hash(new_password)
        users[username]['password'] = hashed_password
        
        save_users(users)
        return True, "Password updated successfully."
    return False, "User not found."