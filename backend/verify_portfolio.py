import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"
EMAIL = "test_portfolio@example.com"
PASSWORD = "TestPassword123!"

def print_result(step, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {step}")
    if not success and details:
        print(f"   Details: {details}")
    if not success:
        sys.exit(1)

def main():
    print("Starting Portfolio API Verification...")
    
    # 1. Register/Login
    session = requests.Session()
    
    # Try login first
    print(f"\n1. Authenticating as {EMAIL}...")
    auth_resp = session.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    
    token = None
    if auth_resp.status_code == 200:
        token = auth_resp.json()["access_token"]
        print_result("Login existing user", True)
    elif auth_resp.status_code == 401:
        # Register if not exists
        print("   User not found, registering...")
        reg_resp = session.post(f"{BASE_URL}/auth/register", json={"email": EMAIL, "password": PASSWORD, "name": "Test User"})
        if reg_resp.status_code == 201:
            token = reg_resp.json()["access_token"]
            print_result("Register new user", True)
        else:
            print_result("Register user", False, reg_resp.text)
    else:
        print_result(f"Login failed ({auth_resp.status_code})", False, auth_resp.text)

    # Set Auth Header
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Add Holding
    print("\n2. Adding Bitcoin holding...")
    add_data = {
        "coin_id": "bitcoin",
        "amount": 0.5,
        "buy_price": 45000.0
    }
    
    # Check if exists first and delete to clean state
    # But delete relies on verification, so let's just add/update
    
    add_resp = session.post(f"{BASE_URL}/portfolio", json=add_data, headers=headers)
    if add_resp.status_code in [200, 201]:
        print_result("Add Bitcoin", True, str(add_resp.json()))
    else:
        print_result("Add Bitcoin", False, add_resp.text)
        
    # 3. Get Portfolio
    print("\n3. Fetching portfolio...")
    get_resp = session.get(f"{BASE_URL}/portfolio", headers=headers)
    if get_resp.status_code == 200:
        holdings = get_resp.json()
        btc = next((h for h in holdings if h["coin_id"] == "bitcoin"), None)
        if btc and btc["amount"] == 0.5:
            print_result("Get Portfolio (Verify BTC amount)", True)
        else:
            print_result("Get Portfolio", False, f"BTC not found or incorrect amount: {btc}")
    else:
        print_result("Get Portfolio", False, get_resp.text)

    # 4. Update Holding
    print("\n4. Updating Bitcoin holding...")
    update_data = {
        "amount": 1.0,
        "buy_price": 46000.0
    }
    put_resp = session.put(f"{BASE_URL}/portfolio/bitcoin", json=update_data, headers=headers)
    if put_resp.status_code == 200:
        updated = put_resp.json()
        if updated["amount"] == 1.0:
            print_result("Update Bitcoin", True)
        else:
            print_result("Update Bitcoin", False, f"Amount not updated: {updated}")
    else:
        print_result("Update Bitcoin", False, put_resp.text)

    # 5. Get Summary
    print("\n5. Checking Summary...")
    sum_resp = session.get(f"{BASE_URL}/portfolio/summary", headers=headers)
    if sum_resp.status_code == 200:
        summary = sum_resp.json()
        if summary["holdings_count"] >= 1:
            print_result("Get Summary", True, str(summary))
        else:
            print_result("Get Summary", False, "Count is 0")
    else:
        print_result("Get Summary", False, sum_resp.text)

    # 6. Delete Holding
    print("\n6. Deleting Bitcoin holding...")
    del_resp = session.delete(f"{BASE_URL}/portfolio/bitcoin", headers=headers)
    if del_resp.status_code == 204:
        print_result("Delete Bitcoin", True)
    else:
        print_result("Delete Bitcoin", False, del_resp.text)

    # Final Check
    print("\n7. Verifying deletion...")
    final_resp = session.get(f"{BASE_URL}/portfolio", headers=headers)
    holdings = final_resp.json()
    btc = next((h for h in holdings if h["coin_id"] == "bitcoin"), None)
    if not btc:
        print_result("Verify Deletion", True)
    else:
        print_result("Verify Deletion", False, "BTC still exists")

    print("\n✅ All backend portfolio tests passed!")

if __name__ == "__main__":
    main()
