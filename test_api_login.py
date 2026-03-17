import requests

url = 'http://127.0.0.1:5000/api/auth/login'
payload = {
    'username': '103',
    'password': 'Police103',
    'role': 'officer'
}

try:
    response = requests.post(url, json=payload)
    print(response.status_code)
    print(response.json())
except Exception as e:
    print(e)
