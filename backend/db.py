import os
from typing import Literal
from sqlmodel import Session, create_engine, SQLModel, select
from dotenv import load_dotenv
from models import User

class DB:

    engine = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DB, cls).__new__(cls)
            cls.instance._init()
        return cls.instance

    def _init(self):
        load_dotenv()
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST") or 'localhost'
        DB_PORT = os.getenv("DB_PORT") or '5432'
        DB_NAME = os.getenv("DB_NAME")

        DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

        self.engine = create_engine(DB_URL, echo=False)
        SQLModel.metadata.create_all(self.engine)

    def get_users(self):
        with Session(self.engine) as session:
            users = session.exec(select(User)).all()
            return users
    
    def get_user(self, identifier: str) -> User | Literal[False]:
        user = self.get_user_by_username(identifier)
        if not user:
            # If not found by username, try email
            user = self.get_user_by_email(identifier)
        if not user:
            return False
        return user
    
    def get_user_by_username(self, username: str) -> User | None:
        with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            result = session.exec(statement)
            user = result.first()
            return user
    
    def get_user_by_email(self, email: str) -> User | None:
        with Session(self.engine) as session:
            statement = select(User).where(User.email == email)
            result = session.exec(statement)
            user = result.first()
            return user

    def insert_user(self, user: User):
        with Session(self.engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    
    def update_user(self, user: User):
        with Session(self.engine) as session:
            db_user = session.get(User, user.id)
            if not db_user:
                raise ValueError(f"User with id {user.id} not found")

            for key, value in user.model_dump(exclude_unset=True).items():
                setattr(db_user, key, value)

            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return db_user