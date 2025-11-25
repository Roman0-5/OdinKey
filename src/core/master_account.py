class MasterAccount:
    "Python Dunder-Klasse -> Konstruktor"
    def __init__(self, id: int = None, username: str = None, password: str = None):
        self.id = id
        self.username = username
        self.password = password
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        if not password:
            return False, "Passwort darf nicht leer sein"
        if len(password) < 8:
            return False, "Passwort muss mindestens 8 Zeichen haben"
        return True, password

    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        if not username:
            return False, "Username darf nicht leer sein"
        return True, username
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password
        }
    @classmethod
    def from_dict(cls, data: dict) -> 'MasterAccount':
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            password=data.get('password')
        )