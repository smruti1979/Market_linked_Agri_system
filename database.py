import sqlite3
import os

DB_FILE = "agri_platform.db"

def get_connection():
    """Establishes a resilient connection with a 30-second timeout to handle high load."""
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    # Enable Write-Ahead Logging (WAL) for concurrent read/write support
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmer_ledgers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            acres REAL NOT NULL,
            recommended_crop TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_farm_record(farmer_id: str, lat: float, lon: float, acres: float, crop: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO farmer_ledgers (farmer_id, latitude, longitude, acres, recommended_crop)
            VALUES (?, ?, ?, ?, ?)
        """, (farmer_id, lat, lon, acres, crop))
        conn.commit()
    except Exception as e:
        print(f"[DB Error Writing Record]: {e}")
    finally:
        conn.close()

def fetch_all_farm_records():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT farmer_id, latitude, longitude, acres, recommended_crop FROM farmer_ledgers")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def purge_all_database_records():
    """Safely clears all rows from the ledger table and resets auto-incrementing IDs."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM farmer_ledgers;")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='farmer_ledgers';")
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB Error Purging Table]: {e}")
        return False
    finally:
        conn.close()
