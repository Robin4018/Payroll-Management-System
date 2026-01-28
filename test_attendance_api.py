import requests
import json
import os
import django
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_attendance_api():
    # 1. Login
    login_url = f"{BASE_URL}/api/token/"
    try:
        resp = requests.post(login_url, data={"username": "admin", "password": "password123"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            return
        
        token = resp.json().get('access')
        print("Logged in successfully.")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # 2. Check Leave Types
        lt_url = f"{BASE_URL}/api/leave-types/"
        resp = requests.get(lt_url, headers=headers)
        print(f"Leave Types API: {resp.status_code}")
        
        data = resp.json()
        if not data:
            print("No Leave Types found. Seeding now...")
            # Seed Leave Types via API (or script)
            types = ['CL', 'SL', 'EL']
            for t in types:
                requests.post(lt_url, headers=headers, json={
                    "name": t, "max_days_allowed": 12, "tenant": 1 # Assuming tenant 1
                })
            print("Seeded Leave Types.")
        else:
            print(f"Found {len(data)} leave types.")

        # 3. Check Attendance API
        att_url = f"{BASE_URL}/api/attendance/"
        resp = requests.get(att_url, headers=headers)
        print(f"Attendance API: {resp.status_code}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_attendance_api()
