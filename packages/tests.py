"""
Test scripts for Packages Module
================================
This script tests all package-related endpoints.

Usage:
    python packages/tests.py

Requirements:
    - Django server should be running
    - A superuser account should exist for authentication
"""

import requests
import json
import sys
import uuid

# Configuration
BASE_URL = "http://127.0.0.1:8000"
PACKAGES_URL = f"{BASE_URL}/packages/"
AUTH_URL = f"{BASE_URL}/auth/"

# Test data
SUPERUSER_EMAIL = "admin@qbox.com"
SUPERUSER_PASSWORD = "admin123"

# Generate unique tracking ID for test
def generate_unique_tracking_id():
    return f"TRK-{uuid.uuid4().hex[:8].upper()}"


# Package test data
TEST_PACKAGE = {
    "tracking_id": generate_unique_tracking_id(),
    "merchant_name": "Test Merchant",
    "merchant_phone": "1234567890",
    "sender_name": "Test Sender",
    "sender_phone": "0987654321",
    "sender_address": "123 Sender Street",
    "receiver_name": "Test Receiver",
    "receiver_phone": "1122334455",
    "receiver_address": "456 Receiver Street",
    "package_description": "Test package description",
    "weight": 2.5,
    "dimensions": "10x10x10",
    "package_type": "fragile",
    "shipment_status": "pending",
    "payment_method": "cash_on_delivery",
    "delivery_fee": 10.00,
    "package_fee": 50.00,
    "total_fee": 60.00
}

TEST_PACKAGE_UPDATE = {
    "package_description": "Updated test package description",
    "shipment_status": "in_transit"
}


class PackagesAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.package_id = None
        
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
            self.access_token = data.get("data", {}).get("tokens", {}).get("access") or data.get("access")
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
    
    # ==================== PACKAGE TESTS ====================
    
    def create_package(self):
        """Test creating a new package"""
        print("\n" + "="*50)
        print("CREATING PACKAGE...")
        print("="*50)
        
        response = self.session.post(
            f"{PACKAGES_URL}create",
            json=TEST_PACKAGE
        )
        
        if response.status_code == 201:
            data = response.json()
            self.package_id = data.get("data", {}).get("id")
            tracking_id = data.get("data", {}).get("tracking_id")
            print(f"✓ Package created successfully")
            print(f"  ID: {self.package_id}")
            print(f"  Tracking ID: {tracking_id}")
            return True
        else:
            print(f"✗ Failed to create package: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def list_packages(self):
        """Test listing all packages"""
        print("\n" + "="*50)
        print("LISTING PACKAGES...")
        print("="*50)
        
        response = self.session.get(PACKAGES_URL)
        
        if response.status_code == 200:
            data = response.json()
            package_list = data.get("data", {}).get("items", [])
            print(f"✓ Package list retrieved successfully")
            print(f"  Total packages: {len(package_list)}")
            for package in package_list[:3]:
                print(f"    - {package.get('tracking_id')} ({package.get('shipment_status')})")
            return True
        else:
            print(f"✗ Failed to list packages: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def get_package_detail(self):
        """Test getting package details"""
        if not self.package_id:
            print("\n✗ No package ID available for detail test")
            return False
            
        print("\n" + "="*50)
        print("GETTING PACKAGE DETAIL...")
        print("="*50)
        
        response = self.session.get(f"{PACKAGES_URL}{self.package_id}/")
        
        if response.status_code == 200:
            data = response.json()
            package_data = data.get("data", {})
            print(f"✓ Package detail retrieved successfully")
            print(f"  Tracking ID: {package_data.get('tracking_id')}")
            print(f"  Merchant: {package_data.get('merchant_name')}")
            print(f"  Status: {package_data.get('shipment_status')}")
            return True
        else:
            print(f"✗ Failed to get package detail: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def update_package(self):
        """Test updating package"""
        if not self.package_id:
            print("\n✗ No package ID available for update test")
            return False
            
        print("\n" + "="*50)
        print("UPDATING PACKAGE...")
        print("="*50)
        
        response = self.session.patch(
            f"{PACKAGES_URL}{self.package_id}/update",
            json=TEST_PACKAGE_UPDATE
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Package updated successfully")
            print(f"  New Description: {data.get('data', {}).get('package_description')}")
            return True
        else:
            print(f"✗ Failed to update package: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def change_package_status(self):
        """Test changing package active status"""
        if not self.package_id:
            print("\n✗ No package ID available for status change test")
            return False
            
        print("\n" + "="*50)
        print("CHANGING PACKAGE STATUS...")
        print("="*50)
        
        response = self.session.patch(
            f"{PACKAGES_URL}{self.package_id}/change-status",
            json={"is_active": False}
        )
        
        if response.status_code == 200:
            data = response.json()
            is_active = data.get("data", {}).get("is_active")
            print(f"✓ Package status changed successfully")
            print(f"  New Status (is_active): {is_active}")
            return True
        else:
            print(f"✗ Failed to change package status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def delete_package(self):
        """Test deleting package"""
        if not self.package_id:
            print("\n✗ No package ID available for delete test")
            return False
            
        print("\n" + "="*50)
        print("DELETING PACKAGE...")
        print("="*50)
        
        response = self.session.delete(f"{PACKAGES_URL}{self.package_id}/delete")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Package deleted successfully")
            print(f"  Message: {data.get('message')}")
            self.package_id = None
            return True
        else:
            print(f"✗ Failed to delete package: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def run_package_tests(self):
        """Run all package tests"""
        print("\n" + "#"*60)
        print("# PACKAGE MODULE TESTS")
        print("#"*60)
        
        tests = [
            ("Create Package", self.create_package),
            ("List Packages", self.list_packages),
            ("Get Package Detail", self.get_package_detail),
            ("Update Package", self.update_package),
            ("Change Package Status", self.change_package_status),
            ("Delete Package", self.delete_package),
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
        print("# PACKAGES MODULE API TEST SCRIPTS")
        print("#"*60)
        
        # Authenticate
        if not self.authenticate(SUPERUSER_EMAIL, SUPERUSER_PASSWORD):
            print("\n✗ Cannot proceed without authentication")
            return False
        
        self.set_headers()
        
        # Run package tests
        package_results = self.run_package_tests()
        
        # Summary
        print("\n" + "#"*60)
        print("# TEST SUMMARY")
        print("#"*60)
        
        passed = sum(1 for _, result in package_results if result)
        total = len(package_results)
        
        print("\n--- Package Module ---")
        for name, result in package_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return passed == total


def main():
    """Main function"""
    tester = PackagesAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
