import pytest
import string
from src.services.password_generator_service import PasswordGeneratorService


class TestPasswordGeneratorService:

    def test_generate_password_length(self):
        """Testet, ob das Passwort die gewünschte Länge hat."""
        service = PasswordGeneratorService()
        password = service.generate_password(length=16)
        assert len(password) == 16

    def test_generate_password_defaults(self):
        """Testet, ob standardmäßig alles (Groß, Klein, Zahlen, Sonderzeichen) an ist."""
        service = PasswordGeneratorService()
        # Wir generieren ein langes Passwort, um die Wahrscheinlichkeit zu maximieren, dass alle Typen vorkommen
        password = service.generate_password(length=100)

        has_upper = any(c in string.ascii_uppercase for c in password)
        has_lower = any(c in string.ascii_lowercase for c in password)
        has_digit = any(c in string.digits for c in password)
        has_symbol = any(c in string.punctuation for c in password)

        assert has_upper and has_lower and has_digit and has_symbol

    def test_generate_password_no_upper(self):
        """Testet: use_upper=False darf KEINE Großbuchstaben enthalten."""
        service = PasswordGeneratorService()
        password = service.generate_password(length=50, use_upper_case=False)

        has_upper = any(c in string.ascii_uppercase for c in password)
        assert not has_upper, "Passwort sollte KEINE Großbuchstaben enthalten"

    def test_generate_password_no_lower(self):
        """Testet: use_lower=False darf KEINE Kleinbuchstaben enthalten."""
        service = PasswordGeneratorService()
        password = service.generate_password(length=50, use_lower_case=False)

        has_lower = any(c in string.ascii_lowercase for c in password)
        assert not has_lower, "Passwort sollte KEINE Kleinbuchstaben enthalten"

    def test_generate_password_only_digits(self):
        """Edge Case: Nur Zahlen."""
        service = PasswordGeneratorService()
        password = service.generate_password(
            length=20,
            use_upper_case=False,
            use_lower_case=False,
            use_symbols=False,
            use_digits=True
        )

        # Prüfen, ob wirklich NUR Zahlen drin sind
        assert password.isdigit()
        assert len(password) == 20

    def test_generate_password_error_if_nothing_selected(self):
        """(Optional) Sollte einen Fehler werfen, wenn gar nichts ausgewählt ist."""
        service = PasswordGeneratorService()
        with pytest.raises(ValueError):
            service.generate_password(
                use_upper_case=False,
                use_lower_case=False,
                use_symbols=False,
                use_digits=False
            )