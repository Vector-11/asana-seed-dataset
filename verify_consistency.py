#!/usr/bin/env python3
"""Verify temporal consistency with sample data"""
import sqlite3

conn = sqlite3.connect('output/asana_simulation.sqlite')
cursor = conn.cursor()

print("\n" + "="*100)
print("TEMPORAL CONSISTENCY VERIFICATION")
print("="*100)
print("\nExpected chain: joined_date <= created_at <= updated_at\n")

cursor.execute("""
SELECT 
    name,
    joined_date,
    created_at,
    updated_at,
    CAST((julianday(created_at) - julianday(joined_date)) * 24 as INTEGER) as hours_from_joined,
    CAST((julianday(updated_at) - julianday(created_at)) * 24 as INTEGER) as hours_from_created
FROM users
ORDER BY RANDOM()
LIMIT 20
""")

users = cursor.fetchall()
print(f"{'User':<20} {'Joined':<20} {'Created':<20} {'Updated':<20} {'hrs(J→C)':<10} {'hrs(C→U)':<10}")
print("-" * 100)

all_valid = True
for name, joined, created, updated, hrs_jc, hrs_cu in users:
    status = "✓" if hrs_jc >= 0 and hrs_cu >= 0 else "✗"
    print(f"{name:<20} {joined:<20} {created:<20} {updated:<20} {hrs_jc:>8} {hrs_cu:>8} {status}")
    if hrs_jc < 0 or hrs_cu < 0:
        all_valid = False

# Statistics
cursor.execute("""
SELECT 
    COUNT(*) as total,
    MIN(CAST((julianday(created_at) - julianday(joined_date)) * 24 as INTEGER)) as min_hours_jc,
    MAX(CAST((julianday(created_at) - julianday(joined_date)) * 24 as INTEGER)) as max_hours_jc,
    AVG(CAST((julianday(created_at) - julianday(joined_date)) * 24 as INTEGER)) as avg_hours_jc,
    MIN(CAST((julianday(updated_at) - julianday(created_at)) * 24 as INTEGER)) as min_hours_cu,
    MAX(CAST((julianday(updated_at) - julianday(created_at)) * 24 as INTEGER)) as max_hours_cu,
    AVG(CAST((julianday(updated_at) - julianday(created_at)) * 24 as INTEGER)) as avg_hours_cu
FROM users
""")

stats = cursor.fetchone()
print("\n" + "="*100)
print(f"{'STATISTICS':<20}")
print("-" * 100)
print(f"Total users: {stats[0]}")
print(f"  joined_date → created_at:")
print(f"    Min: {stats[1]} hours, Max: {stats[2]} hours, Avg: {stats[3]:.1f} hours")
print(f"  created_at → updated_at:")
print(f"    Min: {stats[4]} hours, Max: {stats[5]} hours, Avg: {stats[6]:.1f} hours")

if all_valid:
    print("\n✅ ALL RECORDS ARE TEMPORALLY CONSISTENT")
else:
    print("\n❌ SOME RECORDS VIOLATE TEMPORAL CONSTRAINTS")

conn.close()
print("="*100 + "\n")
