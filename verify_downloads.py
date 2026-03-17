import requests
import sys

BASE_URL = "http://localhost:5000"

def test_download(report_type, expected_content_type):
    print(f"Testing download for: {report_type}...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/reports/download/{report_type}")
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if expected_content_type in content_type:
                print(f"[PASS] Success: Got {content_type}")
                print(f"Preview: {response.text[:100]}...")
            else:
                print(f"[FAIL] Failed: Expected {expected_content_type}, got {content_type}")
        else:
            print(f"[FAIL] Failed: Status Code {response.status_code}")
            # print(response.text) # Reduce noise
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    print("-" * 30)

if __name__ == "__main__":
    test_download("monthly_summary", "text/plain")
    test_download("officer_performance", "text/csv")
    test_download("all_crimes", "text/csv")
