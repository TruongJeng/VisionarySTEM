from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.config import MYSQL_URL

# Create the SQLAlchemy Engine
engine = create_engine(
    MYSQL_URL,
    pool_pre_ping=True, # check connection before use
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
