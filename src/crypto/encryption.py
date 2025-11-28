import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class Encryption:

    def derive_key(self, password:str, salt: bytes) -> bytes:
        # Erstellt ein KDF (Key Derivation Function) Objekt, PBKDF2HMAC ist Funktion von cryptography
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), #SHA256 als Algorithmus
            length=32,  #AES-Schlüssel muss 32 Bytes groß sein
            salt=salt, #bekommt salt übergeben
            iterations=100000,
            backend=default_backend()
        )

        #Schlüsselableitung
        #Das Passwort muss erst in bytes umgewandelt werden: password.encode()
        key = kdf.derive(password.encode())

        return key #mit diesem Key (wird aus Master-PW abgeleitet) wird DB mit AES-256 ver- und entschlüsselt

    def encrypt_data(self, key: bytes, plaintext: str) -> tuple[bytes, bytes]:

        # Instanz erstellen
        aesgcm = AESGCM(key)

        # zufällige Nonce (Number used once) erstellen mit 12 Bytes
        nonce = os.urandom(12)

        # Verschlüsseln - Daten kommen als Bytes daher plaintext.encode()
        # 3. Parameter (associated_data) kann hier none sein
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)

        # Nonce und Ciphertext zurückgeben
        return nonce, ciphertext

    def decrypt_data(self, key: bytes, nonce: bytes, ciphertext: bytes) -> str:

        # Instanz erstellen
        aesgcm = AESGCM(key)

        # Entschlüsseln
        # Wenn der Key falsch ist oder die Daten manipuliert wurden, wirft dies einen Fehler (InvalidTag)
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)

        # In String umwandeln
        return plaintext_bytes.decode()





