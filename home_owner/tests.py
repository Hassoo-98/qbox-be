"""
Test scripts for Home Owner Module
==================================
This script tests all home owner-related endpoints.

Usage:
    python home_owner/tests.py

Requirements:
    - Django server should be running
"""

import requests
import json
import sys
import uuid

# Configuration
BASE_URL = "http://127.0.0.1:8000"
HOME_OWNER_URL = f"{BASE_URL}/home_owner/"
AUTH_URL = f"{BASE_URL}/auth/"

# Generate unique email for test
def generate_unique_email():
    return f"test.homeowner.{uuid.uuid4().hex[:8]}@example.com"


# Home Owner test data
TEST_HOME_OWNER = {
    "full_name": "Test Home Owner",
    "email": generate_unique_email(),
    "phone_number": "1234567890",
    "password": "testpassword123",
    "secondary_phone_number": "0987654321",
    "installation_location_preference": "Front door",
    "installation_access_instruction": "Ring doorbell",
    "preferred_installment_location": "Living room"
}

TEST_HOME_OWNER_UPDATE = {
    "full_name": "Updated Home Owner Name",
    "phone_number": "1111111111"
}

LOGIN_CREDENTIALS = {
    "email": "test.homeowner@example.com",
    "password": "testpassword123"
}


class HomeOwnerAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.home_owner_id = None
        self.home_owner_email = TEST_HOME_OWNER["email"]
        self.home_owner_password = TEST_HOME_OWNER["password"]
        
    def authenticate(self, email, password):
        """Authenticate and get access token"""
        print("\n" + "="*50)
        print("AUTHENTICATING...")
        print("="*50)
        
        response = self.session.post(
            f"{AUTH_URL}login",
            json={
                "email": email,
                "password": password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("data", {}).get("access")
            print(f"✓ Authentication successful")
            print(f"  Token: {self.access_token[:20]}...")
            return True
        else:
            print(f"✗ Authentication failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def set_headers(self):
        """Set authorization headers"""
        if self.access_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            })
    
    # ==================== HOME OWNER TESTS ====================
    
    def create_home_owner(self):
        """Test creating a new home owner"""
        print("\n" + "="*50)
        print("CREATING HOME OWNER...")
        print("="*50)
        
        response = self.session.post(
            HOME_OWNER_URL + "create",
            json=TEST_HOME_OWNER
        )
        
        if response.status_code == 201:
            data = response.json()
            self.home_owner_id = data.get("data", {}).get("id")
            print(f"✓ Home Owner created successfully")
            print(f"  ID: {self.home_owner_id}")
            print(f"  Email: {data.get('data', {}).get('email')}")
            return True
        else:
            print(f"✗ Failed to create home owner: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def login_home_owner(self):
        """Test home owner login"""
        print("\n" + "="*50)
        print("LOGGING IN HOME OWNER...")
        print("="*50)
        
        response = self.session.post(
            f"{HOME_OWNER_URL}login",
            json={
                "email": self.home_owner_email,
                "password": self.home_owner_password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("data", {}).get("access")
            print(f"✓ Login successful")
            print(f"  Token: {self.access_token[:20]}...")
            return True
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def list_home_owners(self):
        """Test listing all home owners"""
        print("\n" + "="*50)
        print("LISTING HOME OWNERS...")
        print("="*50)
        
        response = self.session.get(HOME_OWNER_URL)
        
        if response.status_code == 200:
            data = response.json()
            homeowner_list = data.get("data", {}).get("items", [])
            print(f"✓ Home Owner list retrieved successfully")
            print(f"  Total home owners: {len(homeowner_list)}")
            for homeowner in homeowner_list[:3]:
                print(f"    - {homeowner.get('full_name')} ({homeowner.get('email')})")
            return True
        else:
            print(f"✗ Failed to list home owners: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def get_home_owner_detail(self):
        """Test getting home owner details"""
        if not self.home_owner_id:
            print("\n✗ No home owner ID available for detail test")
            return False
            
        print("\n" + "="*50)
        print("GETTING HOME OWNER DETAIL...")
        print("="*50)
        
        response = self.session.get(f"{HOME_OWNER_URL}{self.home_owner_id}/")
        
        if response.status_code == 200:
            data = response.json()
            homeowner_data = data.get("data", {})
            print(f"✓ Home Owner detail retrieved successfully")
            print(f"  Name: {homeowner_data.get('full_name')}")
            print(f"  Email: {homeowner_data.get('email')}")
            print(f"  Phone: {homeowner_data.get('phone_number')}")
            return True
        else:
            print(f"✗ Failed to get home owner detail: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def update_home_owner(self):
        """Test updating home owner"""
        if not self.home_owner_id:
            print("\n✗ No home owner ID available for update test")
            return False
            
        print("\n" + "="*50)
        print("UPDATING HOME OWNER...")
        print("="*50)
        
        response = self.session.patch(
            f"{HOME_OWNER_URL}{self.home_owner_id}/update",
            json=TEST_HOME_OWNER_UPDATE
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Home Owner updated successfully")
            print(f"  New Name: {data.get('data', {}).get('full_name')}")
            return True
        else:
            print(f"✗ Failed to update home owner: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def change_home_owner_status(self):
        """Test changing home owner active status"""
        if not self.home_owner_id:
            print("\n✗ No home owner ID available for status change test")
            return False
            
        print("\n" + "="*50)
        print("CHANGING HOME OWNER STATUS...")
        print("="*50)
        
        response = self.session.patch(
            f"{HOME_OWNER_URL}{self.home_owner_id}/status",
            json={"is_active": False}
        )
        
        if response.status_code == 200:
            data = response.json()
            is_active = data.get("data", {}).get("is_active")
            print(f"✓ Home Owner status changed successfully")
            print(f"  New Status (is_active): {is_active}")
            return True
        else:
            print(f"✗ Failed to change home owner status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def reset_password(self):
        """Test resetting password"""
        print("\n" + "="*50)
        print("RESETTING PASSWORD...")
        print("="*50)
        
        response = self.session.post(
            f"{HOME_OWNER_URL}reset-password",
            json={
                "email": self.home_owner_email,
                "new_password": "newpassword123"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Password reset successful")
            print(f"  Message: {data.get('message')}")
            # Update password for subsequent logins
            self.home_owner_password = "newpassword123"
            return True
        else:
            print(f"✗ Password reset failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def delete_home_owner(self):
        """Test deleting home owner"""
        if not self.home_owner_id:
            print("\n✗ No home owner ID available for delete test")
            return False
            
        print("\n" + "="*50)
        print("DELETING HOME OWNER...")
        print("="*50)
        
        response = self.session.delete(f"{HOME_OWNER_URL}{self.home_owner_id}/delete")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Home Owner deleted successfully")
            print(f"  Message: {data.get('message')}")
            self.home_owner_id = None
            return True
        else:
            print(f"✗ Failed to delete home owner: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def run_home_owner_tests(self):
        """Run all home owner tests"""
        print("\n" + "#"*60)
        print("# HOME OWNER MODULE TESTS")
        print("#"*60)
        
        tests = [
            ("Create Home Owner", self.create_home_owner),
            ("Login Home Owner", self.login_home_owner),
            ("List Home Owners", self.list_home_owners),
            ("Get Home Owner Detail", self.get_home_owner_detail),
            ("Update Home Owner", self.update_home_owner),
            ("Change Home Owner Status", self.change_home_owner_status),
            ("Reset Password", self.reset_password),
            ("Delete Home Owner", self.delete_home_owner),
        ]
        
        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                results.append((name, result))
            except Exception as e:
                print(f"\n✗ Error in {name}: {str(e)}")
                results.append((name, False))
        
        return results
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "#"*60)
        print("# HOME OWNER MODULE API TEST SCRIPTS")
        print("#"*60)
        
        # Run home owner tests (some endpoints don't require authentication)
        homeowner_results = self.run_home_owner_tests()
        
        # Summary
        print("\n" + "#"*60)
        print("# TEST SUMMARY")
        print("#"*60)
        
        passed = sum(1 for _, result in homeowner_results if result)
        total = len(homeowner_results)
        
        print("\n--- Home Owner Module ---")
        for name, result in homeowner_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return passed == total


def main():
    """Main function"""
    tester = HomeOwnerAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
