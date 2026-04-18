import hashlib
import hmac
import os
import secrets


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    )
    return f"{salt}${password_hash.hex()}"


def verify_password(password: str, stored_password: str) -> bool:
    try:
        salt, password_hash = stored_password.split("$", maxsplit=1)
    except ValueError:
        return False

    computed_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()
    return hmac.compare_digest(computed_hash, password_hash)
