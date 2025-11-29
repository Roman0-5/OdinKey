import sqlite3
import os

#importieren der Funktion aus dem models-Modul
from src.database.models import create_schema

class DatabaseConnection:
    def __init__(self, db_file: str = "data/odinkey.db"):
        self.db_file = db_file

    #stellt Verbindung zu SQ-Lite Datenbank her
    def connect(self) -> sqlite3.Connection:
        # falls Ordner nicht existiert wird er angelegt
        directory = os.path.dirname(self.db_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        return sqlite3.connect(self.db_file)

    def create_tables(self):
        #erstellt Tabellen mithilfe von models.py
        conn = self.connect()
        cursor = conn.cursor()

        #Aufruf der Funktion aus models.py
        create_schema(cursor)

        conn.commit()
        conn.close()

if __name__ == "__main__":
    print("Versuche Datenbank zu erstellen...")

    # 1. Instanz erstellen
    db = DatabaseConnection()

    # 2. Methode aufrufen
    db.create_tables()

    print(f"Datenbank liegt unter: {db.db_file}")
