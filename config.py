import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "180"))
DB_PATH = os.getenv("GHOST_DB", "instance/ghost.db")
MAX_INPUT = 8000
HISTORY_TURNS = 10
