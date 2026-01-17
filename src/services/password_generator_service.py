import string
from pathlib import Path
from src.crypto.generator import PasswordGenerator

class PasswordGeneratorService:
    DEFAULT_WORDLIST = [
        "dragon", "tiger", "eagle", "phoenix", "wizard", "castle",
        "forest", "mountain", "ocean", "thunder", "lightning", "storm",
        "knight", "crown", "blade", "shield", "spirit", "mystic",
        "brave", "swift", "strong", "wise", "bright", "hidden"
    ]

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
                            _, word = line.split('\t', 1)
                            words.append(word.strip())
                        else:
                            words.append(line)
                if words:
                    print(f"Loaded {len(words)} words from {wordlist_path}")
                    return words
        except Exception as e:
            print(f"Failed to load wordlist: {e}")
        return self.DEFAULT_WORDLIST

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
                password = self._generate_pronounceable(
                    length=length,
                    use_digits=use_digits,
                    use_special=use_special
                )

            elif algorithm == "passphrase":
                num_words = (max(2, min(length // 5, 8)))
                password = self._generate_passphrase(
                    num_words=num_words,
                    use_digits=use_digits,
                    use_special=use_special
                )

            elif algorithm == "pattern":
                password = self._generate_pattern(
                    use_uppercase=use_uppercase,
                    use_lowercase=use_lowercase,
                    use_digits=use_digits,
                    use_special=use_special
                )

            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            return {
                'success': True,
                'password': password,
                'length': len(password)
            }

        except Exception as e:
            return{
                'success': False,
                'error': str(e)
            }
    def generate_with_wildcard(self, template: str) -> dict:
        try:
            password = self.generator.generate_from_template(template)

            return{
                'success': True,
                'password': password,
                'length': len(password)
            }
        except Exception as e:
            return{
                'success': False,
                'error': str(e)
            }
    def _generate_pronounceable(
            self,
            length: int,
            use_digits: bool,
            use_special: bool
    ) -> str:
        vowels = 'aeiou'
        consonants = 'bcdfghjklmnpqrstvwxyz'
        password= []

        target_length = length
        if use_digits:
            target_length -= 2
        if use_special:
            target_length -= 1

        target_length = max(6, target_length)

        for i in range(target_length):
            if i % 2 == 0:
                char = self.generator.random.choice(consonants)
                if i == 0:
                    char = char.upper()
                password.append(char)
            else:
                password.append(self.generator.random.choice(vowels))

        if use_digits:
            digit1 = self.generator.get_random_digit()
            digit2 = self.generator.get_random_digit()
            password.append(f"{digit1}{digit2}")

        if use_special:
            password.append(self.generator.get_random_special())

        return ''.join(password)


    def _generate_passphrase(
            self,
            num_words: int,
            use_digits: bool,
            use_special: bool
    ) -> str:
        num_words = max(2, num_words)
        words = [
            self.generator.random.choice(self.wordlist)
            for _ in range(num_words)
        ]
        words[0] = words[0].capitalize()

        if use_digits:
            digit1 = self.generator.get_random_digit()
            digit2 = self.generator.get_random_digit()
            words.append(f"{digit1}{digit2}")
        if use_special:
            words.append(self.generator.get_random_special())
        return ''.join(words)


    def _generate_pattern(
            self,
            use_uppercase: bool,
            use_lowercase: bool,
            use_digits: bool,
            use_special: bool
    ) -> str:
        pattern = []
        # first word
        if use_uppercase:
            pattern.append(self.generator.get_random_letter(uppercase=True))
        if use_lowercase:
            for _ in range(2):
                pattern.append(self.generator.get_random_letter(uppercase=False))
        # seperator
        if pattern:
            pattern.append('-')
        # second word
        if use_uppercase:
            pattern.append(self.generator.get_random_letter(uppercase=True))

        if use_lowercase:
            for _ in range(2):
                pattern.append(self.generator.get_random_letter(uppercase=False))

        if pattern and pattern[-1] != '-':
            pattern.append('-')
        # digits
        if use_digits:
            for _ in range(2):
                pattern.append(self.generator.get_random_digit())
            pattern.append('-')
        # special characters
        if use_special:
            for _ in range(2):
                pattern.append(self.generator.get_random_special())

        result = ''.join(pattern)
        if result.endswith('-'):
            result = result[:-1]
        return result

# short test methods
if __name__ == "__main__":
    print("=== PasswordGeneratorService Tests ===\n")

    service = PasswordGeneratorService()
    print(f"Wordlist: {len(service.wordlist)} words\n")

    # Test all algorithms
    tests = [
        ("random", 16),
        ("pronounceable", 12),
        ("passphrase", 4),
        ("pattern", 16)
    ]

    for algo, length in tests:
        result = service.generate_password(length=length, algorithm=algo)
        if result['success']:
            print(f"{algo.capitalize():15} : {result['password']}")

    # Test wildcard
    print("\nWildcard:")
    result = service.generate_with_wildcard("OdinKey-####-@@@@")
    if result['success']:
        print(f"{'Template':15} : {result['password']}")

    print("\n✓ All tests completed!")