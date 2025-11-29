import secrets
import string

class PasswordGeneratorService:

    def generate_password(self,
                          length: int = 12,
                          use_symbols: bool = True,
                          use_lower_case: bool = True,
                          use_upper_case: bool = True,
                          use_digits: bool = True) -> str:

        # pool mit allen zulässigen Zeichen erstellen
        pool = ""
        length = int(length)
        if use_symbols:
            pool += string.punctuation
        if use_lower_case:
            pool += string.ascii_lowercase
        if use_upper_case:
            pool += string.ascii_uppercase
        if use_digits:
            pool += string.digits

        # Fehler werfen, wenn nichts ausgewählt wurde
        if pool == "":
            raise ValueError ("Bitte mindestens einen Parameter wählen")

        password = ""
        for i in range(length):
            password += str(secrets.choice(pool))

        return password










