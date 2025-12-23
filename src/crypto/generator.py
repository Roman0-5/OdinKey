import secrets
import string
"""
secrets ist die Kryptographie Library
string ist die Zeichenset Library (ASCII, Ziffern, Zeichen)
"""

class PasswordGenerator:
    # Konstanten
    MIN_LENGTH = 8
    MAX_LENGTH = 64

    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase
    DIGITS = string.digits
    SPECIAL = string.punctuation

    @staticmethod
    def validate_length(length: int) -> bool:
        # Länge muss innerhalb von Konstanten sein
        if length < PasswordGenerator.MIN_LENGTH or length > PasswordGenerator.MAX_LENGTH:
            return False
        else:
            return True

    @staticmethod
    def validate_options(use_uppercase, use_lowercase, use_digits, use_special):
        # es muss mindestens eine Option aktiv sein
        if use_uppercase or use_lowercase or use_digits or use_special:
            return True
        else:
            return False

    @staticmethod
    def generate(length=12, use_uppercase=True, use_lowercase=True,
                 use_digits=True, use_special=True):
        # Ganze Logik um es zu generieren

        # Länge validieren
        if not PasswordGenerator.validate_length(length):
            raise ValueError(f"Password must be between {PasswordGenerator.MIN_LENGTH} and {PasswordGenerator.MAX_LENGTH}"
            )
        # Optionen validieren
        if not PasswordGenerator.validate_options(use_uppercase, use_lowercase,
                                                  use_digits, use_special):
            raise ValueError("Choose at least one type")

        # Leeres Zeichen Pool initialisieren
        characters = ""

        if use_uppercase:
            characters += PasswordGenerator.UPPERCASE

        if use_lowercase:
            characters += PasswordGenerator.LOWERCASE

        if use_digits:
            characters += PasswordGenerator.DIGITS

        if use_special:
            characters += PasswordGenerator.SPECIAL

        # Je nachdem welche Option gewählt ist Passwort generieren
        password = ''.join(secrets.choice(characters) for _ in range(length))

        return password