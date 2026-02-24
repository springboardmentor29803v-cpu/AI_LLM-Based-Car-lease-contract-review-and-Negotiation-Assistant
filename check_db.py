import sqlite3

# Connect to the database
conn = sqlite3.connect("contracts.db")
cursor = conn.cursor()

# Ask for all data
cursor.execute("SELECT id, filename, extracted_text FROM contracts")
rows = cursor.fetchall()

print(f"Total Contracts Found: {len(rows)}\n")

for row in rows:
    print(f"--- Contract ID: {row[0]} ---")
    print(f"Filename: {row[1]}")
    # Print just the first 200 characters to prove it's there
    print(f"Saved Text Start: {row[2][:200]}...\n")

conn.close()