import sqlite3
import os

DB_PATH = "/home/workspace/N5/cognition/brain.db"
SCHEMA_PATH = "/home/workspace/N5/cognition/schema.sql"

def init_db():
    print(f"Initializing database at {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
    
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
