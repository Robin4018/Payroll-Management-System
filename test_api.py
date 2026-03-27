import requests
url = "http://127.0.0.1:8000/api/payroll/consolidated-report/?month=2026-02&type=monthly"
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQwMDYwNTA3LCJpYXQiOjE3NDAwNTY5MDcsImp0aSI6Ijk2NDBiNTk2MWI0YTREMTZiNmRjMGEwODRiMGUxMzUyIiwidXNlcl9pZCI6MX0.32pXg3C2k6xKCKUGOZKaxQQwB3YoVS7PiyWb6a1Bf3"}
res = requests.get(url, headers=headers)
print("Status:", res.status_code)
print("Body:", res.text)
