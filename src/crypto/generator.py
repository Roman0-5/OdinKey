import secrets #NFMR3
import string
"""
secrets is die Kryptographie Library, die auch CSPRN konform ist
string ist die Zeichenset Library (ASCII, Ziffern, Zeichen)
"""

class PasswordGenerator:
    # Klassen-Konstanten
    MIN_LENGTH = 8
    MAX_LENGTH = 64
    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase
    DIGITS = string.digits
    SPECIAL = string.punctuation

    def __init__(self):
        self.random = secrets.SystemRandom() # initialize instance

    @staticmethod
    def validate_length(length: int) -> bool:
        # Länge muss innerhalb von den Konstanten sein
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

    def generate_random( #FMR4
            self,
            length: int = 16,
            use_uppercase: bool = True,
            use_lowercase: bool = True,
            use_digits: bool = True,
            use_special: bool = True
    ) -> str:
        # Validierung mit den separaten Methoden
        if not self.validate_length(length):
            raise ValueError(
                f"Password length must be between {self.MIN_LENGTH} and {self.MAX_LENGTH}"
            )

        if not self.validate_options(use_uppercase, use_lowercase, use_digits, use_special):
            raise ValueError("At least one character type must be selected")

        # initialize character pool
        char_pool = ""
        required_chars = []

        if use_uppercase:
            char_pool += self.UPPERCASE
            required_chars.append(self.random.choice(self.UPPERCASE))

        if use_lowercase:
            char_pool += self.LOWERCASE
            required_chars.append(self.random.choice(self.LOWERCASE))

        if use_digits:
            char_pool += self.DIGITS
            required_chars.append(self.random.choice(self.DIGITS))

        if use_special:
            char_pool += self.SPECIAL
            required_chars.append(self.random.choice(self.SPECIAL))

        remaining_length = length - len(required_chars)
        random_chars = [
            self.random.choice(char_pool)
            for _ in range(remaining_length)
        ]

        # combine and mix
        all_chars = required_chars + random_chars
        self.random.shuffle(all_chars)

        return ''.join(all_chars)

    def generate_from_template(self, template: str) -> str:
        """
        Wildcard function FMR6
        Wildcards:
            # - Digit (0-9)
            @ - Letter (a-z, A-Z)
            ? - Any character (letter + digit)
            ! - Special character
            Other - Literal character
        """
        if not template:
            raise ValueError("Template cannot be empty")

        result = []

        for char in template:
            if char == '#':
                # digit
                result.append(self.random.choice(self.DIGITS))
            elif char == '@':
                # letter
                result.append(self.random.choice(string.ascii_letters))
            elif char == '?':
                # character (letter + digit)
                result.append(self.random.choice(string.ascii_letters + self.DIGITS))
            elif char == '!':
                # special character
                result.append(self.random.choice(self.SPECIAL))
            else:
                # Literal character
                result.append(char)

        return ''.join(result)

    #Help_Methods for further algorithms
    def get_random_digit(self) -> str:
        return self.random.choice(self.DIGITS)
    def get_random_letter(self, uppercase: bool = None) -> str:
        if uppercase is None:
            return self.random.choice(string.ascii_letters)
        elif uppercase:
            return self.random.choice(self.UPPERCASE)
        else:
            return self.random.choice(self.LOWERCASE)
    def get_random_special(self) -> str:
        return self.random.choice(self.SPECIAL)
generator = PasswordGenerator()
# testing methods
if __name__ == "__main__":
    generator = PasswordGenerator()

    # Test 1: Random password
    password1 = generator.generate_random(length=16, use_special=True)
    print(f"Random (16 chars): {password1}")

    # Test 2: Only letters and digits
    password2 = generator.generate_random(length=12, use_special=False)
    print(f"No special (12 chars): {password2}")

    # Test 3: Wildcard template
    password3 = generator.generate_from_template("OdinKey-!#@?")
    print(f"Template: {password3}")

    # Test 4: Validation
    try:
        generator.generate_random(length=5)  # Too short
    except ValueError as e:
        print(f"Validation error: {e}")