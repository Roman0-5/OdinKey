from src.crypto.generator import PasswordGenerator
class PasswordGeneratorService:
    WORLDLISTE = ["correct", "horse", "battery", "staple", "dragon", "wizard", "castle",
        "forest", "mountain", "ocean", "thunder", "lightning", "phoenix", "tiger",
        "eagle", "river", "sunset", "rainbow", "diamond", "crystal", "silver",
        "golden", "mystic", "shadow", "flame", "frost", "storm", "blade", "shield",
        "knight", "crown", "spirit", "magic", "power", "energy", "cosmic", "stellar",
        "ancient", "royal", "noble", "brave", "swift", "strong", "wise", "bright"]
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