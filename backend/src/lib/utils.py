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
