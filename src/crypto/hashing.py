from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class Hashing:

    # Konstruktor für Hasher "ph"
    def __init__(self):
        self.ph = PasswordHasher()


    # mit "ph" Master-PW hashen
    def hash_master_password(self, password: str) -> str:
        hashed_password = self.ph.hash(password)
        return hashed_password

    def verify_master_password(self, stored_hash: str, password_to_check: str) -> bool:
        try:
            # wir nützen .verify von argon2 import, da man aufgrund des Salt nicht mit logical operators arbeiten kann --> hash würde nie übereinstimmen
            self.ph.verify(stored_hash, password_to_check)
            return True #wenn verify passt gib True zurück
        # VerifyMismatchError ist auch von agron2 --> gibt False aus wenn Passwort falsch
        except VerifyMismatchError:
            return False



