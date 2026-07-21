"""Global configuration for Experimental-Research-OpenClaw backend."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file
load_dotenv(override=True)

# --- Path constants ---
BASE_DIR = Path(__file__).resolve().parent
OPENCLAW_DIR = BASE_DIR / ".openclaw"
WORKSPACE_TEMPLATES_DIR = BASE_DIR / "workspace-templates"
DEFAULT_WORKSPACE_DIR = OPENCLAW_DIR / "workspace-default"
SKILLS_DIR = BASE_DIR / "skills"
CONFIG_JSON_PATH = BASE_DIR / "config.json"

PLACEHOLDER_API_KEYS = {
    "",
    "your_key",
    "your_api_key",
    "sk-xxx",
    "sk-your-key",
    "replace_me",
}

# --- LLM configuration ---
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- Embedding configuration (Phase 5, RAG) ---
EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY", "")
EMBEDDING_BASE_URL: str = os.getenv("EMBEDDING_BASE_URL", "")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

# --- Optional API keys ---
BRAVE_API_KEY: str = os.getenv("BRAVE_API_KEY", "")

# --- Server ---
DEFAULT_AGENT_ID = "default"


def has_valid_openai_api_key() -> bool:
    """Return True only when OPENAI_API_KEY looks like a real configured value."""
    return OPENAI_API_KEY.strip() not in PLACEHOLDER_API_KEYS


def openai_api_key_error() -> str:
    """Return a user-facing configuration error for invalid/missing API keys."""
    key = OPENAI_API_KEY.strip()
    if key in PLACEHOLDER_API_KEYS:
        return (
            "OPENAI_API_KEY is missing or still using a placeholder value in backend/.env. "
            "Set a real provider key, and make sure OPENAI_BASE_URL matches the same provider."
        )
    return ""


def load_config() -> dict:
    """Load persistent config from config.json. Returns empty dict if not found."""
    if CONFIG_JSON_PATH.exists():
        with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"rag_mode": False}


def save_config(config: dict) -> None:
    """Save persistent config to config.json."""
    with open(CONFIG_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

