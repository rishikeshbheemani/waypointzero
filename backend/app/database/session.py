import logging
from collections.abc import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import settings
from app.models.trip import Base

logger = logging.getLogger(__name__)

# Determine database URL with SQLite local fallback
raw_url = settings.DATABASE_URL.strip() if settings.DATABASE_URL else ""
if not raw_url:
    raw_url = "sqlite:///./waypointzero.db"

if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)


def _build_engine(url: str):
    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )
    try:
        # Quick 2-second timeout probe for PostgreSQL
        probe_engine = create_engine(
            url,
            connect_args={"connect_timeout": 2},
            pool_pre_ping=True,
        )
        with probe_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Connected to remote PostgreSQL database.")
        return probe_engine
    except Exception as err:
        logger.warning(
            f"Unable to connect to PostgreSQL ({err}). Falling back to local SQLite 'waypointzero.db'."
        )
        return create_engine(
            "sqlite:///./waypointzero.db",
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )


engine = _build_engine(raw_url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def init_db() -> None:
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}")


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database session lifecycle."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """Check database liveness."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False