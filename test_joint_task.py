import json
import httpx
import time
import os

QUERIES_FILE = os.path.join(os.path.dirname(__file__), "data", "updated_queries.json")
API_URL = "http://127.0.0.1:8000/chat"

def run_tests():
    # Load the JSON data
    with open(QUERIES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Loop through each query and post to backend
    for i, item in enumerate(data, 1):
        query = item.get("query", "")
        expected = item.get("response", "")
        
        print(f"--- Test {i} ---")
        print(f"Query:     {query}")
        print(f"Expected:  {expected}")
        
        try:
            start_time = time.time()
            r = httpx.post(API_URL, json={"message": query}, timeout=30.0)
            latency = round((time.time() - start_time) * 1000)
            
            if r.status_code == 200:
                actual = r.json().get("reply", "No reply found")
            else:
                actual = f"HTTP Error {r.status_code}: {r.text}"
                
            print(f"Actual:    {actual}")
            print(f"Latency:   {latency}ms\n")
            
        except httpx.RequestError as e:
            print(f"Actual:    Request failed: {e}")
            print(f"Latency:   N/A\n")

if __name__ == "__main__":
    run_tests()
