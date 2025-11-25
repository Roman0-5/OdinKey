from typing import Optional
class PasswordProfile:
    def __init__(self,
                 id: int = None,
                 password: str = None,
                 serviceName: str = None,
                 name: str = None,
                 notes: Optional [str] = None,
                 created_at: Optional[str] = None):
        self.id = id
        self.password = password
        self.serviceName = serviceName
        self.name = name
        self.notes = notes
        self.created_at = created_at
    """
    Überprüfungen von Feldern
    """
    @staticmethod
    def validate_name(self, name: str) -> tuple [bool, str]:
        """
        Überprüft ob Feld leer "not name" oder mit whitespace "not name.strip" gefüllt ist
        """
        if not name or not name.strip():
            return False, "Name darf nicht leer sein"
        if len(name) > 25:
            return False, "Name darf nicht über 25 Zeichen lang sein"
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
    def get_example_text(field: str) -> str: #beispieltextausgabe
        examples = {
            "password": "Supersicher321",
            "serviceName": "Github Account",
            "username": "Github"
        }
        return examples.get(field, '')
    def to_dict(self) -> dict:
        return {
            "password": self.password,
            "serviceName": self.serviceName,
            "name": self.name
        }
    @classmethod
    def from_dict(cls, data: dict) -> 'PasswordProfile':
        return cls(
            password=data.get("password"),
            serviceName=data.get("serviceName"),
            name=data.get("name"),
        )
