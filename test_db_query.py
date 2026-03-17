import sqlite3

conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

identifier = '103'
password = 'Police103'

cursor.execute("SELECT * FROM users WHERE (email = ? OR username = ?) AND password = ?", (identifier, identifier, password))
user = cursor.fetchone()

if user:
    print(dict(user))
else:
    print("User not found or password incorrect")
