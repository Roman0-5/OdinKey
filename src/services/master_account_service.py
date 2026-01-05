import os
from typing import Optional, Tuple
from src.core.master_account import MasterAccount
from src.database.repository import MasterAccountRepository
from src.crypto.hashing import Hashing
from src.crypto.encryption import Encryption


class MasterAccountService:
    def __init__(self, repo: MasterAccountRepository):
        self.repo = repo
        self.hashing = Hashing()
        self.encryption = Encryption()

    def register_account(self, username: str, password: str) -> MasterAccount:
        """
        Erstellt einen neuen Master-Account.
        Wirft einen Fehler, wenn schon einer existiert (Single-User Prinzip).
        """
        # Prüfen, ob schon ein Account existiert
        if self.repo.account_exists():
            raise ValueError("Es existiert bereits ein Master-Account. Bitte einloggen.")


        # Validierung
        valid, msg = MasterAccount.validate_password(password)
        if not valid:
            raise ValueError(msg)

        # Salt generieren (Zufallswert für Hashing & Key-Derivation)
        salt = os.urandom(16)

        # Passwort hashen (für die Datenbank)
        password_hash = self.hashing.hash_master_password(password)

        # Speichern
        # WICHTIG: Im Objekt speichern wir den Hash, nicht das Klartext-Passwort
        new_account = MasterAccount(username=username, password=password_hash)
        self.repo.create_account(new_account, salt)

        return new_account

    def login(self, username: str, password: str) -> Optional[Tuple[MasterAccount, bytes]]:
        """
        Versucht Login
        Bei Erfolg: Gibt (Account, MasterKey) zurück.
        Bei Fehler: Gibt None zurück.
        """
        # Daten aus DB holen
        account, salt = self.repo.get_account_by_username(username)

        if not account or not salt:
            return None  # Benutzer nicht gefunden

        # Passwort prüfen (Hash vergleich)
        # account.password ist hier der Hash aus der DB
        is_valid = self.hashing.verify_master_password(account.password, password)
        if not is_valid:
            return None  # Falsches Passwort

        # Wenn alles stimmt: Master-Key ableiten
        # Diesen Key brauchen wir für die Session, um Profile zu entschlüsseln
        master_key = self.encryption.derive_key(password, salt)

        return account, master_key