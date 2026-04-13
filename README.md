# CareerCompass — AI-Powered Job Guidance Chatbot

**Developed by:** Rajhavel V S

## Description
CareerCompass is an AI-powered career counseling platform built specifically to address the gap in generic AI advice. It serves as an intelligent Job Guidance Assistant that leverages a hybrid Natural Language Processing (NLP) architecture. By combining classic mathematical NLP techniques (TF-IDF, Cosine Similarity) with modern Generative AI (local LLMs via Ollama), CareerCompass offers highly personalized, data-backed career guidance, resume gap analysis, and interview preparation.

## Features
- **Mathematical Skill Evaluation:** Automate the gap analysis between a candidate's resume and a target job domain.
- **Context-Aware Assistance:** Chatbot interface that understands professional goals, intent, and career context.
- **Local & Secure Processing:** Privacy-first processing of resumes and interactions using Ollama running locally.
- **Premium User Experience:** Modern Glassmorphism aesthetic and fast UI.

## Technologies Used
- Frontend: HTML5, CSS3, Vanilla JavaScript
- Backend: Python, FastAPI
- NLP: scikit-learn, TF-IDF Vectorizer
- Generative AI: Ollama (qwen3-vl:8b)

## How to Run
1. Make sure you have Ollama installed and `qwen3-vl:8b` pulled.
2. Install Python dependencies: `pip install -r backend/requirements.txt`
3. Start the application: `python run.py` (which usually starts the backend server and serves the frontend).
