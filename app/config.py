import os
from pathlib import Path
from dotenv import load_dotenv

# Project root is fodler with .env file
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Load dev: load .env if it exists
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")