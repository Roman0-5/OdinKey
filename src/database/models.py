import sqlite3


def create_schema(cursor: sqlite3.Cursor):
    """
    Erstellt die notwendigen Tabellen für OdinKey.
    """

    # 1. Tabelle: Master Account
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_account (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL,
                   password_hash TEXT NOT NULL,
                   salt BLOB NOT NULL,
                   created_at TEXT
        );
    """)

    # 2. Tabelle: Passwort Profile
    # Wir speichern Metadaten (Service, URL, User) im Klartext für die Suche/Anzeige.
    # NUR das Passwort wird verschlüsselt (password_blob).
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_profiles (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id INTEGER NOT NULL,
                   service_name TEXT NOT NULL,
                   url TEXT NOT NULL,
                   username TEXT NOT NULL,
                   password_blob BLOB NOT NULL,
                   nonce BLOB NOT NULL,
                   salt BLOB,
                   notes TEXT,
                   created_at TEXT,
                   FOREIGN KEY (user_id) REFERENCES master_account (id)
        );
    """)