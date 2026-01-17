from src.database.password_profile_repository import PasswordProfileRepository
from src.services.master_account_service import MasterAccountService


class PasswordProfileService:
    def __init__(self, profile_repo: PasswordProfileRepository, auth_service: MasterAccountService):
        self.profile_repo = profile_repo
        self.auth_service = auth_service

    def create_profile(self, profile):
        """Validiert und speichert ein neues Profil"""
        if not profile.service_name or not profile.username or not profile.password:
            raise ValueError("Pflichtfelder fehlen (Service, Username, Password)")

        return self.profile_repo.create_profile(profile)

    def update_profile(self, profile):
        """Aktualisiert ein Profil"""
        if not profile.id:
            raise ValueError("Profil hat keine ID")
        return self.profile_repo.update_profile(profile)

    def delete_profile_securely(self, profile_id: int, username: str, password_attempt: str):
        """
        Löscht nur, wenn das Master-Passwort korrekt ist.
        Kapselt die Logik: Auth-Check -> Delete
        """
        # 1. Sicherheits-Check (Backend-Logik)
        if not self.auth_service.login(username, password_attempt):
            raise PermissionError("Falsches Master-Passwort! Löschen verweigert.")

        # 2. Durchführung
        self.profile_repo.delete_profile(profile_id)
        return True