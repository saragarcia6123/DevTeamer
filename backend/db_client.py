from sqlmodel import Session, create_engine, SQLModel, func, select

from models import User
from config import Config

class DBClient:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBClient, cls).__new__(cls)
            cls.instance._init()
        return cls.instance

    def _init(self):
        config = Config()
        DB_URL = f"postgresql+psycopg2://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"

        self.engine = create_engine(DB_URL)
        SQLModel.metadata.create_all(self.engine)

    def get_users(self):
        with Session(self.engine) as session:
            users = session.exec(select(User)).all()
            return users
    
    def get_user(self, identifier: str) -> User | None:
        user: User | None = None
        if '@' in identifier:
            user = self.get_user_by_email(identifier)
        else:
            user = self.get_user_by_username(identifier)
        return user
    
    def get_user_by_username(self, username: str) -> User | None:
        with Session(self.engine) as session:
            statement = select(User).where(func.lower(User.username) == username.lower())
            result = session.exec(statement)
            user = result.first()
            return user
    
    def get_user_by_email(self, email: str) -> User | None:
        with Session(self.engine) as session:
            statement = select(User).where(func.lower(User.email) == email.lower())
            result = session.exec(statement)
            user = result.first()
            return user

    def insert_user(self, user: User):
        with Session(self.engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    
    def delete_user(self, user_id: int):
        with Session(self.engine) as session:
            user = session.get(User, user_id)
            if user:
                session.delete(user)
                session.commit()
    
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