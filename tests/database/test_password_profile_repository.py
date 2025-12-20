import pytest
import os
from src.core.password_profile import PasswordProfile
from src.database.connection import DatabaseConnection
from src.database.password_profile_repository import PasswordProfileRepository


class TestPasswordProfileRepository:

    @pytest.fixture
    def db_connection(self, tmp_path):
        """
        Erstellt eine temporäre Datei-Datenbank für den Test.
        ':memory:' funktioniert hier nicht, weil die DatabaseConnection
        die Verbindung nach dem Erstellen der Tabellen schließt
        (und damit die Memory-DB löscht).
        """
        # 1. Temporären Pfad erstellen (Pytest managed das Aufräumen)
        db_file = tmp_path / "test_odinkey.db"

        # 2. Connection mit diesem Pfad erstellen
        conn = DatabaseConnection(str(db_file))

        # 3. Tabellen erstellen (werden jetzt in die Datei geschrieben)
        conn.create_tables()

        return conn

    def test_create_and_retrieve_profile(self, db_connection):
        # 1. Vorbereitung
        dummy_key = b'0' * 32  # Fake Key (32 Bytes für AES-256)

        # Repository initialisieren
        repo = PasswordProfileRepository(db_connection, dummy_key)

        # Ein Test-Profil erstellen
        profile = PasswordProfile(
            user_id=1,
            service_name="Amazon",
            url="https://amazon.de",
            username="roman@test.de",
            password="MeinGeheimesPassword123!",
            notes="Privater Account"
        )

        # 2. Ausführen: Speichern
        saved_id = repo.create_profile(profile)

        # 3. Prüfen: Wurde eine ID vergeben?
        assert saved_id is not None
        assert isinstance(saved_id, int)

        # 4. Ausführen: Laden (anhand der ID)
        loaded_profile = repo.get_profile_by_id(saved_id)

        # 5. Prüfen: Sind die Daten korrekt zurückgekommen?
        assert loaded_profile.service_name == "Amazon"
        assert loaded_profile.username == "roman@test.de"

        # DER WICHTIGSTE TEST:
        # Das Repo muss das Passwort entschlüsselt haben
        assert loaded_profile.password == "MeinGeheimesPassword123!"