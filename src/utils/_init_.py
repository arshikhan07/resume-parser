# app/utils.py
import os
from dotenv import load_dotenv

load_dotenv()  # load .env if present


def get_env_var(key: str, default=None):
    return os.getenv(key, default)