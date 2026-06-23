# AI Customer Support Agent (System Layer)

A production-ready, AI-powered customer support backend built for a digital marketing agency. This project ingests a localized FAQ dataset and uses a strict prompt architecture to provide fast, reliable, and hallucination-free support via the Groq LPU inference engine.

**Designed by:**
- **Mayank Jindal**

## 🚀 Features

- **Blazing Fast Inference:** Powered by Groq and the `llama-3.3-70b-versatile` model for near-instant latency.
- **Intelligent Lead Capture:** Native LLM Tool Calling autonomously intercepts provided contact details (name, phone, query) and stores them cleanly using internal backend triggers.
- **RESTful Endpoints:** `GET /leads` and `GET /analytics` endpoints mathematically aggregate runtime API logs off the disk to provide live dashboards.
- **Microservice Architecture:** Clean separation of concerns (`config`, `loader`, `prompt builder`, `llm_service`, `db`, `logger`, `api`).
- **Zero-Hallucination Guardrails:** Implements a 4-level defense system (Input limits, System Prompting, Hyperparameter tuning, and Post-LLM Sanity Checks) to ensure the AI never invents services or breaks character.
- **Resilient Network Handling:** Built-in exponential backoff retries and strict timeouts to gracefully handle transient API provider drops without throwing 500 errors.
- **Full Context Injection:** Bypasses basic RAG implementations in favor of caching and injecting the full localized JSON knowledge base, ensuring zero "retrieval misses."
- **Interaction Tracking:** Structured JSONL logging of all queries, responses, and API latencies natively integrated via `logger_service`.

## 🛠 Tech Stack
- **Framework:** FastAPI (Python)
- **LLM Provider:** Groq API
- **Model:** `llama-3.3-70b-versatile`
- **Validation:** Pydantic

## ⚙️ Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mayankjndl/customer-support-agent-v2.git
   cd customer-support-agent-v2
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the Server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. **Test the API:**
   Navigate to `http://127.0.0.1:8000/docs` to use the interactive Swagger UI, or run a test query:
   ```bash
   curl -X POST http://127.0.0.1:8000/chat \
   -H "Content-Type: application/json" \
   -d "{\"message\": \"Do you offer SEO services?\"}"
   ```
