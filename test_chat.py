"""Quick test script to verify all query types against the live /chat endpoint."""
import httpx

tests = [
    ("Normal - FAQ match", "Do you offer SEO services?"),
    ("Normal - FAQ match", "What services do you offer?"),
    ("Partial match", "SEO?"),
    ("Out of scope", "What is the weather in Mumbai?"),
    ("Unknown service", "Do you provide legal consulting?"),
    ("Ambiguous", "How much does it cost?"),
    ("Frustrated user", "My ads are not working at all"),
]

results = []
for label, query in tests:
    r = httpx.post("http://127.0.0.1:8000/chat", json={"message": query}, timeout=30)
    data = r.json()
    reply = data.get("reply", data.get("detail", "ERROR"))
    results.append(f"--- {label} ---\nQuery: {query}\nStatus: {r.status_code}\nReply: {reply}\n")

output = "\n".join(results)
print(output)

with open("test_results.txt", "w", encoding="utf-8") as f:
    f.write(output)
