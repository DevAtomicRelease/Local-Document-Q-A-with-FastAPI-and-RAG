# backend/app/config.py
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent 
ENV_PATH = BACKEND_DIR / ".env"

load_dotenv(dotenv_path=str(ENV_PATH))

def _abs_path(val: str | None, default_rel: str) -> str:
    if val and os.path.isabs(val):
        return val
    base = BACKEND_DIR / (val or default_rel)
    return str(base.resolve())


EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-m3")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "OPENAI_COMP")  
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama-3.1-8b-instruct-hf")
LLM_API_KEY  = os.getenv("LLM_API_KEY", "lm-studio") 
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

CHROMA_DIR = _abs_path(os.getenv("CHROMA_DIR"), "chroma_db")
DOCS_DIR= _abs_path(os.getenv("DOCS_DIR"), "documents")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
TOP_K = int(os.getenv("TOP_K", 5))

Path(CHROMA_DIR).mkdir(parents=True, exist_ok=True)
Path(DOCS_DIR).mkdir(parents=True, exist_ok=True)
