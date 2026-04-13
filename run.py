"""
run.py — One-click startup for CareerCompass Job Guidance Chatbot.
Starts the FastAPI server and opens the browser.
"""

import subprocess
import sys
import time
import webbrowser
import requests
from pathlib import Path

PORT = 8000
URL = f"http://localhost:{PORT}"
BACKEND_DIR = Path(__file__).parent / "backend"


def check_ollama():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=4)
        models = [m["name"] for m in r.json().get("models", [])]
        has_model = any("qwen3-vl" in m for m in models)
        if not has_model:
            print("⚠️  qwen3-vl:8b not found in Ollama. Pull it with:")
            print("       ollama pull qwen3-vl:8b")
            print("    Continuing anyway (Ollama may still serve it)...\n")
        else:
            print("✅  Ollama is running with qwen3-vl:8b")
    except Exception:
        print("⚠️  Could not connect to Ollama at localhost:11434")
        print("    Make sure Ollama is running: ollama serve\n")


def wait_for_server():
    print(f"⏳  Waiting for server at {URL} ...")
    for _ in range(30):
        try:
            requests.get(f"{URL}/health", timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


if __name__ == "__main__":
    print("\n🧭  CareerCompass — Job Guidance Chatbot")
    print("=" * 44)

    check_ollama()

    print(f"\n🚀  Starting FastAPI server on port {PORT}...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", f"--port={PORT}", "--reload"],
        cwd=str(BACKEND_DIR),
    )

    if wait_for_server():
        print(f"\n✅  Server ready at {URL}")
        print("🌐  Opening browser...\n")
        webbrowser.open(URL)
        print("    Press Ctrl+C to stop.\n")
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("\n🛑  Shutting down...")
            proc.terminate()
    else:
        print("❌  Server did not start in time. Check errors above.")
        proc.terminate()
        sys.exit(1)
