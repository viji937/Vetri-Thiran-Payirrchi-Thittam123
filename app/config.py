import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "FitBuddy")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_DIR / 'fitbuddy.db'}")

# Current Gemini API model names. These can be changed in .env without editing code.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_PLAN_MODEL = os.getenv("GEMINI_PLAN_MODEL", "gemini-3.8-flash").strip()
GEMINI_TIP_MODEL = os.getenv("GEMINI_TIP_MODEL", "gemini-3.8-flash-lite").strip()

# Demo mode lets the UI and tests run without a Gemini key.
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Simple admin protection for this local/demo project.
ADMIN_KEY = os.getenv("ADMIN_KEY", "change-me").strip()
