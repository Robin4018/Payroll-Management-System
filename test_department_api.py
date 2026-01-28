import requests
import json
import os
import django
import sys

# We need to setup Django to access models directly if we want to bypass auth for token generation, 
# OR we can just try to hit it without auth if it's AllowAny, OR we can generate a user token.

# Let's try to use valid credentials.
BASE_URL = "http://127.0.0.1:8000"

def test_create_department():
    # 1. Login to get token
    login_url = f"{BASE_URL}/api/token/"
    # We need a user. 'admin' / 'password123' from create_demo_user.py
    try:
        resp = requests.post(login_url, data={"username": "admin", "password": "password123"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            # Try to register if login fails? Or assume admin exists.
            return
        
        token = resp.json().get('access')
        print(f"Got Access Token: {token[:10]}...")
        
        # 2. Create Department
        dept_url = f"{BASE_URL}/api/employees/departments/"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": "Test Dept API",
            "description": "Created via python script",
            "tenant": 1
        }
        
        resp = requests.post(dept_url, headers=headers, json=payload)
        print(f"Create Department Response: {resp.status_code}")
        print(f"Response Body: {resp.text}")
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_create_department()
