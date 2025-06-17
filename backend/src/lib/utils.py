from datetime import datetime, timezone
from fastapi import Request


def now():
    """Ensure consistent timezone throughout app"""
    return datetime.now(timezone.utc)


def mask_email(email: str) -> str:
    """
    Basic email masking: shows first character + *** + @domain
    example@gmail.com -> e***@gmail.com
    """

    local, domain = email.split("@", 1)
    if len(local) <= 1:
        return email

    masked_local = local[0] + "*" * 3  # Don't reveal how long local is
    return f"{masked_local}@{domain}"


def get_client_ip(request: Request) -> str | None:
    # Check common proxy headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in case of multiple proxies
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to direct connection
    ip = request.client.host if request.client else None

    return ip
