import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet


# Default salt (replace with securely stored random salt in production)
DEFAULT_SALT = b"nexa_salt"


def derive_fernet(password: str, salt: bytes = DEFAULT_SALT, iterations: int = 200_000) -> Fernet:
    """
    Derive a Fernet instance from a master password using PBKDF2-HMAC-SHA256.

    Args:
        password (str): The master password provided by the user.
        salt (bytes): The salt for key derivation. Should be securely random
                      and stored alongside the hash in production.
        iterations (int): Number of PBKDF2 iterations. Default is 200,000.

    Returns:
        Fernet: A Fernet instance for encryption and decryption.
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")
    if not isinstance(salt, (bytes, bytearray)):
        raise TypeError("Salt must be bytes.")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
    return Fernet(key)