import sqlite3
import os

# The app uses crime_data.db (as set in database.py)
DB_PATH = "crime_data.db"

if not os.path.exists(DB_PATH):
    print(f"Database file '{DB_PATH}' does not exist yet.")
    print("Run setup_admin.py or trigger /api/admin/db-reset to initialize it.")
else:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # List all tables and row counts
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("=== TABLES ===")
    if not tables:
        print("  (no tables found - database not initialized)")
    for t in tables:
        name = t[0]
        cursor.execute(f"SELECT COUNT(*) FROM {name}")
        count = cursor.fetchone()[0]
        print(f"  {name}: {count} rows")

    print()

    # Show last 5 crimes
    print("=== CRIMES (last 5) ===")
    try:
        cursor.execute("SELECT * FROM crimes ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        print("Columns:", cols)
        for r in rows:
            print(dict(r))
        if not rows:
            print("  No crime records found.")
    except Exception as e:
        print("Error:", e)

    print()

    # Show users
    print("=== USERS ===")
    try:
        cursor.execute("SELECT user_id, username, email, role FROM users")
        rows = cursor.fetchall()
        for r in rows:
            print(dict(r))
        if not rows:
            print("  No users found.")
    except Exception as e:
        print("Error:", e)

    conn.close()
