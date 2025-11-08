# backend/app/llm_router.py
import requests
from .config import LLM_PROVIDER, LLM_BASE_URL, LLM_MODEL, LLM_API_KEY, OLLAMA_BASE_URL

def llama_generate(prompt: str) -> str:
    """
    Unified function to call LM Studio / Ollama / OpenRouter.
    """

    # LM Studio or OpenAI-compatible
    if LLM_PROVIDER == "OPENAI_COMP":
        url = f"{LLM_BASE_URL}/chat/completions"
        headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": LLM_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    # Ollama (if you ever switch)
    if LLM_PROVIDER == "OLLAMA":
        url = f"{OLLAMA_BASE_URL}/api/generate"
        payload = {"model": LLM_MODEL, "prompt": prompt, "stream": False}
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        return r.json().get("response", "")

    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")
