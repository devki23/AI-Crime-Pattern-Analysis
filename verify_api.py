import requests
import json

try:
    print("Fetching users from API...")
    response = requests.get('http://127.0.0.1:5000/api/admin/users')
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        print("Response JSON:")
        print(json.dumps(data, indent=2))
        
        if 'users' in data and data['users']:
            print(f"\nSUCCESS: Found {len(data['users'])} users.")
        else:
            print("\nWARNING: No users found in response (or 'users' key missing).")
            
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print("Raw Text:", response.text)

except Exception as e:
    print(f"Connection Error: {e}")
    print("Is the server running?")
