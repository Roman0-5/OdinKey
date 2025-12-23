import secrets
import string
"""
secrets ist die Kryptographie Library
string ist die Zeichenset Library (ASCII, Ziffern, Zeichen)
"""

class PasswordGenerator:
    MIN_LENGTH = 8
    MAX_LENGTH = 128

    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase
    DIGITS = string.digits
    SPECIAL = string.punctuation

    @staticmethod
    def validate_length(length: int) -> bool:
        if length < PasswordGenerator.MIN_LENGTH or length > PasswordGenerator.MAX_LENGTH:
            return False
        else:
            return True

    @staticmethod
    def validate_options(use_uppercase, use_lowercase, use_digits, use_special):

        if use_uppercase or use_lowercase or use_digits or use_special:
            return True
        else:
            return False

    @staticmethod
    def generate(length=16, use_uppercase=True, use_lowercase=True,
                 use_digits=True, use_special=True):

        # 1. Validiere length
        if not PasswordGenerator.validate_length(length):
            raise ValueError(f"Password must be between {PasswordGenerator.MIN_LENGTH} and {PasswordGenerator.MAX_LENGTH}"
            )

        # 2. Validiere options
        if not PasswordGenerator.validate_options(use_uppercase, use_lowercase,
                                                  use_digits, use_special):
            raise ValueError("Choose at least one type")

        # 3. Baue Zeichen-Pool
        characters = ""

        if use_uppercase:
            characters += PasswordGenerator.UPPERCASE

        if use_lowercase:
            characters += PasswordGenerator.LOWERCASE

        if use_digits:
            characters += PasswordGenerator.DIGITS

        if use_special:
            characters += PasswordGenerator.SPECIAL

        # 4. Generiere Passwort
        password = ''.join(secrets.choice(characters) for _ in range(length))

        # 5. Return
        return password