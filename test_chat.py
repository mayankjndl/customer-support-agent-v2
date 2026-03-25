"""Task 2 verification script to test empty bypass, updated fallbacks, and Hinglish queries."""
import httpx

tests = [
    ("Empty Query Bypass", ""),
    ("Whitespace Query Bypass", "   "),
    ("Updated Fallback (Out of scope)", "What is the weather in Mumbai?"),
    ("Hinglish/Informal Query", "SEO plan ka cost kya hai?"),
]

results = []
for label, query in tests:
    r = httpx.post("http://127.0.0.1:8000/chat", json={"message": query}, timeout=30)
    data = r.json()
    reply = data.get("reply", data.get("detail", "ERROR"))
    results.append(f"--- {label} ---\nQuery: '{query}'\nStatus: {r.status_code}\nReply: {reply}\n")

output = "\n".join(results)
print(output)

with open("test_results_v2.txt", "w", encoding="utf-8") as f:
    f.write(output)
