
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

    def test_encrypt_returns_bytes_and_nonce(self):
        """
        Testet, ob encrypt() Bytes zurückgibt und ob eine Nonce dabei ist.
        """
        # Arrange
        encryption = Encryption()
        password = "MasterPassword"
        salt = os.urandom(16)
        key = encryption.derive_key(password, salt)
        plaintext = "GeheimesPasswort123"

        # Act
        # WICHTIG: AES-GCM braucht eine "Nonce" (Number used once).
        nonce, ciphertext = encryption.encrypt_data(key, plaintext)

        # Assert
        assert isinstance(nonce, bytes)
        assert isinstance(ciphertext, bytes)
        assert len(nonce) == 12  # Bei AES-GCM ist die Nonce standardmäßig 12 Bytes lang
        assert len(ciphertext) > 0
        assert ciphertext != plaintext.encode()  # Der Text muss verschlüsselt sein

    def test_encrypt_decrypt_cycle(self):
        """
        Der wichtigste Test: Kann ich etwas verschlüsseln und wieder entschlüsseln?
        """
        # Arrange
        encryption = Encryption()
        password = "MasterPassword"
        salt = os.urandom(16)
        key = encryption.derive_key(password, salt)
        original_text = "MeinSuperGeheimesGooglePasswort"

        # Act
        # 1. Verschlüsseln
        nonce, ciphertext = encryption.encrypt_data(key, original_text)

        # 2. Entschlüsseln (wir brauchen den Key, die Nonce und den Ciphertext)
        decrypted_text = encryption.decrypt_data(key, nonce, ciphertext)

        # Assert
        assert decrypted_text == original_text