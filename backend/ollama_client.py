"""
Ollama API client — handles chat completions with streaming support.
"""

import requests
import json
from typing import Generator

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "qwen3-vl:8b"


def check_ollama_health() -> bool:
    """Check if Ollama is running and the model is available."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code != 200:
            return False
        models = [m["name"] for m in resp.json().get("models", [])]
        return any(MODEL_NAME.split(":")[0] in m for m in models)
    except Exception:
        return False


def chat_stream(
    messages: list[dict],
    system_prompt: str,
) -> Generator[str, None, None]:
    """
    Stream a chat response from Ollama token by token.
    Yields text chunks as they arrive.
    """
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "stream": True,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 1024,
            "num_ctx": 8192,
        },
    }

    try:
        with requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            stream=True,
            timeout=120,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
    except requests.exceptions.ConnectionError:
        yield "\n\n⚠️ **Error:** Could not connect to Ollama. Please make sure Ollama is running (`ollama serve`)."
    except requests.exceptions.Timeout:
        yield "\n\n⚠️ **Error:** Request timed out. The model may be loading — please try again."
    except Exception as e:
        yield f"\n\n⚠️ **Error:** {str(e)}"
