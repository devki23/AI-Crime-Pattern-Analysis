import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'crime_db'),
        auth_plugin='mysql_native_password'
    )
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("SHOW COLUMNS FROM users LIKE 'aadhar_number'")
    exists = cursor.fetchone()
    
    if exists:
        print("Column 'aadhar_number' already exists.")
    else:
        cursor.execute("ALTER TABLE users ADD COLUMN aadhar_number VARCHAR(12)")
        conn.commit()
        print("Column 'aadhar_number' added successfully.")
    
    cursor.execute("DESCRIBE users")
    rows = cursor.fetchall()
    print("\nCurrent users table columns:")
    for row in rows:
        print("  " + str(row[0]) + " - " + str(row[1]))
    
    conn.close()
except Exception as e:
    print("Error: " + str(e))
