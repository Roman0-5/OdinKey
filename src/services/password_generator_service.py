from src.crypto.generator import PasswordGenerator
class PasswordGeneratorService:
    def generate_password(self, length: int = 12,
                          use_uppercase: bool = True,
                          use_lowercase: bool = True,
                          use_digits: bool = True,
                          use_special: bool = True) -> dict:
        try:
            password = PasswordGenerator.generate(
                length=length,
                use_uppercase=use_uppercase,
                use_lowercase=use_lowercase,
                use_digits=use_digits,
                use_special=use_special
            )

            return {
                'success': True,
                'password': password
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }