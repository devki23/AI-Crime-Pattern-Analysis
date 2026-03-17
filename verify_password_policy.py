import requests
import json
import random
import time

BASE_URL = "http://127.0.0.1:5000/api/auth/register"

def generate_user():
    rnd = random.randint(1000, 9999)
    return {
        "full_name": f"Test User {rnd}",
        "email": f"test{rnd}@example.com",
        "role": "officer",
        "phone": "1234567890",
        "station": "Test Station",
        "username": f"TEST-{rnd}",
        "badge": f"BADGE-{rnd}"
    }

def test_registration(description, password, expected_status, expected_message_part):
    print(f"\n--- Testing: {description} ---")
    data = generate_user()
    data["password"] = password
    
    try:
        response = requests.post(BASE_URL, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == expected_status:
            if expected_message_part in response.text:
                print("PASSED")
            else:
                print(f"FAILED: Message mismatch. Expected '{expected_message_part}'")
        else:
            print(f"FAILED: Status mismatch. Expected {expected_status}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    print("Waiting for server to be ready...")
    # Assuming server is running. If not, this script will fail connection.
    
    # 1. Test Short Password
    test_registration(
        "Short Password (7 chars)", 
        "Abcdef1", 
        400, 
        "Password must be at least 8 characters long"
    )

    # 2. Test Lowercase Start
    test_registration(
        "Lowercase Start", 
        "abcdefg123", 
        400, 
        "Password must start with a capital letter"
    )

    # 3. Test Valid Password
    test_registration(
        "Valid Password", 
        "Abcdefg123", 
        201, 
        "User registered successfully"
    )
