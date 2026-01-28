import requests
import json

BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/token/"
DASHBOARD_URL = f"{BASE_URL}/api/payroll/dashboard/stats/"

USERNAME = "robin"
PASSWORD = "robin 2003"

def verify_api():
    print(f"--- Verifying API: {DASHBOARD_URL} ---")
    
    # 1. Login to get token
    print("Logging in...")
    try:
        resp = requests.post(LOGIN_URL, json={'username': USERNAME, 'password': PASSWORD})
        if resp.status_code != 200:
            print(f"Login Failed: {resp.status_code} - {resp.text}")
            return
        
        token = resp.json().get('access')
        print("Login Successful. Token received.")
        
        # 2. Call Dashboard API with Token
        print("Calling Dashboard API...")
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.get(DASHBOARD_URL, headers=headers)
        
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print("Response Data:")
            print(json.dumps(resp.json(), indent=2))
        else:
            print("Request Failed:")
            print(resp.text)
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    verify_api()
