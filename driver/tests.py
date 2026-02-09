"""
Test scripts for Driver Module
==============================
This script tests all driver-related endpoints.

Usage:
    python driver/tests.py

Requirements:
    - Django server should be running
    - A superuser account should exist for authentication
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000"
DRIVER_URL = f"{BASE_URL}/driver/"
AUTH_URL = f"{BASE_URL}/auth/"

# Test data
SUPERUSER_EMAIL = "admin@qbox.com"
SUPERUSER_PASSWORD = "admin123"

# Driver test data
TEST_DRIVER = {
    "driver_name": "Test Driver",
    "email": "test.driver@example.com",
    "phone_number": "1234567890",
    "image": "https://example.com/driver.jpg",
    "is_active": True
}

TEST_DRIVER_UPDATE = {
    "driver_name": "Updated Driver Name",
    "phone_number": "0987654321"
}


class DriverAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.driver_id = None
        
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
    
    # ==================== DRIVER TESTS ====================
    
    def create_driver(self):
        """Test creating a new driver"""
        print("\n" + "="*50)
        print("CREATING DRIVER...")
        print("="*50)
        
        response = self.session.post(
            DRIVER_URL + "create",
            json=TEST_DRIVER
        )
        
        if response.status_code == 201:
            data = response.json()
            self.driver_id = data.get("data", {}).get("id")
            print(f"✓ Driver created successfully")
            print(f"  ID: {self.driver_id}")
            print(f"  Email: {data.get('data', {}).get('email')}")
            return True
        else:
            print(f"✗ Failed to create driver: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def list_drivers(self):
        """Test listing all drivers"""
        print("\n" + "="*50)
        print("LISTING DRIVERS...")
        print("="*50)
        
        response = self.session.get(DRIVER_URL)
        
        if response.status_code == 200:
            data = response.json()
            driver_list = data.get("data", {}).get("items", [])
            print(f"✓ Driver list retrieved successfully")
            print(f"  Total drivers: {len(driver_list)}")
            for driver in driver_list[:3]:
                print(f"    - {driver.get('driver_name')} ({driver.get('email')})")
            return True
        else:
            print(f"✗ Failed to list drivers: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def get_driver_detail(self):
        """Test getting driver details"""
        if not self.driver_id:
            print("\n✗ No driver ID available for detail test")
            return False
            
        print("\n" + "="*50)
        print("GETTING DRIVER DETAIL...")
        print("="*50)
        
        response = self.session.get(f"{DRIVER_URL}{self.driver_id}/")
        
        if response.status_code == 200:
            data = response.json()
            driver_data = data.get("data", {})
            print(f"✓ Driver detail retrieved successfully")
            print(f"  Name: {driver_data.get('driver_name')}")
            print(f"  Email: {driver_data.get('email')}")
            print(f"  Active: {driver_data.get('is_active')}")
            return True
        else:
            print(f"✗ Failed to get driver detail: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def update_driver(self):
        """Test updating driver"""
        if not self.driver_id:
            print("\n✗ No driver ID available for update test")
            return False
            
        print("\n" + "="*50)
        print("UPDATING DRIVER...")
        print("="*50)
        
        response = self.session.patch(
            f"{DRIVER_URL}{self.driver_id}/update",
            json=TEST_DRIVER_UPDATE
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Driver updated successfully")
            print(f"  New Name: {data.get('data', {}).get('driver_name')}")
            return True
        else:
            print(f"✗ Failed to update driver: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def change_driver_status(self):
        """Test changing driver active status"""
        if not self.driver_id:
            print("\n✗ No driver ID available for status change test")
            return False
            
        print("\n" + "="*50)
        print("CHANGING DRIVER STATUS...")
        print("="*50)
        
        response = self.session.patch(
            f"{DRIVER_URL}{self.driver_id}/change-status",
            json={"is_active": False}
        )
        
        if response.status_code == 200:
            data = response.json()
            is_active = data.get("data", {}).get("is_active")
            print(f"✓ Driver status changed successfully")
            print(f"  New Status (is_active): {is_active}")
            return True
        else:
            print(f"✗ Failed to change driver status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def delete_driver(self):
        """Test deleting driver"""
        if not self.driver_id:
            print("\n✗ No driver ID available for delete test")
            return False
            
        print("\n" + "="*50)
        print("DELETING DRIVER...")
        print("="*50)
        
        response = self.session.delete(f"{DRIVER_URL}{self.driver_id}/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Driver deleted successfully")
            print(f"  Message: {data.get('message')}")
            self.driver_id = None
            return True
        else:
            print(f"✗ Failed to delete driver: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def run_driver_tests(self):
        """Run all driver tests"""
        print("\n" + "#"*60)
        print("# DRIVER MODULE TESTS")
        print("#"*60)
        
        tests = [
            ("Create Driver", self.create_driver),
            ("List Drivers", self.list_drivers),
            ("Get Driver Detail", self.get_driver_detail),
            ("Update Driver", self.update_driver),
            ("Change Driver Status", self.change_driver_status),
            ("Delete Driver", self.delete_driver),
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
        print("# DRIVER MODULE API TEST SCRIPTS")
        print("#"*60)
        
        # Authenticate
        if not self.authenticate(SUPERUSER_EMAIL, SUPERUSER_PASSWORD):
            print("\n✗ Cannot proceed without authentication")
            return False
        
        self.set_headers()
        
        # Run driver tests
        driver_results = self.run_driver_tests()
        
        # Summary
        print("\n" + "#"*60)
        print("# TEST SUMMARY")
        print("#"*60)
        
        passed = sum(1 for _, result in driver_results if result)
        total = len(driver_results)
        
        print("\n--- Driver Module ---")
        for name, result in driver_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return passed == total


def main():
    """Main function"""
    tester = DriverAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
