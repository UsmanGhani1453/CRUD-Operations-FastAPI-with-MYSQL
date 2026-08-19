"""
Centralized application configuration.

All secrets/config are read from environment variables. Load a local .env
file (never committed - see .gitignore) for development via python-dotenv.

In production, required variables MUST be set on the host/platform; this
module fails fast at startup instead of silently falling back to insecure
defaults.
"""
import os
import secrets
import warnings

from dotenv import load_dotenv

load_dotenv()  # no-op if .env doesn't exist (e.g. in production)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"


def _require(name: str, dev_default: str | None = None) -> str:
    """
    Read a required environment variable.

    In production, raises if the variable is missing (fail closed).
    In development, falls back to `dev_default` (if given) with a warning,
    so local setup stays easy without ever shipping a real default secret.
    """
    value = os.getenv(name)
    if value:
        return value

    if IS_PRODUCTION:
        raise RuntimeError(
            f"Missing required environment variable '{name}'. "
            "Set it before starting the app in production."
        )

    if dev_default is not None:
        warnings.warn(
            f"Environment variable '{name}' is not set - using an "
            f"insecure development default. Do NOT do this in production.",
            stacklevel=2,
        )
        return dev_default

    raise RuntimeError(f"Missing required environment variable '{name}'.")


# --- Database ---------------------------------------------------------
DATABASE_URL = _require(
    "DATABASE_URL",
    dev_default="mysql+pymysql://root:password@localhost:3306/my_database",
)

# --- Auth / JWT ---------------------------------------------------------
# Never ship a static fallback secret. In dev, generate a random one per
# process start (still insecure for multi-process setups, but far better
# than a fixed, publicly-known string).
SECRET_KEY = _require("SECRET_KEY", dev_default=secrets.token_hex(32))
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS = int(
    os.getenv("EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS", "24")
)

# --- Email (SMTP) ---------------------------------------------------------
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")

# --- CORS ---------------------------------------------------------
_default_origins = "http://127.0.0.1:5500,http://localhost:5500"
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

# --- Currency ---------------------------------------------------------
CURRENCY = os.getenv("CURRENCY", "usd")
