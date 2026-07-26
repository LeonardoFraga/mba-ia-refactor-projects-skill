"""Centralized configuration — all secrets/settings come from the environment.

Nothing sensitive is hardcoded. Values are read from environment variables
(optionally loaded from a local .env file via python-dotenv), with dev-only
fallbacks so the app still boots out of the box.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # python-dotenv not installed — env vars still work
    pass


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


# --- Flask / app ---
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-change-me')
DEBUG = _as_bool(os.getenv('FLASK_DEBUG'), default=False)
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '5000'))

# --- Database ---
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///tasks.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# --- Password hashing ---
# pbkdf2:sha256 is portable across platforms (scrypt can be unavailable).
PASSWORD_HASH_METHOD = os.getenv('PASSWORD_HASH_METHOD', 'pbkdf2:sha256')

# --- SMTP / notifications ---
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
