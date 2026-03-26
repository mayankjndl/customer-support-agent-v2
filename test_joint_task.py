import json
import urllib.request
import urllib.error
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
            data_bytes = json.dumps({"message": query}).encode('utf-8')
            req = urllib.request.Request(API_URL, data=data_bytes, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req, timeout=30.0) as response:
                status_code = response.getcode()
                response_body = response.read().decode('utf-8')
                reply_data = json.loads(response_body)
                actual = reply_data.get("reply", "No reply found")
                
            latency = round((time.time() - start_time) * 1000)
            
            print(f"Actual:    {actual}")
            print(f"Latency:   {latency}ms\n")
            
        except urllib.error.HTTPError as e:
            try:
                error_body = e.read().decode('utf-8')
                actual = f"HTTP Error {e.code}: {error_body}"
            except:
                actual = f"HTTP Error {e.code}"
            print(f"Actual:    {actual}")
            print(f"Latency:   N/A\n")
        except urllib.error.URLError as e:
            print(f"Actual:    Request failed: {e.reason}")
            print(f"Latency:   N/A\n")
        except Exception as e:
            print(f"Actual:    Request failed: {e}")
            print(f"Latency:   N/A\n")

if __name__ == "__main__":
    run_tests()
