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

### specific calls 

### These calls assume you have correctly specified paths in your .env file. 

OUTPUT_DIRECTORY = get_env_path("OUTPUT_DIRECTORY")

DB_PATH = get_env_path("DB_PATH")

TEST_DB_PATH = get_env_path("TEST_DB_PATH")
TEST_FILE = get_env_path("TEST_FILE")

FILE_DIRECTORY_ROOT = get_env_path("FILE_DIRECTORY_ROOT")
PROJECT_ROOT = get_env_path("PROJECT_ROOT")
LINKING_ID_PEPPER = get_env("LINKING_ID_PEPPER")