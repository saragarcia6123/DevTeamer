from pydantic import EmailStr, field_validator
from sqlmodel import SQLModel, Field

from lib.validators import validate_name, validate_password, validate_username


class UserBase(SQLModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)

    @field_validator("username")
    @classmethod
    def _validate_username(cls, username: str) -> str:
        return validate_username(username)

    @field_validator("first_name", "last_name")
    @classmethod
    def _validate_name(cls, name: str) -> str:
        return validate_name(name)


class User(UserBase, table=True):
    __tablename__: str = "users"
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    verified: bool


class UserCreate(UserBase):
    password: str = Field(nullable=False)

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        return validate_password(password)


class UserRead(UserBase):
    id: int
    verified: bool


class UserUpdate(UserBase):
    username: str | None = Field(None, min_length=3, max_length=50)
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)

    email: EmailStr = Field(exclude=True)
