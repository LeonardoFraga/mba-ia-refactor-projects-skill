"""Application configuration.

All secrets and environment-specific values are read from environment
variables. Nothing sensitive is hardcoded in source.
"""
import os


def _as_bool(value: str) -> bool:
    return str(value).strip().lower() in ("1", "true", "yes", "on")


# Never commit a real secret. The fallback is a dev-only placeholder.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

# Debug is OFF by default; enable it explicitly per environment.
DEBUG = _as_bool(os.getenv("FLASK_DEBUG", "false"))

# SQLite database file (relative to the process working directory).
DB_PATH = os.getenv("DB_PATH", "loja.db")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))
