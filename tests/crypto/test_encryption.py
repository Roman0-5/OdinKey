
import os
from src.crypto.encryption import Encryption

class TestEncryption:
    def test_derive_key_returns_correct_length(self):
        """
        Testet, ob die Schlüsselableitung einen Key der richtigen Länge (32 Bytes für AES-256)
        zurückgibt und ob er vom Typ 'bytes' ist.
        """
        # Arrange (Vorbereitung)
        encryption = Encryption()
        password = "MeinMasterPasswort"
        # Ein Salt ist einfach ein zufälliger Bytewert, z.B. 16 Bytes
        salt = os.urandom(16)

        # Act (Ausführung)

        derived_key = encryption.derive_key(password, salt)

        # Assert (Überprüfung)
        # Ein AES-256 Schlüssel MUSS genau 32 Bytes lang sein.
        assert len(derived_key) == 32
        # Der Schlüssel muss binäre Daten (bytes) sein, kein Text (str).
        assert isinstance(derived_key, bytes)