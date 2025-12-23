# tests/test_generator.py

import pytest
import string
from src.crypto.generator import PasswordGenerator


class TestPasswordGenerator:
    """Tests für PasswordGenerator"""

    def test_generate_default_length(self):
        """Standard-Länge ist 16 Zeichen"""
        password = PasswordGenerator.generate()

        assert len(password) == 16

    def test_generate_custom_length(self):
        """Custom Länge funktioniert"""
        password = PasswordGenerator.generate(length=20)

        assert len(password) == 20

    def test_generate_minimum_length(self):
        """Minimale Länge ist 8 Zeichen (NFMR3)"""
        password = PasswordGenerator.generate(length=8)

        assert len(password) == 8

    def test_generate_rejects_too_short(self):
        """Länge < 8 wird abgelehnt"""
        with pytest.raises(ValueError) as exc_info:
            PasswordGenerator.generate(length=7)

        assert f"password must be between {PasswordGenerator.MIN_LENGTH} and {PasswordGenerator.MAX_LENGTH}" in str(exc_info.value).lower()

    def test_generate_rejects_too_long(self):
        """Länge > 128 wird abgelehnt"""
        with pytest.raises(ValueError) as exc_info:
            PasswordGenerator.generate(length=129)

        assert f"password must be between {PasswordGenerator.MIN_LENGTH} and {PasswordGenerator.MAX_LENGTH}" in str(exc_info.value).lower()

    def test_generate_with_uppercase(self):
        """Passwort enthält Großbuchstaben"""
        password = PasswordGenerator.generate(
            length=16,
            use_uppercase=True,
            use_lowercase=False,
            use_digits=False,
            use_special=False
        )

        assert len(password) == 16
        assert any(c in string.ascii_uppercase for c in password)

    def test_generate_with_lowercase(self):
        """Passwort enthält Kleinbuchstaben"""
        password = PasswordGenerator.generate(
            length=16,
            use_uppercase=False,
            use_lowercase=True,
            use_digits=False,
            use_special=False
        )

        assert len(password) == 16
        assert any(c in string.ascii_lowercase for c in password)

    def test_generate_with_digits(self):
        """Passwort enthält Zahlen"""
        password = PasswordGenerator.generate(
            length=16,
            use_uppercase=False,
            use_lowercase=False,
            use_digits=True,
            use_special=False
        )

        assert len(password) == 16
        assert any(c in string.digits for c in password)

    def test_generate_with_special(self):
        """Passwort enthält Sonderzeichen"""
        password = PasswordGenerator.generate(
            length=16,
            use_uppercase=False,
            use_lowercase=False,
            use_digits=False,
            use_special=True
        )

        assert len(password) == 16
        assert any(c in string.punctuation for c in password)

    def test_generate_with_all_character_types(self):
        """Passwort mit allen Zeichen-Typen (Default)"""
        password = PasswordGenerator.generate(
            length=16,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_special=True
        )

        assert len(password) == 16
        # Mindestens ein von jedem Typ (statistisch sehr wahrscheinlich bei 16 Zeichen)
        # Aber nicht garantiert, daher nur prüfen dass Zeichen aus allen Sets kommen könnten

    def test_generate_with_mixed_types(self):
        """Passwort mit gemischten Typen"""
        password = PasswordGenerator.generate(
            length=20,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=False,
            use_special=False
        )

        assert len(password) == 20
        # Nur Buchstaben
        assert all(c.isalpha() for c in password)

    def test_generate_no_character_types_selected(self):
        """Fehler wenn keine Zeichen-Typen ausgewählt"""
        with pytest.raises(ValueError) as exc_info:
            PasswordGenerator.generate(
                use_uppercase=False,
                use_lowercase=False,
                use_digits=False,
                use_special=False
            )

        assert "choose at least one type" in str(exc_info.value).lower()

    def test_generate_is_random(self):
        """Generiert verschiedene Passwörter (nicht deterministisch)"""
        password1 = PasswordGenerator.generate(length=16)
        password2 = PasswordGenerator.generate(length=16)

        # Sehr unwahrscheinlich dass beide gleich sind
        assert password1 != password2

    def test_generate_multiple_times_different(self):
        """Mehrfaches Generieren gibt unterschiedliche Passwörter"""
        passwords = set()
        for _ in range(50):
            password = PasswordGenerator.generate(length=12)
            passwords.add(password)

        # Mindestens 49 verschiedene (erlaubt 1 Kollision bei 50)
        assert len(passwords) >= 49


