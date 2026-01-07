#!/usr/bin/env python3
"""Fix joined_date <= created_at <= updated_at temporal consistency"""
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('output/asana_simulation.sqlite')
cursor = conn.cursor()

print("Fixing temporal consistency: joined_date <= created_at <= updated_at...")

# Get all users and fix their created_at to be after joined_date
cursor.execute("SELECT user_id, joined_date, updated_at FROM users")
users = cursor.fetchall()

updates = 0
for user_id, joined_date_str, updated_at_str in users:
    # Parse dates
    joined_date = datetime.fromisoformat(joined_date_str.replace('Z', '+00:00').split('+')[0])
    updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00').split('+')[0])
    
    # created_at should be 0-3 days after joined_date
    days_after = (updated_at - joined_date).days // 100  # Use a portion of the tenure spread
    if days_after < 0:
        days_after = 0
    elif days_after > 3:
        days_after = 3
    
    # Create new created_at: joined_date + 0-3 days
    new_created_at = joined_date + timedelta(days=min(3, max(0, days_after)))
    
    # Verify temporal chain: joined_date <= created_at <= updated_at
    if new_created_at < joined_date:
        new_created_at = joined_date
    if updated_at < new_created_at:
        updated_at = new_created_at + timedelta(hours=1)
    
    cursor.execute(
        "UPDATE users SET created_at = ?, updated_at = ? WHERE user_id = ?",
        (new_created_at.isoformat(), updated_at.isoformat(), user_id)
    )
    updates += 1

conn.commit()
print(f"✓ Fixed temporal consistency for {updates} user records")

# Verify the fix
cursor.execute("""
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN datetime(created_at) < datetime(joined_date) THEN 1 ELSE 0 END) as bad_created,
    SUM(CASE WHEN datetime(updated_at) < datetime(created_at) THEN 1 ELSE 0 END) as bad_updated
FROM users
""")

total, bad_created, bad_updated = cursor.fetchone()
print(f"\nVerification: Total={total}, Bad created_at={bad_created}, Bad updated_at={bad_updated}")

if bad_created == 0 and bad_updated == 0:
    print("✅ Temporal consistency verified: joined_date <= created_at <= updated_at")
else:
    print("⚠️ Some records still violate temporal consistency")

conn.close()
