import requests
import json

base_url = 'http://127.0.0.1:8000/api'

# 1. Login
try:
    auth_resp = requests.post(f'{base_url}/token/', json={'username': 'admin', 'password': 'password123'})
    print(f"Login Status: {auth_resp.status_code}")
    if auth_resp.status_code != 200:
        print("Login Failed:", auth_resp.text)
        exit()
    
    tokens = auth_resp.json()
    access_token = tokens['access']
    print("Got Access Token")
except Exception as e:
    print(f"Connection Error: {e}")
    exit()

# 2. Run Payroll
try:
    headers = {'Authorization': f'Bearer {access_token}'}
    # Payload matching the UI
    payload = {'tenant_id': 1, 'month': '2026-01-15'}
    
    print("\nSending Payload:", payload)
    resp = requests.post(f'{base_url}/payroll/run/', json=payload, headers=headers)
    
    print(f"Payroll Status: {resp.status_code}")
    print("Response Body:")
    print(resp.text)
except Exception as e:
    print(f"Request Error: {e}")
