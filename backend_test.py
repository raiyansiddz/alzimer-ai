import requests
import sys
import json
from datetime import datetime
import time

class AlzheimerAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.session_id = None
        self.test_email = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:200]}"
                
                self.log_test(name, False, error_msg)
                return False, {}

        except requests.exceptions.RequestException as e:
            self.log_test(name, False, f"Request error: {str(e)}")
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Unexpected error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health endpoint"""
        return self.run_test("Health Check", "GET", "api/health", 200)

    def test_user_registration(self):
        """Test user registration"""
        test_user_data = {
            "email": f"test_user_{int(time.time())}@example.com",
            "name": "Test User",
            "age": 65,
            "education_level": "graduate",
            "vision_type": "normal",
            "language": "en"
        }
        
        success, response = self.run_test(
            "User Registration", 
            "POST", 
            "api/auth/register", 
            200, 
            test_user_data
        )
        
        if success and 'id' in response:
            self.user_id = response.get('id')
            self.test_email = test_user_data['email']  # Store for login
            return True
        return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        if not hasattr(self, 'test_email'):
            self.test_email = "test@example.com"
            
        login_data = {
            "email": self.test_email
        }
        
        success, response = self.run_test(
            "User Login", 
            "POST", 
            "api/auth/login", 
            200, 
            login_data
        )
        
        if success and 'id' in response:
            self.user_id = response.get('id')
            return True
        return False

    def test_create_test_session(self):
        """Test creating a test session"""
        if not self.user_id:
            self.log_test("Create Test Session", False, "No user ID available")
            return False
            
        session_data = {
            "user_id": self.user_id,
            "session_type": "comprehensive",
            "notes": "Automated test session"
        }
        
        success, response = self.run_test(
            "Create Test Session",
            "POST",
            "api/test-sessions/",
            200,
            session_data
        )
        
        if success and 'id' in response:
            self.session_id = response['id']
            return True
        return False

    def test_available_cognitive_tests(self):
        """Test getting available cognitive tests"""
        return self.run_test(
            "Available Cognitive Tests",
            "GET",
            "api/cognitive-tests/tests/available",
            200
        )

    def test_submit_cognitive_test(self):
        """Test submitting a cognitive test"""
        if not self.session_id:
            self.log_test("Submit Cognitive Test", False, "No session ID available")
            return False
            
        test_data = {
            "session_id": self.session_id,
            "test_name": "MMSE Test",
            "test_type": "mmse",
            "test_data": {
                "orientation_score": 8,
                "registration_score": 3,
                "attention_score": 4,
                "recall_score": 2,
                "language_score": 7,
                "total_score": 24
            },
            "response_times": [2.5, 3.1, 1.8, 4.2],
            "user_notes": "Test completed successfully",
            "risk_level": "low"
        }
        
        return self.run_test(
            "Submit Cognitive Test",
            "POST",
            "api/cognitive-tests/enhanced/submit",
            200,
            test_data
        )

    def test_speech_tests_available(self):
        """Test getting available speech tests"""
        return self.run_test(
            "Available Speech Tests",
            "GET",
            "api/speech-tests/tests/prompts",
            200
        )

    def test_get_user_profile(self):
        """Test getting user profile"""
        if not self.user_id:
            self.log_test("Get User Profile", False, "No user ID available")
            return False
            
        return self.run_test(
            "Get User Profile",
            "GET",
            f"api/users/preferences/{self.user_id}",
            200
        )

    def test_get_test_sessions(self):
        """Test getting user's test sessions"""
        if not self.user_id:
            self.log_test("Get Test Sessions", False, "No user ID available")
            return False
            
        return self.run_test(
            "Get Test Sessions",
            "GET",
            f"api/test-sessions/user/{self.user_id}",
            200
        )

    def test_get_reports(self):
        """Test getting user reports"""
        if not self.user_id:
            self.log_test("Get Reports", False, "No user ID available")
            return False
            
        return self.run_test(
            "Get Reports",
            "GET",
            f"api/reports/user/{self.user_id}",
            200
        )

    def run_comprehensive_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Alzheimer's AI Application Backend Tests")
        print("=" * 60)
        
        # Basic connectivity
        success, _ = self.test_health_check()
        if not success:
            print("❌ Health check failed - backend may not be running")
            return False
            
        # Authentication tests
        print("\n📝 Testing Authentication...")
        if not self.test_user_registration():
            print("⚠️  Registration failed, trying login with existing user...")
            if not self.test_user_login():
                print("❌ Both registration and login failed")
                return False
        
        # Core functionality tests
        print("\n🧠 Testing Core Functionality...")
        self.test_create_test_session()
        self.test_available_cognitive_tests()
        self.test_submit_cognitive_test()
        self.test_speech_tests_available()
        
        # User data tests
        print("\n👤 Testing User Data...")
        self.test_get_user_profile()
        self.test_get_test_sessions()
        self.test_get_reports()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_run - self.tests_passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['name']}: {result['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = AlzheimerAPITester()
    
    try:
        success = tester.run_comprehensive_tests()
        all_passed = tester.print_summary()
        
        # Save results to file
        with open('/app/test_reports/backend_test_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_tests': tester.tests_run,
                'passed_tests': tester.tests_passed,
                'success_rate': (tester.tests_passed/tester.tests_run)*100 if tester.tests_run > 0 else 0,
                'detailed_results': tester.test_results
            }, f, indent=2)
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())