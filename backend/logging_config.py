"""Centralized logging configuration for VacanceAI Backend"""

import os
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(__file__), "log_apps")


def setup_logging():
    """Configure logging with rotating file handlers.

    Log files (in log_apps/):
      - app.log       General application logs
      - agents.log    AI agent activity (orchestrator, UI, database agents)
      - sql.log       Database queries and operations
      - errors.log    ERROR+ from all loggers
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    def _rotating(filename, level=logging.DEBUG):
        h = RotatingFileHandler(
            os.path.join(LOG_DIR, filename),
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8",
        )
        h.setLevel(level)
        h.setFormatter(fmt)
        return h

    # --- Root logger (console) ---
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    root.addHandler(console)

    # --- App log (everything INFO+) ---
    app_handler = _rotating("app.log", logging.INFO)
    root.addHandler(app_handler)

    # --- Errors log (ERROR+ from all loggers) ---
    err_handler = _rotating("errors.log", logging.ERROR)
    root.addHandler(err_handler)

    # --- Agents log ---
    agents_logger = logging.getLogger("agents")
    agents_logger.setLevel(logging.DEBUG)
    agents_logger.addHandler(_rotating("agents.log"))

    # --- SQL / Database log ---
    db_logger = logging.getLogger("database")
    db_logger.setLevel(logging.DEBUG)
    db_logger.addHandler(_rotating("sql.log"))

    # Reduce noise from third-party libs
    for noisy in ("httpcore", "httpx", "urllib3", "asyncio", "hpack", "markdown_it"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
