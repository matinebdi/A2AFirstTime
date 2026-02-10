"""SQLAlchemy engine and session management for VacanceAI"""

import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from config import settings

logger = logging.getLogger("database")

engine = None
SessionLocal: sessionmaker = None


def init_engine():
    """Initialize the SQLAlchemy engine and session factory."""
    global engine, SessionLocal

    url = (
        f"oracle+oracledb://{settings.oracle_user}:{settings.oracle_password}"
        f"@{settings.oracle_host}:{settings.oracle_port}"
        f"/?service_name={settings.oracle_service}"
    )

    engine = create_engine(
        url,
        poolclass=QueuePool,
        pool_size=2,
        max_overflow=8,
        pool_pre_ping=True,
        echo=False,
    )

    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    logger.info(
        "SQLAlchemy engine initialized: %s:%s/%s",
        settings.oracle_host, settings.oracle_port, settings.oracle_service,
    )

    # Route SQLAlchemy SQL logs to sql.log via the database logger
    sa_logger = logging.getLogger("sqlalchemy.engine")
    sa_logger.setLevel(logging.INFO)
    for handler in logger.handlers:
        sa_logger.addHandler(handler)


def close_engine():
    """Dispose of the SQLAlchemy engine."""
    global engine, SessionLocal
    if engine:
        engine.dispose()
        engine = None
        SessionLocal = None
        logger.info("SQLAlchemy engine disposed")


def create_session() -> Session:
    """Create a new session (for use outside FastAPI Depends, e.g. WebSocket, agent tools)."""
    return SessionLocal()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
