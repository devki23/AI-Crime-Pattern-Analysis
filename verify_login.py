import sqlite3
import os

DB_PATH = 'crime_data.db'

def test_login(identifier, password):
    print(f"Testing login for: '{identifier}' with password: '{password}'")
    
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM users WHERE (email = ? OR username = ?) AND password = ?"
        print(f"Executing Query: {query}")
        
        cursor.execute(query, (identifier, identifier, password))
        user = cursor.fetchone()
        
        if user:
            print(f"SUCCESS! Found user: {user['full_name']} (Role: {user['role']}, ID: {user['user_id']})")
        else:
            print("FAILURE! No user found matching credentials.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with the credentials found in the previous step
    test_login('101', 'ayushishah')
    test_login('ayushishah0506@gmail.com', 'ayushishah')
