# tests/test_crypto_hashing.py
import pytest
from argon2 import PasswordHasher
from src.crypto.hashing import Hashing

class TestHashing:
    def test_hash_master_password_returns_valid_argon2_hash(self):
        """
        Testet, ob die hash_password Methode einen validen ARGON2-String zurückgibt.
        Ein ARGON2-Hash fängt typischerweise mit '$argon2' an.
        """
        # Arrange (Vorbereitung)
        password = "SicheresMasterPasswort123!"
        hashing_st = Hashing()

        # Act (Ausführung)
        hashed_password = hashing_st.hash_master_password(password)

        # Assert (Überprüfung)
        assert hashed_password is not None
        assert isinstance(hashed_password, str)
        assert hashed_password.startswith("$argon2"), "Der Hash sollte mit '$argon2' beginnen"

    def test_verify_master_password_correct(self):
        """
        Testet, ob ein korrektes Passwort erfolgreich gegen seinen Hash verifiziert wird.
        """
        # Arrange
        password = "MeinGeheimesPasswort"
        hashing_st = Hashing()
        # Wir erstellen uns einen "echten" Hash zum Testen
        ph = PasswordHasher()
        valid_hash = ph.hash(password)

        # Act
        is_valid = hashing_st.verify_master_password(valid_hash, password)

        # Assert
        assert is_valid is True, "Das korrekte Passwort sollte verifiziert werden"

    def test_verify_password_incorrect(self):
        """
        Testet, ob ein falsches Passwort abgelehnt wird.
        """
        # Arrange
        password = "RichtigesPasswort"
        wrong_password = "FalschesPasswort"
        hashing_st = Hashing()
        ph = PasswordHasher()
        valid_hash = ph.hash(password)

        # Act
        is_valid = hashing_st.verify_master_password(valid_hash, wrong_password)

        # Assert
        assert is_valid is False, "Das falsche Passwort sollte NICHT verifiziert werden"