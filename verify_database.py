"""
Quick verification script to check generated data.
"""

import sqlite3
import os

db_path = "output/asana_simulation.sqlite"

if not os.path.exists(db_path):
    print(f"Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
tables = cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
).fetchall()

print("\n" + "="*60)
print("DATABASE VERIFICATION REPORT")
print("="*60)

for table in tables:
    table_name = table[0]
    count = cursor.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
    print(f"{table_name:<35} : {count:>8} records")

print("="*60)

# Sample data
print("\nSAMPLE DATA:")
print("="*60)

# Organization
org = cursor.execute("SELECT name, domain FROM organizations LIMIT 1;").fetchone()
print(f"\nOrganization: {org[0]} ({org[1]})")

# Teams
teams = cursor.execute(
    "SELECT name, team_type FROM teams LIMIT 3;"
).fetchall()
print(f"\nSample Teams:")
for team in teams:
    print(f"  - {team[0]} ({team[1]})")

# Users
users = cursor.execute(
    "SELECT name, email, department FROM users LIMIT 3;"
).fetchall()
print(f"\nSample Users:")
for user in users:
    print(f"  - {user[0]} ({user[1]}) - {user[2]}")

# Projects
projects = cursor.execute(
    "SELECT name, project_type FROM projects LIMIT 3;"
).fetchall()
print(f"\nSample Projects:")
for project in projects:
    print(f"  - {project[0]} ({project[1]})")

# Tasks
tasks = cursor.execute(
    "SELECT name, priority, status FROM tasks LIMIT 3;"
).fetchall()
print(f"\nSample Tasks:")
for task in tasks:
    print(f"  - {task[0]} [Priority: {task[1]}] [Status: {task[2]}]")

print("\n" + "="*60)
print("✓ Database verification complete")
print("="*60 + "\n")

conn.close()