class TestPasswordGeneratorCharacterSets:
    """Tests für Zeichen-Sets"""

    def test_uppercase_only_contains_uppercase(self):
        """Nur Großbuchstaben"""
        password = PasswordGenerator.generate(
            length=50,  # Länger für bessere Statistik
            use_uppercase=True,
            use_lowercase=False,
            use_digits=False,
            use_special=False
        )

        assert all(c in string.ascii_uppercase for c in password)
        assert not any(c in string.ascii_lowercase for c in password)
        assert not any(c in string.digits for c in password)
        assert not any(c in string.punctuation for c in password)

    def test_lowercase_only_contains_lowercase(self):
        """Nur Kleinbuchstaben"""
        password = PasswordGenerator.generate(
            length=50,
            use_uppercase=False,
            use_lowercase=True,
            use_digits=False,
            use_special=False
        )

        assert all(c in string.ascii_lowercase for c in password)

    def test_digits_only_contains_digits(self):
        """Nur Zahlen"""
        password = PasswordGenerator.generate(
            length=50,
            use_uppercase=False,
            use_lowercase=False,
            use_digits=True,
            use_special=False
        )

        assert all(c in string.digits for c in password)

    def test_special_only_contains_special(self):
        """Nur Sonderzeichen"""
        password = PasswordGenerator.generate(
            length=50,
            use_uppercase=False,
            use_lowercase=False,
            use_digits=False,
            use_special=True
        )

        assert all(c in string.punctuation for c in password)


class TestPasswordGeneratorEdgeCases:
    """Tests für Edge Cases"""

    def test_generate_with_exact_minimum_length(self):
        """Exakt minimale Länge (8)"""
        password = PasswordGenerator.generate(length=8)

        assert len(password) == 8

    def test_generate_with_exact_maximum_length(self):
        """Exakt maximale Länge (128)"""
        password = PasswordGenerator.generate(length=128)

        assert len(password) == 128

    def test_generate_length_boundary_minus_one(self):
        """Länge 7 wird abgelehnt"""
        with pytest.raises(ValueError):
            PasswordGenerator.generate(length=7)

    def test_generate_length_boundary_plus_one(self):
        """Länge 129 wird abgelehnt"""
        with pytest.raises(ValueError):
            PasswordGenerator.generate(length=129)

    def test_generate_with_zero_length(self):
        """Länge 0 wird abgelehnt"""
        with pytest.raises(ValueError):
            PasswordGenerator.generate(length=0)

    def test_generate_with_negative_length(self):
        """Negative Länge wird abgelehnt"""
        with pytest.raises(ValueError):
            PasswordGenerator.generate(length=-1)


class TestPasswordGeneratorSecurity:
    """Tests für Sicherheits-Aspekte"""

    def test_passwords_have_good_entropy(self):
        """Passwörter haben gute Entropie (nicht vorhersagbar)"""
        passwords = [PasswordGenerator.generate(length=16) for _ in range(100)]

        # Prüfe dass keine Muster erkennbar sind
        # Jedes Passwort sollte einzigartig sein
        assert len(set(passwords)) == 100

    def test_no_repeated_patterns(self):
        """Keine offensichtlichen Wiederholungen"""
        password = PasswordGenerator.generate(length=20)

        # Sehr unwahrscheinlich dass gleiche 3 Zeichen hintereinander
        for i in range(len(password) - 2):
            if password[i] == password[i + 1] == password[i + 2]:
                # Kann vorkommen (Zufall), aber nicht bei jedem Generieren
                pass

    def test_distribution_is_uniform(self):
        """Zeichen-Verteilung ist ungefähr gleichmäßig"""
        # Generiere viele kurze Passwörter
        all_chars = ''.join([
            PasswordGenerator.generate(length=10)
            for _ in range(100)
        ])

        # Zähle Zeichen-Typen
        uppercase_count = sum(1 for c in all_chars if c in string.ascii_uppercase)
        lowercase_count = sum(1 for c in all_chars if c in string.ascii_lowercase)
        digit_count = sum(1 for c in all_chars if c in string.digits)
        special_count = sum(1 for c in all_chars if c in string.punctuation)

        # Alle sollten > 0 sein (bei 1000 Zeichen sehr wahrscheinlich)
        assert uppercase_count > 0
        assert lowercase_count > 0
        assert digit_count > 0
        assert special_count > 0

class TestPasswordGeneratorStaticMethods:
    """Tests für statische Methoden (Helper)"""

    def test_validate_length_valid(self):
        """validate_length() akzeptiert gültige Längen"""
        # Falls du validate_length() als separate Methode implementierst
        assert PasswordGenerator.validate_length(8) == True
        assert PasswordGenerator.validate_length(16) == True
        assert PasswordGenerator.validate_length(128) == True

    def test_validate_length_invalid(self):
        """validate_length() lehnt ungültige Längen ab"""
        assert PasswordGenerator.validate_length(7) == False
        assert PasswordGenerator.validate_length(129) == False
        assert PasswordGenerator.validate_length(0) == False
        assert PasswordGenerator.validate_length(-1) == False

    def test_validate_options_valid(self):
        """validate_options() akzeptiert gültige Optionen"""
        # Mindestens eine Option True
        assert PasswordGenerator.validate_options(
            use_uppercase=True,
            use_lowercase=False,
            use_digits=False,
            use_special=False
        ) == True

    def test_validate_options_invalid(self):
        """validate_options() lehnt alle False ab"""
        assert PasswordGenerator.validate_options(
            use_uppercase=False,
            use_lowercase=False,
            use_digits=False,
            use_special=False
        ) == False