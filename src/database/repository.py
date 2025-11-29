from src.database.connection import DatabaseConnection
from src.core.master_account import MasterAccount


class MasterAccountRepository:
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    def create_account(self, master_account: MasterAccount, salt: bytes):
        #Speichert einen neuen Master Account inklusive Salt in der DB
        conn = self.db_connection.connect()
        cursor = conn.cursor()

        # Einfügen von Username, den Hash (der im password-Feld liegt) und das Salt
        cursor.execute("""
            INSERT INTO master_account (username, password_hash, salt)
            VALUES (?, ?, ?)
        """, (master_account.username, master_account.password, salt))

        conn.commit()
        conn.close()

    def account_exists(self) -> bool:
        #Prüft, ob bereits ein Master Account existiert (egal welcher).
        conn = self.db_connection.connect()
        cursor = conn.cursor()

        # SELECT 1 ist eine sehr schnelle Abfrage, um nur Existenz zu prüfen
        cursor.execute("SELECT 1 FROM master_account LIMIT 1")
        result = cursor.fetchone()

        conn.close()
        return result is not None

    def get_account_by_username(self, username: str) -> tuple[MasterAccount, bytes]:

        #Lädt den Account und das Salt anhand des Benutzernamens.
        #Gibt (MasterAccount, salt) zurück oder (None, None), falls nicht gefunden.

        conn = self.db_connection.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, password_hash, salt
            FROM master_account
            WHERE username = ?
        """, (username,))

        row = cursor.fetchone()
        conn.close()

        if row:
            # row[0]=id, row[1]=username, row[2]=password_hash, row[3]=salt

            # Wir bauen das Objekt wieder zusammen.
            # WICHTIG: Das Feld 'password' im Objekt enthält den Hash aus der DB!
            account = MasterAccount(
                id=row[0],
                username=row[1],
                password=row[2]
            )
            salt = row[3]
            return account, salt

        return None, None