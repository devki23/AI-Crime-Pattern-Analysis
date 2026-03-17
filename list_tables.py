import sqlite3
import os

db_path = 'crime_data.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables:", tables)
        
        # List users if table exists
        if ('users',) in tables:
            print("\nUsers:")
            cursor.execute("SELECT * FROM users")
            columns = [description[0] for description in cursor.description]
            print(f"Columns: {columns}")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        else:
            print("\nTable 'users' NOT found.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
