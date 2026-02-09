"""
Test scripts for Staff Module
=============================
This script tests all staff-related endpoints.

Usage:
    python staff/tests.py

Requirements:
    - Django server should be running
    - A superuser account should exist for authentication
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000"
STAFF_URL = f"{BASE_URL}/staff/"
AUTH_URL = f"{BASE_URL}/auth/"

# Test data
SUPERUSER_EMAIL = "admin@qbox.com"
SUPERUSER_PASSWORD = "admin123"

# Staff test data
TEST_STAFF = {
    "name": "Test Staff Member",
    "email": "test.staff@example.com",
    "phone_number": "+1234567890",
    "password": "testpassword123",
    "role": "agent",
    "is_active": True,
    "is_staff": True
}

TEST_STAFF_UPDATE = {
    "name": "Updated Staff Name",
    "phone_number": "+0987654321",
    "role": "supervisor"
}


class StaffAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.staff_id = None
        
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
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        })
    
    # ==================== STAFF TESTS ====================
    
    def create_staff(self):
        """Test creating a new staff member"""
        print("\n" + "="*50)
        print("CREATING STAFF...")
        print("="*50)
        
        response = self.session.post(
            STAFF_URL + "create",
            json=TEST_STAFF
        )
        
        if response.status_code == 201:
            data = response.json()
            self.staff_id = data.get("data", {}).get("id")
            print(f"✓ Staff created successfully")
            print(f"  ID: {self.staff_id}")
            print(f"  Email: {data.get('data', {}).get('email')}")
            return True
        else:
            print(f"✗ Failed to create staff: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def list_staff(self):
        """Test listing all staff members"""
        print("\n" + "="*50)
        print("LISTING STAFF...")
        print("="*50)
        
        response = self.session.get(STAFF_URL)
        
        if response.status_code == 200:
            data = response.json()
            staff_list = data.get("data", {}).get("items", [])
            print(f"✓ Staff list retrieved successfully")
            print(f"  Total staff: {len(staff_list)}")
            for staff in staff_list[:3]:
                print(f"    - {staff.get('name')} ({staff.get('email')})")
            return True
        else:
            print(f"✗ Failed to list staff: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def get_staff_detail(self):
        """Test getting staff details"""
        if not self.staff_id:
            print("\n✗ No staff ID available for detail test")
            return False
            
        print("\n" + "="*50)
        print("GETTING STAFF DETAIL...")
        print("="*50)
        
        response = self.session.get(f"{STAFF_URL}{self.staff_id}/")
        
        if response.status_code == 200:
            data = response.json()
            staff_data = data.get("data", {})
            print(f"✓ Staff detail retrieved successfully")
            print(f"  Name: {staff_data.get('name')}")
            print(f"  Email: {staff_data.get('email')}")
            print(f"  Role: {staff_data.get('role')}")
            return True
        else:
            print(f"✗ Failed to get staff detail: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def update_staff(self):
        """Test updating staff member"""
        if not self.staff_id:
            print("\n✗ No staff ID available for update test")
            return False
            
        print("\n" + "="*50)
        print("UPDATING STAFF...")
        print("="*50)
        
        response = self.session.patch(
            f"{STAFF_URL}{self.staff_id}/update",
            json=TEST_STAFF_UPDATE
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Staff updated successfully")
            print(f"  New Name: {data.get('data', {}).get('name')}")
            print(f"  New Role: {data.get('data', {}).get('role')}")
            return True
        else:
            print(f"✗ Failed to update staff: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def change_staff_status(self):
        """Test changing staff active status"""
        if not self.staff_id:
            print("\n✗ No staff ID available for status change test")
            return False
            
        print("\n" + "="*50)
        print("CHANGING STAFF STATUS...")
        print("="*50)
        
        response = self.session.patch(
            f"{STAFF_URL}{self.staff_id}/change-status",
            json={"is_active": False}
        )
        
        if response.status_code == 200:
            data = response.json()
            is_active = data.get("data", {}).get("is_active")
            print(f"✓ Staff status changed successfully")
            print(f"  New Status (is_active): {is_active}")
            return True
        else:
            print(f"✗ Failed to change staff status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def delete_staff(self):
        """Test deleting staff member"""
        if not self.staff_id:
            print("\n✗ No staff ID available for delete test")
            return False
            
        print("\n" + "="*50)
        print("DELETING STAFF...")
        print("="*50)
        
        response = self.session.delete(f"{STAFF_URL}{self.staff_id}/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Staff deleted successfully")
            print(f"  Message: {data.get('message')}")
            self.staff_id = None
            return True
        else:
            print(f"✗ Failed to delete staff: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def run_staff_tests(self):
        """Run all staff tests"""
        print("\n" + "#"*60)
        print("# STAFF MODULE TESTS")
        print("#"*60)
        
        tests = [
            ("Create Staff", self.create_staff),
            ("List Staff", self.list_staff),
            ("Get Staff Detail", self.get_staff_detail),
            ("Update Staff", self.update_staff),
            ("Change Staff Status", self.change_staff_status),
            ("Delete Staff", self.delete_staff),
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
        print("# STAFF MODULE API TEST SCRIPTS")
        print("#"*60)
        
        # Authenticate
        if not self.authenticate(SUPERUSER_EMAIL, SUPERUSER_PASSWORD):
            print("\n✗ Cannot proceed without authentication")
            return False
        
        self.set_headers()
        
        # Run staff tests
        staff_results = self.run_staff_tests()
        
        # Summary
        print("\n" + "#"*60)
        print("# TEST SUMMARY")
        print("#"*60)
        
        passed = sum(1 for _, result in staff_results if result)
        total = len(staff_results)
        
        print("\n--- Staff Module ---")
        for name, result in staff_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return passed == total


def main():
    """Main function"""
    tester = StaffAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
