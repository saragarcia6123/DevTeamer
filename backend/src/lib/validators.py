import re
import unicodedata
from password_validator import PasswordValidator


def validate_username(username: str) -> str:
    """Ensure only alphanumeric and underscore usernames"""
    if not re.match(r"^[a-zA-Z0-9_]{3,}$", username):
        raise ValueError(
            "Username must only contain",
            "alphanumeric characters and underscores,",
            "and be at least 3 characters long.",
        )
    return username.lower()


def validate_name(name: str) -> str:
    """Validate names supporting international characters"""
    name = name.strip()

    if len(name) > 100:
        raise ValueError("Name must be no more than 100 characters long")

    for char in name:
        category = unicodedata.category(char)
        if not (
            category.startswith(
                "L"
            )  # All letter categories (Latin, Chinese, Cyrillic, etc.)
            or category.startswith("M")  # Marks (accents, diacritics)
            or char in [" ", "-", "'", "."]  # Common name punctuation
        ):
            raise ValueError(f"Invalid character '{char}' in name")

    return name


def validate_password(password: str) -> str:
    """Enforce strict password requirements"""

    if PasswordValidator().spaces().validate(password):
        raise ValueError("Password cannot contain spaces.")

    ILLEGAL_SYMBOLS = [";", "|", "&", "$", "<", ">"]

    if any(s in password for s in ILLEGAL_SYMBOLS):
        raise ValueError(f"Password cannot contain any of {', '.join(ILLEGAL_SYMBOLS)}")

    MIN_CHARS = 8
    MAX_CHARS = 50

    if not PasswordValidator().min(MIN_CHARS).max(MAX_CHARS).validate(password):
        raise ValueError(
            f"Password must be between {MIN_CHARS} and {MAX_CHARS} characters long."
        )

    if not PasswordValidator().lowercase().uppercase().validate(password):
        raise ValueError("Password must contain a lowercase and an uppercase letter.")

    if not PasswordValidator().digits().validate(password):
        raise ValueError("Password must contain a digit.")

    if not PasswordValidator().symbols().validate(password):
        raise ValueError("Password must contain a special symbol.")

    return password
