from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    email: str
    username: str
    first_name: str
    last_name: str

class User(UserBase, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    verified: bool

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    verified: bool

class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None

class UserExists(SQLModel):
    exists: bool