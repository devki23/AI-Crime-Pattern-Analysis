import requests
import time
import random

BASE_URL = "http://127.0.0.1:5000"

def test_username_login():
    # 1. Register a new user with a specific username/officer_id
    username = f"OFFICER-{random.randint(1000, 9999)}"
    email = f"officer{random.randint(1000,9999)}@test.com"
    password = "password123"
    
    print(f"Testing Registration for {username}...")
    register_payload = {
        "username": username,
        "email": email,
        "password": password,
        "role": "police",
        "full_name": "Test Officer",
        "badge": username # Frontend sends badge/id as username usually, or separate? verification needed.
        # In register.html: username: officerId. AND app.py extracts 'badge' independently.
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json=register_payload)
        print(f"Register Status: {resp.status_code}")
        print(f"Register Response: {resp.text}")
        
        if resp.status_code != 201:
            print("Registration failed, cannot proceed.")
            return

        # 2. Login using USERNAME
        print(f"\nTesting Login with USERNAME: {username}")
        # Frontend sends { email: identifier, password: ... }
        login_payload_username = {
            "email": username, 
            "password": password
        }
        resp = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload_username)
        print(f"Login (Username) Status: {resp.status_code}")
        if resp.status_code == 200:
            print("SUCCESS: Logged in with Username")
        else:
            print(f"FAILURE: Could not login with Username. Resp: {resp.text}")

        # 3. Login using EMAIL (Backward compatibility check)
        print(f"\nTesting Login with EMAIL: {email}")
        login_payload_email = {
            "email": email, 
            "password": password
        }
        resp = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload_email)
        print(f"Login (Email) Status: {resp.status_code}")
        if resp.status_code == 200:
            print("SUCCESS: Logged in with Email")
        else:
            print(f"FAILURE: Could not login with Email. Resp: {resp.text}")

    except Exception as e:
        print(f"Exception during test: {e}")

if __name__ == "__main__":
    test_username_login()
