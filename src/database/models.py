
def create_schema(cursor):
    # Tabelle für Master Account (salt wird getrennt von Hash gespeichert)
    # BLOB speichert einfach Folge von Bytes ohne Interpration wie Text oder VARCHAR
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_account (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL,
                   password_hash TEXT NOT NULL,
                   salt BLOB NOT NULL
        );
    """)

    # Tabelle für verschlüsselte Profile
    # 'encrypted_data' enthält alles (USER, PW, URL)
    # 'nonce' brauchen wir zwingend zum Entschlüsseln mit AES-GCM
    # BLOB speichert einfach Folge von Bytes ohne Interpration wie Text oder VARCHAR
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_profiles (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id INTEGER NOT NULL,
                   encrypted_data BLOB NOT NULL,
                   nonce BLOB NOT NULL,
                   FOREIGN KEY (user_id) REFERENCES master_account (id)
        );
    """)