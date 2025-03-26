import os
import json
import sqlite3

# Define the path to the cache directory
CACHE_DIR = 'cache'

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('cache_data.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS cache_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE,
    strategy TEXT,
    data TEXT
)
''')

# Iterate over each file in the cache directory
for filename in os.listdir(CACHE_DIR):
    file_path = os.path.join(CACHE_DIR, filename)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = json.load(file)
            strategy = content.pop('_key', None)
            data = json.dumps(content)
            cursor.execute('''
            INSERT OR IGNORE INTO cache_data (key, strategy, data)
            VALUES (?, ?, ?)
            ''', (filename, strategy, data))

# Commit changes and close the connection
conn.commit()
conn.close()
