
import requests
import json

url = "http://localhost:8000/auth/register"
payload = {
    "email": "debug_test2@test.com",
    "password": "password123",
    "name": "Debug User 2",
    "role": "student"
}

try:
    print(f"Sending POST to {url}...")
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)
except Exception as e:
    print(f"Request failed: {e}")
