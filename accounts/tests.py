"""
Test scripts for Accounts (Authentication) Module
==================================================
This script tests all authentication-related endpoints.

Usage:
    python accounts/tests.py

Requirements:
    - Django server should be running
"""

import requests
import json
import sys
import uuid

# Configuration
BASE_URL = "https://backend.qbox.sa"
AUTH_URL = f"{BASE_URL}/auth/"


class AccountsAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        # Generate unique email for test
        self.user_email = f"test.user.{uuid.uuid4().hex[:8]}@example.com"
        self.user_password = "testpassword123"
        
    # ==================== HELPER METHODS ====================
    
    def register_and_login(self):
        """Register a user and login with the same credentials"""
        print("\n" + "="*50)
        print("REGISTERING AND LOGGING IN USER...")
        print("="*50)
        
        # Register user first
        test_user = {
            "email": self.user_email,
            "password": self.user_password,
            "name": "Test User",
            "phone_number": "1234567890",
            "role": "homeowner"  # Use "homeowner" (not "home_owner")
        }
        
        response = self.session.post(
            f"{AUTH_URL}register",
            json=test_user
        )
        
        if response.status_code == 201:
            data = response.json()
            self.user_id = data.get("data", {}).get("id")
            print(f"✓ User registered successfully")
            print(f"  ID: {self.user_id}")
            print(f"  Email: {data.get('data', {}).get('email')}")
        elif response.status_code == 400 and "email" in response.text.lower():
            # User already exists, try to login
            print(f"User already exists, attempting login...")
        else:
            print(f"✗ Registration failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
        # Now login
        return self.login_user()
    
    def login_user(self):
        """Test user login"""
        print("\n" + "="*50)
        print("LOGGING IN USER...")
        print("="*50)
        
        response = self.session.post(
            f"{AUTH_URL}login",
            json={
                "email": self.user_email,
                "password": self.user_password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("data", {}).get("tokens", {}).get("access")
            self.refresh_token = data.get("data", {}).get("tokens", {}).get("refresh")
            print(f"✓ Login successful")
            print(f"  Access Token: {self.access_token[:20]}...")
            return True
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    # ==================== AUTHENTICATION TESTS ====================
    
    def get_profile(self):
        """Test getting user profile"""
        if not self.access_token:
            print("\n✗ No access token available for profile test")
            return False
            
        print("\n" + "="*50)
        print("GETTING USER PROFILE...")
        print("="*50)
        
        response = self.session.get(
            f"{AUTH_URL}profile/",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Profile retrieved successfully")
            print(f"  Name: {data.get('data', {}).get('full_name')}")
            print(f"  Email: {data.get('data', {}).get('email')}")
            return True
        else:
            print(f"✗ Failed to get profile: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def update_profile(self):
        """Test updating user profile"""
        if not self.access_token:
            print("\n✗ No access token available for profile update test")
            return False
            
        print("\n" + "="*50)
        print("UPDATING USER PROFILE...")
        print("="*50)
        
        response = self.session.patch(
            f"{AUTH_URL}profile/",
            json={"full_name": "Updated Test User"},
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Profile updated successfully")
            print(f"  New Name: {data.get('data', {}).get('full_name')}")
            return True
        else:
            print(f"✗ Failed to update profile: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def change_password(self):
        """Test changing password"""
        if not self.access_token:
            print("\n✗ No access token available for password change test")
            return False
            
        print("\n" + "="*50)
        print("CHANGING PASSWORD...")
        print("="*50)
        
        response = self.session.put(
            f"{AUTH_URL}change-password",
            json={
                "old_password": self.user_password,
                "new_password": "newpassword123"
            },
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Password changed successfully")
            print(f"  Message: {data.get('message')}")
            # Update password for subsequent logins
            self.user_password = "newpassword123"
            return True
        else:
            print(f"✗ Failed to change password: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def refresh_token(self):
        """Test refreshing access token"""
        if not self.refresh_token:
            print("\n✗ No refresh token available")
            return False
            
        print("\n" + "="*50)
        print("REFRESHING TOKEN...")
        print("="*50)
        
        response = self.session.post(
            f"{AUTH_URL}token/refresh",
            json={"refresh": self.refresh_token}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access")
            print(f"✓ Token refreshed successfully")
            print(f"  New Access Token: {self.access_token[:20]}...")
            return True
        else:
            print(f"✗ Token refresh failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def list_users(self):
        """Test listing users (admin only)"""
        if not self.access_token:
            print("\n✗ No access token available for users list test")
            return False
            
        print("\n" + "="*50)
        print("LISTING USERS...")
        print("="*50)
        
        response = self.session.get(
            f"{AUTH_URL}users/",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            user_list = data if isinstance(data, list) else data.get("data", {}).get("items", [])
            print(f"✓ User list retrieved successfully")
            print(f"  Total users: {len(user_list)}")
            return True
        else:
            print(f"✗ Failed to list users: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def get_user_detail(self):
        """Test getting user detail"""
        if not self.access_token or not self.user_id:
            print("\n✗ No access token or user ID available for detail test")
            return False
            
        print("\n" + "="*50)
        print("GETTING USER DETAIL...")
        print("="*50)
        
        response = self.session.get(
            f"{AUTH_URL}users/{self.user_id}/",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ User detail retrieved successfully")
            print(f"  Name: {data.get('data', {}).get('full_name')}")
            print(f"  Email: {data.get('data', {}).get('email')}")
            return True
        else:
            print(f"✗ Failed to get user detail: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def delete_user(self):
        """Test deleting user"""
        if not self.access_token or not self.user_id:
            print("\n✗ No access token or user ID available for delete test")
            return False
            
        print("\n" + "="*50)
        print("DELETING USER...")
        print("="*50)
        
        response = self.session.delete(
            f"{AUTH_URL}users/{self.user_id}/",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        if response.status_code == 200 or response.status_code == 204:
            print(f"✓ User deleted successfully")
            self.user_id = None
            return True
        else:
            print(f"✗ Failed to delete user: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def run_auth_tests(self):
        """Run all authentication tests"""
        print("\n" + "#"*60)
        print("# AUTHENTICATION MODULE TESTS")
        print("#"*60)
        
        # First register and login
        if not self.register_and_login():
            return []
        
        tests = [
            ("Get Profile", self.get_profile),
            ("Update Profile", self.update_profile),
            ("Change Password", self.change_password),
            ("Refresh Token", self.refresh_token),
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
    
    def run_user_tests(self):
        """Run all user management tests"""
        print("\n" + "#"*60)
        print("# USER MANAGEMENT TESTS")
        print("#"*60)
        
        tests = [
            ("List Users", self.list_users),
            ("Get User Detail", self.get_user_detail),
            ("Delete User", self.delete_user),
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
        print("# ACCOUNTS (AUTHENTICATION) MODULE API TEST SCRIPTS")
        print("#"*60)
        
        # Run authentication tests (includes register and login)
        auth_results = self.run_auth_tests()
        
        # Run user management tests
        user_results = self.run_user_tests()
        
        # Summary
        print("\n" + "#"*60)
        print("# TEST SUMMARY")
        print("#"*60)
        
        all_results = auth_results + user_results
        passed = sum(1 for _, result in all_results if result)
        total = len(all_results)
        
        print("\n--- Authentication Module ---")
        for name, result in auth_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {name}")
        
        print("\n--- User Management Module ---")
        for name, result in user_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return passed == total


def main():
    """Main function"""
    tester = AccountsAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
