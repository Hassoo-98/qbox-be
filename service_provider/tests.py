"""
Test scripts for Service Provider Module
=========================================
This script tests all service provider-related endpoints.

Usage:
    python service_provider/tests.py

Requirements:
    - Django server should be running
"""

import requests
import json
import sys
import uuid

# Configuration
BASE_URL = "http://127.0.0.1:8000"
SERVICE_PROVIDER_URL = f"{BASE_URL}/service_provider/"

# Generate unique email for test
def generate_unique_email():
    return f"test.provider.{uuid.uuid4().hex[:8]}@example.com"


# Service Provider test data
TEST_SERVICE_PROVIDER = {
    "business_name": "Test Service Provider",
    "email": generate_unique_email(),
    "phone_number": "1234567890",
    "business_registration_number": f"REG-{uuid.uuid4().hex[:8].upper()}",
    "business_address": "123 Test Street, Test City",
    "operating_cities": ["Karachi", "Lahore"],
    "service_categories": ["Installation", "Maintenance"],
    "hourly_rate": 50.00,
    "is_approved": False
}

TEST_SERVICE_PROVIDER_UPDATE = {
    "business_name": "Updated Service Provider",
    "hourly_rate": 75.00
}


class ServiceProviderAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.service_provider_id = None
        
    # ==================== SERVICE PROVIDER TESTS ====================
    
    def create_service_provider(self):
        """Test creating a new service provider"""
        print("\n" + "="*50)
        print("CREATING SERVICE PROVIDER...")
        print("="*50)
        
        response = self.session.post(
            SERVICE_PROVIDER_URL,
            json=TEST_SERVICE_PROVIDER
        )
        
        if response.status_code == 201:
            data = response.json()
            if isinstance(data, dict):
                self.service_provider_id = data.get("id") or data.get("data", {}).get("id")
                print(f"✓ Service Provider created successfully")
                print(f"  ID: {self.service_provider_id}")
                print(f"  Business Name: {data.get('business_name') or data.get('data', {}).get('business_name')}")
            else:
                self.service_provider_id = data.get("id") if isinstance(data, list) else None
                print(f"✓ Service Provider created successfully")
                print(f"  Response: {data}")
            return True
        else:
            print(f"✗ Failed to create service provider: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def list_service_providers(self):
        """Test listing all service providers"""
        print("\n" + "="*50)
        print("LISTING SERVICE PROVIDERS...")
        print("="*50)
        
        response = self.session.get(SERVICE_PROVIDER_URL)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                provider_list = data
            else:
                provider_list = data.get("data", {}).get("items", []) or data.get("items", []) or data.get("data", [])
            print(f"✓ Service Provider list retrieved successfully")
            print(f"  Total providers: {len(provider_list)}")
            for provider in provider_list[:3]:
                name = provider.get("business_name") or provider.get("name")
                print(f"    - {name}")
            return True
        else:
            print(f"✗ Failed to list service providers: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def get_service_provider_detail(self):
        """Test getting service provider details"""
        if not self.service_provider_id:
            print("\n✗ No service provider ID available for detail test")
            return False
            
        print("\n" + "="*50)
        print("GETTING SERVICE PROVIDER DETAIL...")
        print("="*50)
        
        response = self.session.get(f"{SERVICE_PROVIDER_URL}{self.service_provider_id}/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Service Provider detail retrieved successfully")
            print(f"  Business Name: {data.get('business_name') or data.get('data', {}).get('business_name')}")
            print(f"  Email: {data.get('email') or data.get('data', {}).get('email')}")
            print(f"  Approved: {data.get('is_approved') or data.get('data', {}).get('is_approved')}")
            return True
        else:
            print(f"✗ Failed to get service provider detail: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def update_service_provider(self):
        """Test updating service provider"""
        if not self.service_provider_id:
            print("\n✗ No service provider ID available for update test")
            return False
            
        print("\n" + "="*50)
        print("UPDATING SERVICE PROVIDER...")
        print("="*50)
        
        response = self.session.put(
            f"{SERVICE_PROVIDER_URL}{self.service_provider_id}/",
            json=TEST_SERVICE_PROVIDER_UPDATE
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Service Provider updated successfully")
            name = data.get("business_name") or data.get("data", {}).get("business_name")
            print(f"  New Name: {name}")
            return True
        else:
            print(f"✗ Failed to update service provider: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def approve_service_provider(self):
        """Test approving/disapproving service provider"""
        if not self.service_provider_id:
            print("\n✗ No service provider ID available for approval test")
            return False
            
        print("\n" + "="*50)
        print("APPROVING SERVICE PROVIDER...")
        print("="*50)
        
        response = self.session.patch(
            f"{SERVICE_PROVIDER_URL}{self.service_provider_id}/approve",
            json={"is_approved": True}
        )
        
        if response.status_code == 200:
            data = response.json()
            is_approved = data.get("is_approved") or data.get("data", {}).get("is_approved")
            print(f"✓ Service Provider approval status changed successfully")
            print(f"  New Approval Status: {is_approved}")
            return True
        else:
            print(f"✗ Failed to approve service provider: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def delete_service_provider(self):
        """Test deleting service provider"""
        if not self.service_provider_id:
            print("\n✗ No service provider ID available for delete test")
            return False
            
        print("\n" + "="*50)
        print("DELETING SERVICE PROVIDER...")
        print("="*50)
        
        response = self.session.delete(f"{SERVICE_PROVIDER_URL}{self.service_provider_id}/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Service Provider deleted successfully")
            print(f"  Message: {data.get('message') or data.get('Message')}")
            self.service_provider_id = None
            return True
        else:
            print(f"✗ Failed to delete service provider: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def run_service_provider_tests(self):
        """Run all service provider tests"""
        print("\n" + "#"*60)
        print("# SERVICE PROVIDER MODULE TESTS")
        print("#"*60)
        
        tests = [
            ("Create Service Provider", self.create_service_provider),
            ("List Service Providers", self.list_service_providers),
            ("Get Service Provider Detail", self.get_service_provider_detail),
            ("Update Service Provider", self.update_service_provider),
            ("Approve Service Provider", self.approve_service_provider),
            ("Delete Service Provider", self.delete_service_provider),
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
        print("# SERVICE PROVIDER MODULE API TEST SCRIPTS")
        print("#"*60)
        
        # Run service provider tests
        sp_results = self.run_service_provider_tests()
        
        # Summary
        print("\n" + "#"*60)
        print("# TEST SUMMARY")
        print("#"*60)
        
        passed = sum(1 for _, result in sp_results if result)
        total = len(sp_results)
        
        print("\n--- Service Provider Module ---")
        for name, result in sp_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return passed == total


def main():
    """Main function"""
    tester = ServiceProviderAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
