import requests
import json
import sys

payload = {
    "message": "Help me write a strong resume for a software engineering role.\n\n--- ATTACHED RESUME ---\nRajhavel is a software engineer with 3 years of experience. Python, Java, React.\n-----------------------\n",
    "session_id": "test_session_123"
}

try:
    with requests.post("http://localhost:8000/chat", json=payload, stream=True) as r:
        if r.status_code != 200:
            print("Error", r.status_code, r.text)
            sys.exit(1)
        for line in r.iter_lines():
            if line:
                print(line.decode('utf-8'))
except Exception as e:
    print("Exception:", e)
