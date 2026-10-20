import logging
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import OperationalError
from app.core.config import settings

logger = logging.getLogger("latha_oils_db")

engine_kwargs = {
    "echo": settings.DEBUG,
}

if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
elif "mysql" in settings.DATABASE_URL:
    # MySQL Production Connection Pool Optimization
    engine_kwargs["pool_pre_ping"] = True      # Auto-reconnect if MySQL drops idle connections
    engine_kwargs["pool_recycle"] = 3600       # Recycle connections every hour
    engine_kwargs["pool_size"] = 10            # Keep 10 active connections
    engine_kwargs["max_overflow"] = 20

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)


def init_db() -> None:
    """Initialize database tables with automatic fallback if MySQL server is offline."""
    global engine
    try:
        SQLModel.metadata.create_all(engine)
        logger.info(f"Database connected and tables initialized using: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    except OperationalError as e:
        if "mysql" in settings.DATABASE_URL:
            logger.warning(
                f"Could not connect to MySQL server ({e}). Falling back to local SQLite 'latha_oils.db' for continuous operation."
            )
            fallback_url = "sqlite:///./latha_oils.db"
            engine = create_engine(fallback_url, connect_args={"check_same_thread": False}, echo=settings.DEBUG)
            SQLModel.metadata.create_all(engine)
            logger.info("Fallback SQLite database initialized successfully.")
        else:
            raise e


def get_session() -> Generator[Session, None, None]:
    """Dependency that yields a database session for requests."""
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()
