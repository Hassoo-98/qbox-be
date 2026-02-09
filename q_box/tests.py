"""
Test scripts for QBox Module
============================
This script tests all QBox-related endpoints.

Usage:
    python q_box/tests.py

Requirements:
    - Django server should be running
"""

import requests
import json
import sys
import uuid

# Configuration
BASE_URL = "http://127.0.0.1:8000"
QBOX_URL = f"{BASE_URL}/qbox/"
QRCODE_URL = f"{BASE_URL}/qbox/qrcode/"

# Generate unique qbox_id for test
def generate_unique_qbox_id():
    return f"QBOX-{uuid.uuid4().hex[:8].upper()}"


# QBox test data
TEST_QBOX = {
    "qbox_id": generate_unique_qbox_id(),
    "status": "Offline",
    "led_indicator": "Green",
    "camera_status": "Working",
    "qbox_image": "https://example.com/qbox.jpg"
}

TEST_QBOX_UPDATE = {
    "status": "Online",
    "led_indicator": "Red"
}

# QR Code test data
TEST_QRCODE = {
    "qbox_id": "",  # Will be set after creating qbox
    "name": "Test QR Code",
    "location": "Main Entrance",
    "address": "123 Test Street, Test City",
    "max_users": 5,
    "duration_type": "days",
    "valid_duration": 1
}

TEST_QRCODE_ACCESS = {
    "access_token": "",  # Will be set after creating qrcode
    "user_identifier": "test.user@example.com",
    "user_name": "Test User"
}


class QBoxAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.qbox_id = None
        self.qrcode_id = None
        self.qrcode_access_token = None
        
    # ==================== QBOX TESTS ====================
    
    def create_qbox(self):
        """Test creating a new QBox"""
        print("\n" + "="*50)
        print("CREATING QBOX...")
        print("="*50)
        
        response = self.session.post(
            QBOX_URL + "create",
            json=TEST_QBOX
        )
        
        if response.status_code == 201:
            data = response.json()
            self.qbox_id = data.get("data", {}).get("id")
            qbox_id_value = data.get("data", {}).get("qbox_id")
            TEST_QRCODE["qbox_id"] = qbox_id_value
            print(f"✓ QBox created successfully")
            print(f"  ID: {self.qbox_id}")
            print(f"  QBox ID: {qbox_id_value}")
            return True
        else:
            print(f"✗ Failed to create QBox: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def list_qboxes(self):
        """Test listing all QBoxes"""
        print("\n" + "="*50)
        print("LISTING QBOXES...")
        print("="*50)
        
        response = self.session.get(QBOX_URL)
        
        if response.status_code == 200:
            data = response.json()
            qbox_list = data.get("data", {}).get("items", [])
            print(f"✓ QBox list retrieved successfully")
            print(f"  Total QBoxes: {len(qbox_list)}")
            for qbox in qbox_list[:3]:
                print(f"    - {qbox.get('qbox_id')} ({qbox.get('status')})")
            return True
        else:
            print(f"✗ Failed to list QBoxes: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def get_qbox_detail(self):
        """Test getting QBox details"""
        if not self.qbox_id:
            print("\n✗ No QBox ID available for detail test")
            return False
            
        print("\n" + "="*50)
        print("GETTING QBOX DETAIL...")
        print("="*50)
        
        response = self.session.get(f"{QBOX_URL}{self.qbox_id}/")
        
        if response.status_code == 200:
            data = response.json()
            qbox_data = data.get("data", {})
            print(f"✓ QBox detail retrieved successfully")
            print(f"  QBox ID: {qbox_data.get('qbox_id')}")
            print(f"  Status: {qbox_data.get('status')}")
            print(f"  LED Indicator: {qbox_data.get('led_indicator')}")
            return True
        else:
            print(f"✗ Failed to get QBox detail: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def update_qbox(self):
        """Test updating QBox"""
        if not self.qbox_id:
            print("\n✗ No QBox ID available for update test")
            return False
            
        print("\n" + "="*50)
        print("UPDATING QBOX...")
        print("="*50)
        
        response = self.session.patch(
            f"{QBOX_URL}{self.qbox_id}/update",
            json=TEST_QBOX_UPDATE
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ QBox updated successfully")
            print(f"  New Status: {data.get('data', {}).get('status')}")
            return True
        else:
            print(f"✗ Failed to update QBox: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def change_qbox_status(self):
        """Test changing QBox active status"""
        if not self.qbox_id:
            print("\n✗ No QBox ID available for status change test")
            return False
            
        print("\n" + "="*50)
        print("CHANGING QBOX STATUS...")
        print("="*50)
        
        response = self.session.patch(
            f"{QBOX_URL}{self.qbox_id}/status",
            json={"is_active": False}
        )
        
        if response.status_code == 200:
            data = response.json()
            is_active = data.get("data", {}).get("is_active")
            print(f"✓ QBox status changed successfully")
            print(f"  New Status (is_active): {is_active}")
            return True
        else:
            print(f"✗ Failed to change QBox status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def verify_qbox_id(self):
        """Test verifying QBox ID"""
        print("\n" + "="*50)
        print("VERIFYING QBOX ID...")
        print("="*50)
        
        response = self.session.post(
            f"{QBOX_URL}verify",
            json={"qbox_id": TEST_QBOX["qbox_id"]}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ QBox ID verified successfully")
            print(f"  Message: {data.get('message')}")
            return True
        else:
            print(f"✗ Failed to verify QBox ID: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def delete_qbox(self):
        """Test deleting QBox"""
        if not self.qbox_id:
            print("\n✗ No QBox ID available for delete test")
            return False
            
        print("\n" + "="*50)
        print("DELETING QBOX...")
        print("="*50)
        
        response = self.session.delete(f"{QBOX_URL}{self.qbox_id}/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ QBox deleted successfully")
            print(f"  Message: {data.get('message')}")
            self.qbox_id = None
            return True
        else:
            print(f"✗ Failed to delete QBox: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    # ==================== QR CODE TESTS ====================
    
    def create_qrcode(self):
        """Test creating a new QR Code"""
        if not TEST_QRCODE["qbox_id"]:
            print("\n✗ No QBox ID available for QR code creation")
            return False
            
        print("\n" + "="*50)
        print("CREATING QR CODE...")
        print("="*50)
        
        response = self.session.post(
            QRCODE_URL + "create",
            json=TEST_QRCODE
        )
        
        if response.status_code == 201:
            data = response.json()
            self.qrcode_id = data.get("data", {}).get("id")
            self.qrcode_access_token = data.get("data", {}).get("access_token")
            TEST_QRCODE_ACCESS["access_token"] = self.qrcode_access_token
            print(f"✓ QR Code created successfully")
            print(f"  ID: {self.qrcode_id}")
            print(f"  Name: {data.get('data', {}).get('name')}")
            return True
        else:
            print(f"✗ Failed to create QR Code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def list_qrcodes(self):
        """Test listing all QR Codes"""
        print("\n" + "="*50)
        print("LISTING QR CODES...")
        print("="*50)
        
        response = self.session.get(QRCODE_URL)
        
        if response.status_code == 200:
            data = response.json()
            qrcode_list = data.get("data", {}).get("items", [])
            print(f"✓ QR Code list retrieved successfully")
            print(f"  Total QR Codes: {len(qrcode_list)}")
            for qrcode in qrcode_list[:3]:
                print(f"    - {qrcode.get('name')} ({qrcode.get('location')})")
            return True
        else:
            print(f"✗ Failed to list QR Codes: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def get_qrcode_detail(self):
        """Test getting QR Code details"""
        if not self.qrcode_id:
            print("\n✗ No QR Code ID available for detail test")
            return False
            
        print("\n" + "="*50)
        print("GETTING QR CODE DETAIL...")
        print("="*50)
        
        response = self.session.get(f"{QRCODE_URL}{self.qrcode_id}/")
        
        if response.status_code == 200:
            data = response.json()
            qrcode_data = data.get("data", {})
            print(f"✓ QR Code detail retrieved successfully")
            print(f"  Name: {qrcode_data.get('name')}")
            print(f"  Location: {qrcode_data.get('location')}")
            print(f"  Status: {qrcode_data.get('is_active')}")
            return True
        else:
            print(f"✗ Failed to get QR Code detail: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def access_qrcode(self):
        """Test accessing QBox via QR Code"""
        if not self.qrcode_access_token:
            print("\n✗ No QR Code access token available")
            return False
            
        print("\n" + "="*50)
        print("ACCESSING QBOX VIA QR CODE...")
        print("="*50)
        
        response = self.session.post(
            f"{QRCODE_URL}access",
            json=TEST_QRCODE_ACCESS
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ QBox access via QR Code successful")
            print(f"  Message: {data.get('message')}")
            return True
        else:
            print(f"✗ Failed to access QBox via QR Code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def delete_qrcode(self):
        """Test deleting QR Code"""
        if not self.qrcode_id:
            print("\n✗ No QR Code ID available for delete test")
            return False
            
        print("\n" + "="*50)
        print("DELETING QR CODE...")
        print("="*50)
        
        response = self.session.delete(f"{QRCODE_URL}{self.qrcode_id}/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ QR Code deleted successfully")
            print(f"  Message: {data.get('message')}")
            self.qrcode_id = None
            return True
        else:
            print(f"✗ Failed to delete QR Code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def run_qbox_tests(self):
        """Run all QBox tests"""
        print("\n" + "#"*60)
        print("# QBOX MODULE TESTS")
        print("#"*60)
        
        tests = [
            ("Create QBox", self.create_qbox),
            ("List QBoxes", self.list_qboxes),
            ("Get QBox Detail", self.get_qbox_detail),
            ("Update QBox", self.update_qbox),
            ("Change QBox Status", self.change_qbox_status),
            ("Verify QBox ID", self.verify_qbox_id),
            ("Delete QBox", self.delete_qbox),
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
    
    def run_qrcode_tests(self):
        """Run all QR Code tests"""
        print("\n" + "#"*60)
        print("# QR CODE MODULE TESTS")
        print("#"*60)
        
        tests = [
            ("Create QR Code", self.create_qrcode),
            ("List QR Codes", self.list_qrcodes),
            ("Get QR Code Detail", self.get_qrcode_detail),
            ("Access QBox via QR Code", self.access_qrcode),
            ("Delete QR Code", self.delete_qrcode),
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
        print("# QBOX MODULE API TEST SCRIPTS")
        print("#"*60)
        
        # Run QBox tests
        qbox_results = self.run_qbox_tests()
        
        # Run QR Code tests
        qrcode_results = self.run_qrcode_tests()
        
        # Summary
        print("\n" + "#"*60)
        print("# TEST SUMMARY")
        print("#"*60)
        
        all_results = qbox_results + qrcode_results
        passed = sum(1 for _, result in all_results if result)
        total = len(all_results)
        
        print("\n--- QBox Module ---")
        for name, result in qbox_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {name}")
        
        print("\n--- QR Code Module ---")
        for name, result in qrcode_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return passed == total


def main():
    """Main function"""
    tester = QBoxAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
