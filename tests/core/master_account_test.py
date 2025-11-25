from src.core.master_account import MasterAccount
class TestMasterAccountPasswordValidation:
    def test_password_is_too_short(self):
        valid, error = MasterAccount.validate_password("short")
        assert not valid, "Passwort sollte ungültig sein"
        assert "8 Zeichen" in error, "Error sollte '8 Zeichen' enthalten"
    def test_validate_correct_password(self):
        valid, error = MasterAccount.validate_password("longsecurepassword")
        assert valid == True
        assert error
    def test_password_is_empty(self):
        valid, error = MasterAccount.validate_password("")
        assert valid == False
        assert "leer" in error.lower()

class TestMasterAccountUsernameValidation:
    def test_username_is_empty(self):
        valid, error = MasterAccount.validate_username("")
        assert valid == False
        assert "leer" in error.lower()