"""SQLAlchemy base configuration"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=settings.DEBUG,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Create base class for models
Base = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def check_database():
    """Check database connection"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return "ok"
    except Exception as e:
        logger.error("database_check_failed", error=str(e))
        return "error"

