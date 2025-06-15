def _get_link(endpoint: str, base_url: str, token: str, redirect_uri: str | None):
    link = f"{base_url.rstrip('/')}/api/auth/{endpoint}?token={token}"
    if redirect_uri:
        link = f"{link}&redirectUri={redirect_uri}"
    return link


def get_verification_link(base_url: str, token: str, redirect_uri: str | None):
    return _get_link("verify", base_url, token, redirect_uri)


def get_2fa_link(base_url: str, token: str, redirect_uri: str | None):
    return _get_link("verify-login", base_url, token, redirect_uri)
