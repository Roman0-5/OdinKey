from typing import Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PasswordProfile:

    """
    Modelklasse für einen Passwort-Eintrag
    Diese Klasse dient als Datencontainer (hält Infos des Profils im Arbeitsspeicher)
    WICHTIG: Passwort leigt hier im Klartext vor / Verschlüsselung passiert erst
    """

    #Pflichtfelder für die Initialisierung
    user_id: int # Fremdschlüssel: zu welchen Masteraccount gehört dieser Eintrag?
    service_name: str #Name des Diensts (Amazon, Netflix usw.)
    url: str
    username: str
    password: str

    #Optionale Felder mit Standardwerten
    id: Optional[int] = None # Datenbank-ID (erst nach speichern vorhanden)
    notes: Optional[str] = None #Freitext Notizen des Nutzers
    created_at: Optional[str] = None #Zeitstempel der Erstellung (ISO-Format)

    def __post_init__(self):
        #Sezielle Methode von DataClass - wird automatisch nach Erstellung des Objekts ausgeführt
        #Setzt das Datum automatisch, falls keins übergeben wurde
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    """
    Überprüfungen von Feldern
    """

    @staticmethod
    def validate_service_name(name: str) -> tuple[bool, str]:
        if not name or not name.strip():
            return False, "Service-Name darf nicht leer sein"
        if len(name) > 25:
            return False, "Service-Name darf nicht über 25 Zeichen lang sein"
        return True, ""

    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        if not username or not username.strip():
            return False, "Username darf nicht leer sein"
        if len(username) > 50:
            return False, "Username darf nicht über 50 Zeichen lang sein"
        return True, ""

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        if not password or not password.strip():
            return False, "Password darf nicht leer sein"
        return True, ""

    @staticmethod
    def validate_url(url: str) -> tuple[bool, str]:
        if not url or not url.strip():
            return False, "URL darf nicht leer sein"
        return True, ""

    @staticmethod
    def get_example_text(field: str) -> str:
        #liefert Beispieltexte für UI (placeholder) - hilft für Verständnis was in Felder gehört
        examples = {
            "password": "Supersicher321",
            "service_name": "Github Account",  # Angepasst an snake_case
            "username": "GithubUser",
            "url": "https://github.com",
            "notes": "Mein privater Account"
        }
        return examples.get(field, '')

    """
    Konvertierungs-Methoden (für GUI und Datenbank)
    """

    def to_dict(self) -> dict:
        # Wandelt das Objekt in dictionary um - für JSON oder GUI-Tabellen
        return {
            "id": self.id,
            "user_id": self.user_id,
            "service_name": self.service_name,
            "url": self.url,
            "username": self.username,
            "password": self.password,
            "notes": self.notes,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PasswordProfile':
        # Erstellt ein PasswordProfile-Objekt aus einem dictionary (z.B. aus DB-Daten)
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            service_name=data.get("service_name"),
            url=data.get("url"),
            username=data.get("username"),  # Hier hieß es vorher "name"
            password=data.get("password"),
            notes=data.get("notes"),
            created_at=data.get("created_at")
        )


