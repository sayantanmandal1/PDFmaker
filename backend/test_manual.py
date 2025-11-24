"""
Manual test script to test API endpoints one at a time.
"""
import requests
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

print("Testing API endpoints...")

# Test 1: Health check
print("\n1. Testing health check...")
try:
    response = requests.get(f"{API_BASE}/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Invalid login
print("\n2. Testing invalid login...")
try:
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": "invalid@example.com", "password": "wrongpassword"},
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Register user
print("\n3. Testing user registration...")
email = f"test_{int(time.time())}@example.com"
try:
    response = requests.post(
        f"{API_BASE}/auth/register",
        json={"email": email, "password": "password123", "name": "Test User"},
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Login with valid credentials
print("\n4. Testing valid login...")
try:
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": email, "password": "password123"},
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"   Token received: {token[:20]}...")
    else:
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

print("\nManual tests completed.")
