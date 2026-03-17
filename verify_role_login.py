import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/auth/login"

def test_login(description, identifier, password, role, expected_status, expected_message_part):
    print(f"\n--- Testing: {description} ---")
    payload = {
        "username": identifier, 
        "password": password,
        "role": role
    }
    # Handle email if identifier looks like one
    if "@" in identifier:
        payload["email"] = identifier
        del payload["username"]

    try:
        response = requests.post(BASE_URL, json=payload)
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
    
    # 1. Test Admin Login as Admin (Should Succeed)
    test_login(
        "Admin Login as Admin", 
        "102", "ayushi shah", "admin",
        200, "success"
    )

    # 2. Test Admin Login as Officer (Should Fail)
    test_login(
        "Admin Login as Officer", 
        "102", "ayushi shah", "officer",
        403, "Access Denied"
    )

    # 3. Test Officer Login as Officer (Should Succeed)
    test_login(
        "Officer Login as Officer", 
        "103", "ayushi shah", "officer",
        200, "success"
    )

    # 4. Test Officer Login as Admin (Should Fail)
    test_login(
        "Officer Login as Admin", 
        "103", "ayushi shah", "admin",
        403, "Access Denied"
    )
