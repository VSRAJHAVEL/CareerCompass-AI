import requests
import json

payload = {
    "model": "qwen3-vl:8b",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant. Please summarize the following resume."},
        {"role": "user", "content": "I am a python developer.\n" * 500}
    ],
    "stream": False,
    "options": {
        "num_predict": 1024,
        "num_ctx": 8192
    }
}

try:
    resp = requests.post("http://localhost:11434/api/chat", json=payload)
    print("Status:", resp.status_code)
    print("Response:", resp.text)
except Exception as e:
    print("Error:", e)
