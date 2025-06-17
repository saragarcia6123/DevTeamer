from sqlmodel import Session, create_engine, SQLModel, text
from config import config

PG_URL = (
    f"postgresql+psycopg2://{config.PG_USER}:{config.PG_PASSWORD}"
    f"@{config.PG_HOST}:{config.PG_PORT}/{config.PG_NAME}"
)

engine = create_engine(PG_URL)
SQLModel.metadata.create_all(engine)


# Dependency function for FastAPI
def depends_get_db():
    with Session(engine) as session:
        yield session


def get_db():
    session = Session(engine)
    try:
        return session
    finally:
        session.close()


from sqlmodel import Session, func, select
from lib.utils import mask_email
from logger import get_postgres_logger
from models import User

logger = get_postgres_logger()


def get_users(session: Session) -> list[User]:
    users = session.exec(select(User)).all()
    return list(users)


def get_user(session: Session, identifier: str) -> User | None:
    if "@" in identifier:
        return get_user_by_email(session, identifier)
    else:
        return get_user_by_username(session, identifier)


def get_user_by_username(session: Session, username: str) -> User | None:
    logger.info(f"Searching for user {username}")
    statement = select(User).where(func.lower(User.username) == username.lower())
    result = session.exec(statement)
    return result.first()


def get_user_by_email(session: Session, email: str) -> User | None:
    logger.info(f"Searching for user {mask_email(email)}")
    statement = select(User).where(func.lower(User.email) == email.lower())
    result = session.exec(statement)
    return result.first()


def insert_user(session: Session, user: User) -> User:
    logger.info(f"Inserting user {mask_email(user.email)}")
    logger.info(user.model_dump_json())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user_id: int) -> bool:
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
        return True
    return False


def update_user(session: Session, user: User) -> User:
    db_user = session.get(User, user.id)
    if not db_user:
        raise ValueError(f"User with id {user.id} not found")

    for key, value in user.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def test_connection(session: Session) -> bool:
    logger.info("Testing connection to PostgreSQL...")
    try:
        session.connection().execute(text("SELECT 1"))
        logger.info("PostgreSQL connection successful")
        return True
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        return False
