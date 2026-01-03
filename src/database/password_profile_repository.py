import sqlite3
from typing import Optional
from src.core.password_profile import PasswordProfile
from src.crypto.encryption import Encryption
from src.database.connection import DatabaseConnection


class PasswordProfileRepository:
    def delete_profile(self, profile_id: int) -> None:
        """
        Löscht ein Passwort-Profil anhand der ID.
        """
        query = "DELETE FROM password_profiles WHERE id = ?"
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (profile_id,))
            conn.commit()
    def update_profile(self, profile: PasswordProfile) -> None:
        """
        Updates an existing password profile (fields and encrypted password).
        """
        nonce, encrypted_password = self.crypto.encrypt_data(self.master_key, profile.password)
        salt = b""
        query = """
            UPDATE password_profiles
            SET service_name = ?, url = ?, username = ?, password_blob = ?, nonce = ?, salt = ?, notes = ?, created_at = ?
            WHERE id = ?
        """
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                profile.service_name,
                profile.url,
                profile.username,
                encrypted_password,
                nonce,
                salt,
                profile.notes,
                profile.created_at,
                profile.id
            ))
            conn.commit()

    def __init__(self, db_connection: DatabaseConnection, master_key: bytes):
        """
        Initialisiert das Repository.
        """
        self.db = db_connection # Verbindung zur DB
        self.master_key = master_key #32-Byte Key abgeleitet vom Master-Passwort - dient zur ver- und entschlüsselung
        self.crypto = Encryption() #Instanz der Encryption Klasse

    def create_profile(self, profile: PasswordProfile) -> int:
        """
        Verschlüsselt das Passwort und speichert das Profil.
        """

        nonce, encrypted_password = self.crypto.encrypt_data(self.master_key, profile.password)

        # Salt ist hier optional/leer, da wir den Master-Key direkt nutzen
        salt = b""

        query = """
            INSERT INTO password_profiles 
            (user_id, service_name, url, username, password_blob, nonce, salt, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                profile.user_id,
                profile.service_name,
                profile.url,
                profile.username,
                encrypted_password,  # Der Ciphertext
                nonce,  # Die Nonce
                salt,
                profile.notes,
                profile.created_at
            ))
            conn.commit()
            return cursor.lastrowid

    def get_profile_by_id(self, profile_id: int) -> Optional[PasswordProfile]:
        """
        Lädt ein Profil und entschlüsselt das Passwort wieder.
        """
        query = "SELECT * FROM password_profiles WHERE id = ?"

        with self.db.connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (profile_id,))
            row = cursor.fetchone()

            if not row:
                return None

            # Entschlüsseln
            decrypted_password = self.crypto.decrypt_data(
                key=self.master_key,
                nonce=row["nonce"],
                ciphertext=row["password_blob"]
            )

            return PasswordProfile(
                id=row["id"],
                user_id=row["user_id"],
                service_name=row["service_name"],
                url=row["url"],
                username=row["username"],
                password=decrypted_password,  # Ist jetzt wieder ein String!
                notes=row["notes"],
                created_at=row["created_at"]
            )