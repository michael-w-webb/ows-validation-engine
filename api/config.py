# config.py
from pathlib import Path
import os
from dotenv import load_dotenv

### This file creates a single origin for critical path calls, to avoid repeated relative location specifications. 

# Always resolve relative to THIS file (project root)
BASE_DIR = Path(__file__).resolve().parent

# Load .env once
load_dotenv(BASE_DIR / ".env")

### basic loading mechanism 

def get_env(var_name: str, required: bool = True) -> str:
    value = os.getenv(var_name)
    if required and not value:
        raise ValueError(f"Missing environment variable: {var_name}")
    return value

def get_env_path(var_name: str) -> Path:
    return Path(get_env(var_name))

WB_DEF_DB_PATH = get_env_path("WB_DEF_DB_PATH")
API_BASE_DIR = get_env_path("API_BASE_DIR")
LOCAL_OUTPUT_DIRECTORY = get_env_path("LOCAL_OUTPUT_DIRECTORY")