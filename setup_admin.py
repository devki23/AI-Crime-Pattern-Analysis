import sqlite3
import os

from dotenv import load_dotenv
load_dotenv()
DB_PATH = os.getenv('SQLITE_DB_PATH', 'crime_data.db')

def create_admin():
    print(f"Connecting to database at: {DB_PATH}")
    
    # Check if DB needs initialization
    if not os.path.exists(DB_PATH):
        print("Database not found. Initializing...")
        from backend.app.services.database import init_db
        init_db()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check for tables
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
             print("Users table not found. Initializing schema...")
             from backend.app.services.database import init_db
             init_db()
             # Reconnect
             conn.close()
             conn = sqlite3.connect(DB_PATH)
             conn.row_factory = sqlite3.Row
             cursor = conn.cursor()
    except Exception as e:
        print(f"Error checking DB: {e}")

    print("\n--- Create / Update Admin User ---")

    print("\n--- Create / Update Admin User ---")
    username = input("Enter Admin Username (default: admin): ").strip() or "admin"
    email = input("Enter Admin Email (default: admin@police.gov): ").strip() or "admin@police.gov"
    password = input("Enter Admin Password: ").strip()
    
    if not password:
        print("Password cannot be empty.")
        return

    full_name = "Super Administrator"
    badge_number = "ADM-001"
    station = "Headquarters"

    try:
        # Check if user exists (by username or email)
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        user = cursor.fetchone()

        if user:
            print(f"User '{username}' or '{email}' already exists. Updating password and role to ADMIN...")
            cursor.execute("""
                UPDATE users 
                SET password = ?, role = 'admin', full_name = ?, badge_number = ?, station = ?
                WHERE username = ? OR email = ?
            """, (password, full_name, badge_number, station, username, email))
        else:
            print(f"Creating new admin user '{username}'...")
            cursor.execute("""
                INSERT INTO users (username, full_name, email, password, role, station, badge_number)
                VALUES (?, ?, ?, ?, 'admin', ?, ?)
            """, (username, full_name, email, password, station, badge_number))
        
        conn.commit()
        print(f"\nSUCCESS: Admin user '{username}' set up successfully.")
        print(f"You can now login with Username: '{username}' and your password.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin()
