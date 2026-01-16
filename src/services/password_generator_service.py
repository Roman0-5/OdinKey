from pathlib import Path
from src.crypto.generator import PasswordGenerator
class PasswordGeneratorService:
    def __init__(self):
        self.generator = PasswordGenerator()
        self.wordlist = self._load_wordlist()
    def _load_wordlist(self) -> list[str]:
        try:
            wordlist_path = Path(__file__).parent.parent / 'data' / 'words.txt'

            if wordlist_path.exists():
                words = []
                with open(wordlist_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()

                        if not line or line.startswith('#'):
                            continue
                        if '\t' in line:
                            _, word = line.split('t', 1)
                            words.append(word.strip())
                        else:
                            words.append(line)
                if words:
                    print(f"Loaded {len(words)} words from {wordlist_path}")
                    return words
        except Exception as e:
            print(f"Failed to load wordlist: {e}")
        return self.wordlist


    def generate_password(self, length: int = 12,
                          use_uppercase: bool = True,
                          use_lowercase: bool = True,
                          use_digits: bool = True,
                          use_special: bool = True,
                          algorithm: str = "random") -> dict:
        try:

            if algorithm == "random":
                password = self.generator.generate_random(
                    length=length,
                    use_uppercase=use_uppercase,
                    use_lowercase=use_lowercase,
                    use_digits=use_digits,
                    use_special=use_special
                )
            elif algorithm == "pronounceable":
                password = self
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