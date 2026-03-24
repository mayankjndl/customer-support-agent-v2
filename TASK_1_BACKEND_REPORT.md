# Task 1: System Integration & Backend Architecture Report
**Prepared by:** Mayank Jindal  
**Role:** Backend & LLM Integration Engineer (System Layer)

Hi,

Here is my engineering report for Task 1. While Anohita did a great job defining the "brain" of the agent—creating the FAQ dataset, testing the prompts, and designing the response behavior—my goal was to build a strong, reliable, and production-ready system to house that intelligence. 

I didn't just want to write a basic script that "works." I wanted to design a backend that handles errors gracefully, responds instantly, and strictly follows the rules we set so the AI doesn't hallucinate or break character. 

Here is a breakdown of what I built and the technical decisions behind it.

---

## 1. Tech Stack & Architecture choices
- **Framework:** FastAPI (Python)
- **LLM Provider:** Groq
- **Model:** `llama-3.3-70b-versatile`

**Why this stack?**
I chose FastAPI because it’s incredibly fast, handles async requests perfectly (which is crucial when waiting on external LLM calls), and automatically builds our API documentation. 

For the LLM, I integrated Groq instead of OpenAI. Live customer support needs to feel instant; Groq’s LPU inference engines provide response times that are noticeably faster for the end-user. I paired this with `llama-3.3-70b-versatile`, passing a low temperature of `0.3` to keep the model focused, consistent, and less prone to "creative" hallucinations.

---

## 2. Moving Beyond a Single Script: Modular Design
Instead of putting everything into one massive `app.py` file, I structured the codebase like a real microservice. Every file has one specific job:

- **`config.py`**: Holds all our core settings (timeouts, API keys, token limits) in one place so we don't have "magic numbers" hidden randomly in the code.
- **`faq_loader.py`**: Reads Anohita's FAQ file. **Crucially, I added caching here.** It only reads the file once when the server starts, rather than wasting memory and time reading from the disk every single time a user sends a message.
- **`prompt_builder.py`**: Cleanly merges the system instructions, the FAQ context, and the user's actual question into the exact format the LLM needs.
- **`llm_service.py`**: Dedicated entirely to talking to Groq—managing the actual network request, retries, and output validation.
- **`main.py`**: The traffic cop. It just receives the HTTP request, validates the input using Pydantic, and coordinates the other modules.

By separating the code this way, if we ever want to swap Groq for OpenAI, or change how we load the FAQs (like from a database instead of a text file), we only have to change one specific file without breaking the rest of the app.

---

## 3. Core System Decisions: "The Why"

### A. Full Context Injection vs. RAG (Vector Search)
We currently have 30 FAQ pairs (roughly 2KB of text). At this scale, building a complex Retrieval-Augmented Generation (RAG) system with embeddings is overkill and actually introduces risk (e.g., the search algorithm failing to retrieve the right question). 

**My decision:** I built the system to inject the *entire* 30-item dataset into the LLM’s context on every single query. This guarantees the AI has 100% perfect knowledge of our services every time, making it much more reliable. (If our FAQ grows to 100+ items later, the modular design makes it very easy to swap this out for a RAG system).

### B. The 4-Level Defense Against Hallucinations
The biggest risk with LLMs in customer support is the bot making things up, or "breaking character" and acting like a robotic language model. I built four layers of defense to stop this:

1. **Input Guardrails:** The `/chat` endpoint automatically rejects any user message longer than 500 characters. This stops bad actors from trying complex "prompt injection" attacks.
2. **Prompt-Level Rules:** The system prompt explicitly commands the AI to *only* use the provided context and instructs it on exactly how to sound unsure if the answer isn't there.
3. **Configuration Guardrails:** As mentioned, the low temperature (`0.3`) keeps the AI grounded, and a hard cap of `300` max tokens ensures the bot doesn't go on a rambling tangent.
4. **Post-LLM Sanity Check (The Safety Net):** I wrote a custom check that runs *after* the LLM generates a response, but *before* we send it back to the user. If the response is suspiciously short, oddly long, or contains phrases like *"As an AI..."*, the system catches it and replaces it with a safe, human-sounding fallback message.

### C. System Resilience (Handling Failures Gracefully)
External APIs drop connections. To make sure our customer support agent doesn't just crash when that happens:
- **Exponential Backoff:** If the Groq API times out, my code automatically catches the error and tries again up to 2 times, pausing briefly between attempts.
- **Strict Timeouts:** I capped network calls at 10 seconds. We never want a user staring at a loading screen forever.
- **Masked Errors:** If a permanent error happens (like an invalid API key), the system logs the full detailed error securely on our server, but returns a clean, friendly 500 error to the user: *"Something went wrong. Please try again in a moment."*

---

## 4. Final Testing Results
I ran the live system against the 7 core edge cases Anohita identified (normal matches, partial matches, out-of-scope questions like the weather, ambiguous questions, and frustrated users). 

The system scored a 100% pass rate. It successfully adhered to the 3-part response structure she designed (Direct Answer → Explanation → Next Step) and routed out-of-scope questions cleanly to the human fallback.

I've pushed the code and detailed the setup instructions in the `walkthrough.md` file in the root directory. Let me know if you have any questions!
