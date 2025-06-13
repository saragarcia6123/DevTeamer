from datetime import datetime, timezone


def now():
    """Ensure consistent timezone throughout app"""
    return datetime.now(timezone.utc)
