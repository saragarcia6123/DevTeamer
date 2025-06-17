def _get_link(endpoint: str, base_url: str, token: str, client_url: str | None):
    base_url = base_url.rstrip("/")
    if client_url:
        client_url = client_url.rstrip("/")

    if client_url:
        link = f"{client_url}?token={token}"
    else:
        link = f"{base_url}/api/auth/{endpoint}?token={token}"

    return link


def get_verification_link(base_url: str, token: str, client_url: str | None):
    return _get_link("verify-email", base_url, token, client_url)


def get_2fa_link(base_url: str, token: str, client_url: str | None):
    return _get_link("confirm-login", base_url, token, client_url)
