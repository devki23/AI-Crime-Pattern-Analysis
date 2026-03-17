import sqlite3

try:
    conn = sqlite3.connect('crime_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, role, password FROM users')
    users = cursor.fetchall()
    print("Users found:")
    for user in users:
        print(user)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
