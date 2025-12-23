"""
Services Modul
Eine API-ähnliche Schnittstelle damit ein Mid/Communication-Layer erstellt wird
master_account_service: Masteraccount Operationen
password_generator_service: Passwortgenerierung
password_profile_service: Passwortprofil CRUD

Services koordinieren Core, Crypto, und Datenbank Module

Wege bereits hinzugefügt damit für GUI/CLI die Imports kürzer sind
"""

from .master_account_service import MasterAccount
from .password_generator_service import PasswordGeneratorService
#from .password_profile_service import PasswordProfileService

""""
__all__ = [
    'MasterAccountService',
    'PasswordGeneratorService',
    'PasswordProfileService'
]
"""