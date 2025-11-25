from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

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

