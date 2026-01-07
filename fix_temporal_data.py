#!/usr/bin/env python3
"""Fix temporal data in existing database by adjusting updated_at values"""
import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('output/asana_simulation.sqlite')
cursor = conn.cursor()

print("Fixing temporal data in existing database...")

# Fix users: add realistic hours_since_creation to updated_at
print("Processing users...")
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]

cursor.execute("SELECT user_id, created_at FROM users LIMIT 100")
sample_users = cursor.fetchall()

# Quick batch update for all users at once
cursor.execute("""
UPDATE users SET updated_at = 
  datetime(created_at, '+' || CAST(CAST(ABS(RANDOM() % 720) AS INTEGER) AS TEXT) || ' hours')
""")

conn.commit()
print(f"✓ Updated {user_count} user records")

# Fix projects
print("Processing projects...")
cursor.execute("SELECT COUNT(*) FROM projects")
project_count = cursor.fetchone()[0]

cursor.execute("""
UPDATE projects SET updated_at = 
  datetime(created_at, '+' || CAST(CAST(ABS(RANDOM() % 48) AS INTEGER) AS TEXT) || ' hours')
""")

conn.commit()
print(f"✓ Updated {project_count} project records")

conn.close()
print("\n✅ Temporal data fixed successfully!")
