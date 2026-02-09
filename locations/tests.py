"""
Test scripts for Locations Module
================================
This script tests all location-related endpoints (Cities and Areas).

Usage:
    python locations/tests.py

Requirements:
    - Django server should be running
    - A superuser account should exist for authentication
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000"
LOCATIONS_URL = f"{BASE_URL}/locations/"
AUTH_URL = f"{BASE_URL}/auth/"

# Test data
SUPERUSER_EMAIL = "admin@qbox.com"
SUPERUSER_PASSWORD = "admin123"

# City test data
TEST_CITY = {
    "name": "Test City",
    "name_ar": "مدينة الاختبار",
    "code": "TC",
    "state": "Test State",
    "country": "Test Country"
}

TEST_CITY_UPDATE = {
    "name": "Updated Test City",
    "code": "UTC"
}

# Area test data
TEST_AREA = {
    "name": "Test Area",
    "city": 1,  # Will be updated dynamically
    "postal_code": "12345"
}

TEST_AREA_UPDATE = {
    "name": "Updated Test Area",
    "postal_code": "54321"
}


class LocationsAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.city_id = None
        self.area_id = None
        
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
    
    # ==================== CITY TESTS ====================
    
    def create_city(self):
        """Test creating a new city"""
        print("\n" + "="*50)
        print("CREATING CITY...")
        print("="*50)
        
        response = self.session.post(
            f"{LOCATIONS_URL}city/create",
            json=TEST_CITY
        )
        
        if response.status_code == 201:
            data = response.json()
            self.city_id = data.get("data", {}).get("id")
            print(f"✓ City created successfully")
            print(f"  ID: {self.city_id}")
            print(f"  Name: {data.get('data', {}).get('name')}")
            return True
        else:
            print(f"✗ Failed to create city: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def list_cities(self):
        """Test listing all cities"""
        print("\n" + "="*50)
        print("LISTING CITIES...")
        print("="*50)
        
        response = self.session.get(f"{LOCATIONS_URL}city")
        
        if response.status_code == 200:
            data = response.json()
            city_list = data.get("data", {}).get("items", [])
            print(f"✓ City list retrieved successfully")
            print(f"  Total cities: {len(city_list)}")
            for city in city_list[:3]:
                print(f"    - {city.get('name')} ({city.get('code')})")
            return True
        else:
            print(f"✗ Failed to list cities: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def get_city_detail(self):
        """Test getting city details"""
        if not self.city_id:
            print("\n✗ No city ID available for detail test")
            return False
            
        print("\n" + "="*50)
        print("GETTING CITY DETAIL...")
        print("="*50)
        
        response = self.session.get(f"{LOCATIONS_URL}city/{self.city_id}/")
        
        if response.status_code == 200:
            data = response.json()
            city_data = data.get("data", {})
            print(f"✓ City detail retrieved successfully")
            print(f"  Name: {city_data.get('name')}")
            print(f"  Code: {city_data.get('code')}")
            print(f"  Country: {city_data.get('country')}")
            return True
        else:
            print(f"✗ Failed to get city detail: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def update_city(self):
        """Test updating city"""
        if not self.city_id:
            print("\n✗ No city ID available for update test")
            return False
            
        print("\n" + "="*50)
        print("UPDATING CITY...")
        print("="*50)
        
        response = self.session.patch(
            f"{LOCATIONS_URL}city/{self.city_id}/update",
            json=TEST_CITY_UPDATE
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ City updated successfully")
            print(f"  New Name: {data.get('data', {}).get('name')}")
            return True
        else:
            print(f"✗ Failed to update city: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def change_city_status(self):
        """Test changing city active status"""
        if not self.city_id:
            print("\n✗ No city ID available for status change test")
            return False
            
        print("\n" + "="*50)
        print("CHANGING CITY STATUS...")
        print("="*50)
        
        response = self.session.patch(
            f"{LOCATIONS_URL}city/{self.city_id}/change-status",
            json={"is_active": False}
        )
        
        if response.status_code == 200:
            data = response.json()
            is_active = data.get("data", {}).get("is_active")
            print(f"✓ City status changed successfully")
            print(f"  New Status (is_active): {is_active}")
            return True
        else:
            print(f"✗ Failed to change city status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def delete_city(self):
        """Test deleting city"""
        if not self.city_id:
            print("\n✗ No city ID available for delete test")
            return False
            
        print("\n" + "="*50)
        print("DELETING CITY...")
        print("="*50)
        
        response = self.session.delete(f"{LOCATIONS_URL}city/{self.city_id}/delete")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ City deleted successfully")
            print(f"  Message: {data.get('message')}")
            self.city_id = None
            return True
        else:
            print(f"✗ Failed to delete city: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    # ==================== AREA TESTS ====================
    
    def create_area(self):
        """Test creating a new area"""
        if not self.city_id:
            print("\n✗ No city ID available, cannot create area")
            return False
            
        TEST_AREA["city"] = self.city_id
        
        print("\n" + "="*50)
        print("CREATING AREA...")
        print("="*50)
        
        response = self.session.post(
            f"{LOCATIONS_URL}area/create",
            json=TEST_AREA
        )
        
        if response.status_code == 201:
            data = response.json()
            self.area_id = data.get("data", {}).get("id")
            print(f"✓ Area created successfully")
            print(f"  ID: {self.area_id}")
            print(f"  Name: {data.get('data', {}).get('name')}")
            return True
        else:
            print(f"✗ Failed to create area: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def list_areas(self):
        """Test listing all areas"""
        print("\n" + "="*50)
        print("LISTING AREAS...")
        print("="*50)
        
        response = self.session.get(f"{LOCATIONS_URL}area")
        
        if response.status_code == 200:
            data = response.json()
            area_list = data.get("data", {}).get("items", [])
            print(f"✓ Area list retrieved successfully")
            print(f"  Total areas: {len(area_list)}")
            for area in area_list[:3]:
                print(f"    - {area.get('name')}")
            return True
        else:
            print(f"✗ Failed to list areas: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def get_area_detail(self):
        """Test getting area details"""
        if not self.area_id:
            print("\n✗ No area ID available for detail test")
            return False
            
        print("\n" + "="*50)
        print("GETTING AREA DETAIL...")
        print("="*50)
        
        response = self.session.get(f"{LOCATIONS_URL}area/{self.area_id}/")
        
        if response.status_code == 200:
            data = response.json()
            area_data = data.get("data", {})
            print(f"✓ Area detail retrieved successfully")
            print(f"  Name: {area_data.get('name')}")
            print(f"  Postal Code: {area_data.get('postal_code')}")
            return True
        else:
            print(f"✗ Failed to get area detail: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def update_area(self):
        """Test updating area"""
        if not self.area_id:
            print("\n✗ No area ID available for update test")
            return False
            
        print("\n" + "="*50)
        print("UPDATING AREA...")
        print("="*50)
        
        response = self.session.patch(
            f"{LOCATIONS_URL}area/{self.area_id}/update",
            json=TEST_AREA_UPDATE
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Area updated successfully")
            print(f"  New Name: {data.get('data', {}).get('name')}")
            return True
        else:
            print(f"✗ Failed to update area: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def change_area_status(self):
        """Test changing area active status"""
        if not self.area_id:
            print("\n✗ No area ID available for status change test")
            return False
            
        print("\n" + "="*50)
        print("CHANGING AREA STATUS...")
        print("="*50)
        
        response = self.session.patch(
            f"{LOCATIONS_URL}area/{self.area_id}/change-status",
            json={"is_active": False}
        )
        
        if response.status_code == 200:
            data = response.json()
            is_active = data.get("data", {}).get("is_active")
            print(f"✓ Area status changed successfully")
            print(f"  New Status (is_active): {is_active}")
            return True
        else:
            print(f"✗ Failed to change area status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def delete_area(self):
        """Test deleting area"""
        if not self.area_id:
            print("\n✗ No area ID available for delete test")
            return False
            
        print("\n" + "="*50)
        print("DELETING AREA...")
        print("="*50)
        
        response = self.session.delete(f"{LOCATIONS_URL}area/{self.area_id}/delete")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Area deleted successfully")
            print(f"  Message: {data.get('message')}")
            self.area_id = None
            return True
        else:
            print(f"✗ Failed to delete area: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def run_city_tests(self):
        """Run all city tests"""
        print("\n" + "#"*60)
        print("# CITY MODULE TESTS")
        print("#"*60)
        
        tests = [
            ("Create City", self.create_city),
            ("List Cities", self.list_cities),
            ("Get City Detail", self.get_city_detail),
            ("Update City", self.update_city),
            ("Change City Status", self.change_city_status),
            ("Delete City", self.delete_city),
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
    
    def run_area_tests(self):
        """Run all area tests"""
        print("\n" + "#"*60)
        print("# AREA MODULE TESTS")
        print("#"*60)
        
        tests = [
            ("Create Area", self.create_area),
            ("List Areas", self.list_areas),
            ("Get Area Detail", self.get_area_detail),
            ("Update Area", self.update_area),
            ("Change Area Status", self.change_area_status),
            ("Delete Area", self.delete_area),
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
        print("# LOCATIONS MODULE API TEST SCRIPTS")
        print("#"*60)
        
        # Authenticate
        if not self.authenticate(SUPERUSER_EMAIL, SUPERUSER_PASSWORD):
            print("\n✗ Cannot proceed without authentication")
            return False
        
        self.set_headers()
        
        # Run city tests
        city_results = self.run_city_tests()
        
        # Run area tests
        area_results = self.run_area_tests()
        
        # Summary
        print("\n" + "#"*60)
        print("# TEST SUMMARY")
        print("#"*60)
        
        all_results = city_results + area_results
        passed = sum(1 for _, result in all_results if result)
        total = len(all_results)
        
        print("\n--- City Module ---")
        for name, result in city_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {name}")
        
        print("\n--- Area Module ---")
        for name, result in area_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return passed == total


def main():
    """Main function"""
    tester = LocationsAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
