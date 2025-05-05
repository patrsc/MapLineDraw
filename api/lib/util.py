"""Utilities."""
import secrets
import string


def generate_id(length: int = 12) -> str:
    """Generate random ID."""
    allowed_chars = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(allowed_chars) for _ in range(length))
