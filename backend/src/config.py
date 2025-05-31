"""
Centralized configuration module for environment variables.
This module handles loading environment variables from .env file
and provides a single source of truth for configuration.
"""
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Check if we should load from environment variables only (e.g., in Docker)
LOAD_FROM_ENV = os.getenv("LOAD_FROM_ENV", "").lower() in ("true", "1", "yes", "on")

if LOAD_FROM_ENV:
    logger.info("LOAD_FROM_ENV is set. Skipping .env file loading, using existing environment variables.")
else:
    # Find the backend directory (parent of src)
    BACKEND_DIR = Path(__file__).parent.parent.absolute()
    ENV_FILE_PATH = BACKEND_DIR / "src" / "settings" / ".env"
    logger.info(f"ENV_FILE_PATH is {ENV_FILE_PATH}, {type(ENV_FILE_PATH)}")
    logger.info(f"BACKEND_DIR is {BACKEND_DIR}, {type(BACKEND_DIR)}")

    # Try alternative location if the first doesn't exist
    if not ENV_FILE_PATH.exists():
        # Try in backend settings
        ENV_FILE_PATH = BACKEND_DIR / "settings" / ".env"
    if not ENV_FILE_PATH.exists():
        # Try in backend settings
        ENV_FILE_PATH = BACKEND_DIR / ".env"

    # Load environment variables once when module is imported
    if ENV_FILE_PATH.exists():
        load_dotenv(ENV_FILE_PATH, override=True)
        logger.info(f"Loaded environment from: {ENV_FILE_PATH}")
    else:
        logger.warning(f"No .env file found at {ENV_FILE_PATH} or {BACKEND_DIR / '.env'}")


# Configuration class with all environment variables
class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///db/sql_app.db")

    # Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "240"))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "43200"))
    PASSWORD_SALT: str = os.getenv("PASSWORD_SALT", "default-salt-change-in-production")

    # Email
    GOOGLE_EMAIL: str = os.getenv("YOUR_GOOGLE_EMAIL", "")
    GOOGLE_EMAIL_APP_PASSWORD: str = os.getenv("YOUR_GOOGLE_EMAIL_APP_PASSWORD", "")

    # File storage
    MQ_SAVE_DIR: str = os.getenv("MQ_SAVE_DIR", "/tmp/data")

    # RabbitMQ settings
    MQ_HOST_NAME: str = os.getenv("MQ_HOST_NAME", "localhost")
    MQ_PORT: int = int(os.getenv("MQ_PORT", "5672"))
    MQ_VIRTUAL_HOST: str = os.getenv("MQ_VIRTUAL_HOST", "/")
    MQ_USER_NAME: str = os.getenv("MQ_USER_NAME", "guest")
    MQ_PASSWORD: str = os.getenv("MQ_PASSWORD", "guest")
    MQ_QUEUE_NAME: str = os.getenv("MQ_QUEUE_NAME", "terean_queue")

    # Download URL
    DOWNLOAD_BASE_URL: str = os.getenv("DOWNLOAD_BASE_URL", "http://localhost:8000")

    # Initial users
    INITIAL_USERS: str = os.getenv("INITIAL_USERS", "[]")
    
    # Backend username, password and url for the 1d_consumer
    BACKEND_URL: str = os.environ.get("BACKEND_URL")
    BACKEND_USERNAME: str = os.environ.get("BACKEND_USERNAME")
    BACKEND_PASSWORD: str = os.environ.get("BACKEND_PASSWORD")

    # Other settings can be added here...


# Create a single instance
settings = Settings()

# Export for convenience
__all__ = ["settings", "Settings"]
