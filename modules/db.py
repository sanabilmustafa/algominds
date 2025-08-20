from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
import config

DB_URI = f"postgresql://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"

engine = create_engine(DB_URI, pool_pre_ping=True)

# Use scoped_session for thread safety
SessionLocal = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()


