from fastapi import HTTPException


class AuthenticationException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=400, detail="Authentication error.")


# Debug only
class IncorrectPasswordException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=400, detail="Incorrect password.")


class UnauthorizedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Unauthorized.")


class UnverifiedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=403, detail="User not verified. Please check your email."
        )


class UserNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=404, detail="User not found.")
