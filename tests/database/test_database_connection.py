# tests/database/test_database_connection.py
import pytest
import sqlite3
import os
from src.database.connection import DatabaseConnection


class TestDatabaseConnection:
    # Wir nutzen eine temporäre Datei für den Test, damit wir keine echte DB zumüllen
    TEST_DB_FILE = "test_odinkey.db"

    def teardown_method(self):
        """Aufräumen nach jedem Test: Die Test-Datenbank löschen."""
        if os.path.exists(self.TEST_DB_FILE):
            os.remove(self.TEST_DB_FILE)

    def test_connection_creation(self):
        """Testet, ob die Datenbank-Datei erstellt wird."""
        # Arrange & Act
        db = DatabaseConnection(self.TEST_DB_FILE)
        conn = db.connect()

        # Assert
        assert conn is not None
        assert os.path.exists(self.TEST_DB_FILE)
        conn.close()

    def test_tables_are_created(self):
        """Testet, ob die Tabellen 'master_account' und 'password_profiles' existieren."""
        # Arrange
        db = DatabaseConnection(self.TEST_DB_FILE)
        conn = db.connect()

        # Act: Wir führen das Erstellen der Tabellen aus
        db.create_tables()

        # Assert: Wir prüfen direkt via SQL, ob die Tabellen da sind
        cursor = conn.cursor()

        # Prüfen auf master_account
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='master_account';")
        assert cursor.fetchone() is not None, "Tabelle 'master_account' fehlt"

        # Prüfen auf password_profiles
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='password_profiles';")
        assert cursor.fetchone() is not None, "Tabelle 'password_profiles' fehlt"

        conn.close()

    def test_master_account_schema(self):
        """Testet, ob 'master_account' die kritischen Spalten hat (besonders 'salt')."""
        db = DatabaseConnection(self.TEST_DB_FILE)
        conn = db.connect()
        db.create_tables()
        cursor = conn.cursor()

        # Wir holen uns Infos über die Spalten der Tabelle
        cursor.execute("PRAGMA table_info(master_account)")
        columns = [row[1] for row in cursor.fetchall()]  # row[1] ist der Spaltenname

        assert "id" in columns
        assert "username" in columns
        assert "password_hash" in columns
        assert "salt" in columns, "Das Feld 'salt' fehlt! Wichtig für die Sicherheit."

        conn.close()

    def test_password_profiles_schema(self):
        """Testet, ob 'password_profiles' die Spalte 'nonce' und 'encrypted_data' hat."""
        db = DatabaseConnection(self.TEST_DB_FILE)
        conn = db.connect()
        db.create_tables()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(password_profiles)")
        columns = [row[1] for row in cursor.fetchall()]

        assert "id" in columns
        assert "encrypted_data" in columns
        assert "nonce" in columns, "Das Feld 'nonce' fehlt! Wichtig für AES-GCM."
        assert "user_id" in columns  # Fremdschlüssel zum Master Account

        conn.close()