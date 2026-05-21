class VaultServiceError(Exception):
    """Error occured at application level, in the Vault service context"""

class UnknownError(VaultServiceError):
    """Unknown error of VaultServiceError"""