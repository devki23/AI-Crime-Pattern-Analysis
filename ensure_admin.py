import sqlite3
import os

DB_PATH = 'crime_data.db'

def ensure_admin_test():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin_test'")
        user = cursor.fetchone()
        
        if user:
            print("User 'admin_test' ALREADY EXISTS.")
            # Update password just in case
            cursor.execute("UPDATE users SET password = 'admin123' WHERE username = 'admin_test'")
            conn.commit()
            print("Password reset to 'admin123'.")
        else:
            print("Creating 'admin_test'...")
            cursor.execute("""
                INSERT INTO users (username, full_name, email, password, role, station, badge_number)
                VALUES ('admin_test', 'Test Admin', 'admin@test.com', 'admin123', 'admin', 'HQ', 'TEST-001')
            """)
            conn.commit()
            print("User 'admin_test' CREATED successfully.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ensure_admin_test()
