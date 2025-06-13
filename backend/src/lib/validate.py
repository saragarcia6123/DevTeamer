import re
from password_validator import PasswordValidator
from email_validator import validate_email, EmailNotValidError


def normalize_email(email: str) -> str:
    try:
        emailinfo = validate_email(email)
        return emailinfo.normalized.lower()
    except EmailNotValidError as e:
        raise e


def validate_username(username: str):
    """Ensure only alphanumeric and underscore usernames"""
    return re.match(r'^[a-zA-Z0-9_]{3,}$', username)


def validate_password(password: str):
    """Enforce strict password requirements"""

    if PasswordValidator() \
            .spaces() \
            .validate(password):
        return "Password cannot contain spaces."

    ILLEGAL_SYMBOLS = [';', '|', '&', '$', '<', '>']

    if any(s in password for s in ILLEGAL_SYMBOLS):
        return f"Password cannot contain any of {', '.join(ILLEGAL_SYMBOLS)}"

    MIN_CHARS = 8
    MAX_CHARS = 50

    if not PasswordValidator() \
            .min(MIN_CHARS) \
            .max(MAX_CHARS) \
            .validate(password):
        return (
            f"Password must be between",
            "{MIN_CHARS} and {MAX_CHARS} characters long."
        )

    if not PasswordValidator() \
            .lowercase() \
            .uppercase() \
            .validate(password):
        return "Password must contain a lowercase and an uppercase letter."

    if not PasswordValidator().digits().validate(password):
        return "Password must contain a digit."

    if not PasswordValidator().symbols().validate(password):
        return "Password must contain a special symbol."

    return False
