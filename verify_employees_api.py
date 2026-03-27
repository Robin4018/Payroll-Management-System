import requests
import sys

def check_api():
    url = 'http://127.0.0.1:8000/api/employees/'
    try:
        # Try without auth first (if public)
        print(f"GET {url} ...")
        r = requests.get(url)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Type of response: {type(data)}")
            if isinstance(data, list):
                print(f"Count: {len(data)}")
                if len(data) > 0:
                    print(f"First item keys: {data[0].keys()}")
            elif isinstance(data, dict):
                 print(f"Keys: {data.keys()}")
                 if 'results' in data:
                     print(f"Results Count: {len(data['results'])}")
        else:
            print(f"Error Content: {r.text[:500]}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_api()
