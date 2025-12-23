import secrets
import string
from src.crypto.generator import PasswordGenerator
class PasswordGeneratorService:
    def generate_password(self, length: int = 16,
                          use_uppercase: bool = True,
                          use_lowercase: bool = True,
                          use_digits: bool = True,
                          use_specials: bool = True) -> dict:
        try:
            password = PasswordGenerator.generate(
                length=length,
                use_uppercase=use_uppercase,
                use_lowercase=use_lowercase,
                use_digits=use_digits,
                use_special=use_specials
            )

            return {
                'sucess': True,
                'password': password
            }
        except Exception as e:
            return {
                'sucess': False,
                'error': str(e)
            }