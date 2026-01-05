import sqlite3
import os

class DatabaseConnection:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(os.path.dirname(base_dir))
        self.db_path = os.path.join(self.project_root, "odinkey.db")

    def connect(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_account (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service_name TEXT NOT NULL,
                url TEXT,
                username TEXT,
                password_blob BLOB NOT NULL,
                nonce BLOB NOT NULL,
                salt BLOB,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES master_account(id)
            )
            """)
            conn.commit()


if __name__ == "__main__":
    print("Versuche Datenbank zu erstellen...")
    db = DatabaseConnection()
    db.create_tables()
    print(f"Datenbank liegt unter: {db.db_path}") # Hier stand vorher .db_file (Fehler)