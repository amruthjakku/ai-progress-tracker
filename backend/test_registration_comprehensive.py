
import requests
import json
import random
import string
import sys

BASE_URL = "http://localhost:8000"

def generate_email():
    return f"test_{''.join(random.choices(string.ascii_lowercase, k=8))}@example.com"

def run_test(name, password, expected_status=201):
    email = generate_email()
    print(f"\n--- Testing: {name} ---")
    print(f"Email: {email}")
    print(f"Password length: {len(password)}")
    
    # Register
    print("1. Registering...")
    payload = {
        "email": email,
        "password": password,
        "name": f"Test User {name}",
        "role": "student"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != expected_status:
            print(f"   ❌ FAILED: Expceted {expected_status}, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
        print("   ✅ Registration Success")
        if expected_status != 201:
            return True # Successfully failed as expected
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return False

    # Login
    print("2. Logging in...")
    login_payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"   ✅ Login Success. Token: {token[:20]}...")
            return True
        else:
            print(f"   ❌ FAILED: Login failed with {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return False

def main():
    print(f"Targeting Backend at: {BASE_URL}")
    print("Running comprehensive registration tests...")
    
    results = []
    
    # Test 1: Normal password
    results.append(run_test("Normal Password", "password123"))
    
    # Test 2: Long password (72 chars - boundary)
    results.append(run_test("Boundary Password (72 chars)", "a" * 72))
    
    # Test 3: Very long password (> 72 chars) - This was failing
    results.append(run_test("Long Password (100 chars)", "b" * 100))
    
    # Test 4: Extremely long password
    results.append(run_test("Massive Password (1000 chars)", "c" * 1000))

    print("\n" + "="*30)
    if all(results):
        print("✅ ALL TESTS PASSED! The fix is robust.")
    else:
        print("❌ SOME TESTS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
