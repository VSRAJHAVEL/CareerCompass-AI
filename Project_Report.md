# Project Report: CareerCompass — AI-Powered Job Guidance Chatbot

**Author:** Rajhavel V S

## 1. Introduction
With the rapid evolution of the job market, candidates often struggle to align their resumes and skills with industry expectations. General-purpose Large Language Models (LLMs) can provide generic advice, but they lack mathematical rigor when evaluating a candidate's specific fitness for a role. 

**CareerCompass** is a specialized, AI-powered career counseling platform built specifically to address this gap. It serves as an intelligent Job Guidance Assistant that leverages a hybrid Natural Language Processing (NLP) architecture. By combining classic mathematical NLP techniques (TF-IDF, Cosine Similarity) with modern Generative AI (local LLMs via Ollama), CareerCompass offers highly personalized, data-backed career guidance, resume gap analysis, and interview preparation. 

## 2. Objectives
1. **Mathematical Skill Evaluation:** Automate the gap analysis between a candidate's resume and a target job domain using mathematical vector spaces.
2. **Context-Aware Assistance:** Provide an intelligent chatbot interface that understands professional goals, intent, and career context.
3. **Local, Secure Processing:** Ensure user data privacy by processing all resumes and chat interactions locally using Ollama (`qwen3-vl:8b`).
4. **Premium User Experience:** Deliver the NLP insights through a highly polished, professional "Glassmorphism" user interface.

---

## 3. System Architecture

The project utilizes a modern, decoupled architecture:

- **Frontend (UI Layer):** 
  Built using HTML5, raw CSS3, and Vanilla JavaScript. It features a sophisticated dark-mode "iPhone Glassy" aesthetic. The frontend handles API communication via Server-Sent Events (SSE) to flawlessly stream markdown-rendered LLM responses text token by text token.
- **Backend (API Layer):** 
  A fast, highly concurrent Python backend powered by **FastAPI** and **Uvicorn**. It maintains conversational memory, handles file reading, orchestrates the NLP pipelines, and parses streams from the local LLM.
- **NLP Engine (Analytical Layer):** 
  Powered by `scikit-learn` and Python's `re` module. It performs intent classification, keyword extraction, TF-IDF Vectorization, and Cosine Similarity computations.
- **Generative Engine (Intelligence Layer):** 
  Utilizes the open-weight `qwen3-vl:8b` model running entirely locally on **Ollama**. The LLM is given engineered system prompts enriched dynamically with job market data and the backend's mathematical NLP gap analysis.

---

## 4. NLP Methodology

What distinguishes CareerCompass from a standard LLM wrapper is its implementation of traditional NLP techniques to ground the generative AI's advice in mathematical truth.

### 4.1. Intent and Entity Recognition
When a user submits a query, the system first runs an intent classification pipeline. Using regular expressions and specialized dictionaries (`NLP Utils`), the system parses the user's raw text to extract:
*   **Intent:** Identifying if the user is asking about a *resume*, *interview*, *salary*, *skills*, or *career paths*.
*   **Domain Entities:** Detecting if the user belongs to *Software Engineering*, *Data Science*, *Product Management*, *Design*, etc.
*   **Skill Entities:** Extracting mentioned tools and languages (e.g., Python, AWS, Figma).

This metadata dynamically builds the system prompt for the LLM, effectively directing the model's persona before inference begins.

### 4.2. Mathematical Gap Analysis: TF-IDF and Cosine Similarity
The core analytical feature of CareerCompass is the **Resume Match Engine**. When a user uploads a resume file (`.txt`), the system evaluates it against a canonical "Golden Dataset" of keywords corresponding to their target domain.

1.  **Text Preprocessing:** The resume undergoes tokenization, lowercasing, and removal of non-alphanumeric characters.
2.  **TF-IDF Vectorization:** The system implements `TfidfVectorizer` from `scikit-learn`. It removes English stopwords and transforms both the *canonical domain text* and the *user's resume* into sparse Term Frequency-Inverse Document Frequency matrices. This weighs terms not just by how often they appear in the resume, but how essential they are to the corpus.
3.  **Cosine Similarity:** The system calculates the angle between the canonical document vector and the resume document vector. The `cosine_similarity` function returns a bounded score (0 to 1), mapping exactly how strongly the resume overlaps with the industry benchmark.
4.  **Set Operations:** By extracting the `feature_names_out()` from the matrices, the backend mathematically performs set intersection and set difference to isolate EXACT overlapping skills and crucially missing skills.

### 4.3. Generative Synthesis
The mathematical outputs (The Match Score %, Overlapping Skills, Missing Skills) act as a secondary prompt injection for the LLM. The LLM synthesizes this structured data, turning dry numerical percentages into actionable, human-readable advice on *how* to bridge the identified gaps.

---

## 5. User Interface (UI/UX)

The frontend departs from standard, boring interfaces to implement a premium **Glassmorphism** design:
*   **Frosted Glass Panels:** Background-blurs (`backdrop-filter`) and low-opacity dark surfaces give the appearance of smoked glass over dynamic background orbs.
*   **Typography:** The platform uses luxury fonts — `Cinzel` for authoritative headers and `Montserrat` for clean readability in chat bubbles.
*   **Dynamic Data Visualizations:** The mathematical NLP data (TF-IDF Similarity) is visually rendered via an injected UI card. A circular SVG stroke dynamically animates to represent the match percentage, visually reinforcing the backend calculations before the AI even begins to stream its advice.
*   **Streaming Responses:** Text arrives iteratively via SSE, creating the live-typing effect characteristic of modern AI tools.

---

## 6. Testing & Validation

During testing with mock resumes, the NLP matching engine accurately penalized resumes lacking core domain keywords. For instance, a generic Software Engineering resume missing "AWS" and "Kubernetes" correctly received a lower Cosine Similarity score (~24%), while simultaneously highlighting those precise missing terms in the Gap Analysis tag. The `qwen3-vl:8b` model successfully utilized this metadata to recommend specific cloud computing certifications.

---

## 7. Conclusion & Future Scope

CareerCompass successfully proves that blending classic, statistically-driven NLP techniques (TF-IDF, Cosine Similarity) with modern Generative models yields a vastly superior product than either approach alone. The mathematical model grounds the evaluation in factual keyword analysis, while the LLM provides the nuanced, human-friendly coaching.

**Future Enhancements:**
1.  **PDF/Docx Parsing:** Expanding the resume uploader to scrape multi-format documents using OCR or `PyMuPDF`.
2.  **Live Job Scraping:** Dynamically pulling live job descriptions from LinkedIn to act as the exact canonical TF-IDF comparison document rather than relying on a static dictionary.
3.  **Interview Audio NLP:** Allowing users to record mock interview answers, subsequently running Speech-to-Text inference and performing sentiment analysis on their delivery confidence.
