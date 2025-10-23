#!/usr/bin/env python3
"""
Create temporary admin user for testing (username: admin, password: admin).
Run this script from the project's NetGuardian folder or from the repo root.
It inserts a user into the SQLite fallback database netguardian.db if the user doesn't exist.
Remove the user after testing.
"""

import os
import sqlite3
import sys

# Try to use bcrypt if available, otherwise fallback to SHA256
try:
    import bcrypt
    def hash_password(pw: str) -> str:
        return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
except Exception:
    import hashlib
    def hash_password(pw: str) -> str:
        return hashlib.sha256(pw.encode('utf-8')).hexdigest()

# Determine DB path (repo root/netguardian.db)
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
db_path = os.path.abspath(os.path.join(repo_root, '..', 'netguardian.db'))
if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
    sys.exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Ensure users table exists (safe to run even if already present)
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
""")
conn.commit()

# Check if admin user exists
cur.execute("SELECT * FROM users WHERE username = ?", ('admin',))
if cur.fetchone():
    print("User 'admin' already exists in the database.")
    conn.close()
    sys.exit(0)

# Insert test admin user
pw_hash = hash_password('admin123')
try:
    cur.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        ('admin', 'admin@example.local', pw_hash)
    )
    conn.commit()
    print("Created test user 'admin' with password 'admin'. Please delete this user after testing.")
except Exception as e:
    print("Failed to create user:", e)
finally:
    conn.close()

