#!/usr/bin/env python3
"""
API Validation Script for PlsFindMeAJob Application
Tests all API endpoints to ensure behavior remains consistent during refactoring.
"""
import requests
import json
import time
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestResult:
    """Container for test results."""
    name: str
    passed: bool
    message: str
    response_time: float
    response_data: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None


class APIValidator:
    """Comprehensive API validation for the PlsFindMeAJob application."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results: List[TestResult] = []
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with timing."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except Exception as e:
            # Create a mock response for connection errors
            mock_response = requests.Response()
            mock_response.status_code = 0
            mock_response._content = json.dumps({"error": str(e)}).encode()
            return mock_response
    
    def _record_test(self, name: str, response: requests.Response, 
                     expected_status: int = 200, 
                     expected_keys: Optional[List[str]] = None,
                     custom_validator: Optional[callable] = None) -> TestResult:
        """Record test result with comprehensive validation."""
        
        response_time = getattr(response, 'elapsed', 0)
        if hasattr(response_time, 'total_seconds'):
            response_time = response_time.total_seconds()
        else:
            response_time = 0
        
        # Check if server is reachable
        if response.status_code == 0:
            result = TestResult(
                name=name,
                passed=False,
                message="Server unreachable",
                response_time=response_time,
                error_details="Connection failed"
            )
            self.test_results.append(result)
            return result
        
        # Parse response
        try:
            response_data = response.json() if response.content else {}
        except json.JSONDecodeError:
            response_data = {"raw_content": response.text[:200]}
        
        # Validate status code
        status_ok = response.status_code == expected_status
        
        # Validate expected keys
        keys_ok = True
        if expected_keys and isinstance(response_data, dict):
            missing_keys = [key for key in expected_keys if key not in response_data]
            keys_ok = len(missing_keys) == 0
        
        # Custom validation
        custom_ok = True
        custom_message = ""
        if custom_validator:
            try:
                custom_ok, custom_message = custom_validator(response_data)
            except Exception as e:
                custom_ok = False
                custom_message = f"Custom validator error: {str(e)}"
        
        # Determine overall result
        passed = status_ok and keys_ok and custom_ok
        
        # Build message
        message_parts = []
        if not status_ok:
            message_parts.append(f"Status: {response.status_code} (expected {expected_status})")
        if not keys_ok and expected_keys:
            message_parts.append(f"Missing keys: {missing_keys}")
        if not custom_ok:
            message_parts.append(f"Custom validation: {custom_message}")
        
        message = "PASS" if passed else "; ".join(message_parts)
        
        result = TestResult(
            name=name,
            passed=passed,
            message=message,
            response_time=response_time,
            response_data=response_data,
            error_details=None if passed else str(response_data)
        )
        
        self.test_results.append(result)
        return result
    
    def test_root_endpoint(self) -> TestResult:
        """Test GET / endpoint."""
        response = self._make_request("GET", "/")
        
        def validate_root(data):
            return "message" in data, "Missing welcome message"
        
        return self._record_test(
            "Root Endpoint", 
            response,
            expected_keys=["message"],
            custom_validator=validate_root
        )
    
    def test_profile_get(self) -> TestResult:
        """Test GET /api/profile endpoint."""
        response = self._make_request("GET", "/api/profile")
        
        def validate_profile_structure(data):
            required_fields = ["basics", "experiences", "education", "skills", "projects"]
            missing = [field for field in required_fields if field not in data]
            
            if missing:
                return False, f"Missing profile fields: {missing}"
            
            # Validate basics structure
            basics = data.get("basics", {})
            basics_fields = ["name", "email", "phone"]
            missing_basics = [field for field in basics_fields if field not in basics]
            
            if missing_basics:
                return False, f"Missing basics fields: {missing_basics}"
            
            return True, "Profile structure valid"
        
        return self._record_test(
            "Profile GET", 
            response,
            expected_keys=["basics", "experiences", "education", "skills", "projects"],
            custom_validator=validate_profile_structure
        )
    
    def test_profile_save_valid(self) -> TestResult:
        """Test POST /api/profile with valid data."""
        
        # Create valid test profile
        test_profile = {
            "basics": {
                "name": "Test User",
                "email": "test@example.com", 
                "phone": "123-456-7890",
                "linkedin": "https://linkedin.com/in/testuser",
                "github": "https://github.com/testuser"
            },
            "skills": ["Python", "FastAPI", "React"],
            "experiences": [
                {
                    "company": "Test Company",
                    "position": "Software Engineer",
                    "start_date": "2023-01-01",
                    "end_date": "2024-01-01",
                    "location": "Remote",
                    "bullets": ["Developed APIs", "Built frontend"]
                }
            ],
            "education": [
                {
                    "institution": "Test University",
                    "location": "Test City",
                    "degree": "BS Computer Science",
                    "expected_date": "2024-05-01",
                    "start_date": "2020-08-01",
                    "coursework": "Data Structures, Algorithms"
                }
            ],
            "projects": [
                {
                    "name": "Test Project",
                    "description": "A test project for validation"
                }
            ]
        }
        
        response = self._make_request("POST", "/api/profile", json=test_profile)
        
        def validate_save_response(data):
            if not data.get("success"):
                return False, f"Save failed: {data.get('message', 'Unknown error')}"
            return True, "Save successful"
        
        return self._record_test(
            "Profile Save Valid", 
            response,
            expected_keys=["success", "message"],
            custom_validator=validate_save_response
        )
    
    def test_profile_save_invalid(self) -> TestResult:
        """Test POST /api/profile with invalid data (validation errors)."""
        
        # Create invalid test profile (missing required fields)
        invalid_profile = {
            "basics": {
                "name": "",  # Empty name
                "email": "invalid-email",  # Invalid email format
                "phone": "123"
            },
            "skills": [],  # Empty skills
            "experiences": [],  # Empty experiences  
            "education": []  # Empty education
        }
        
        response = self._make_request("POST", "/api/profile", json=invalid_profile)
        
        def validate_error_response(data):
            # Should be a 422 error with validation details
            if not isinstance(data, dict):
                return False, "Response should be dict for validation errors"
            
            # Check for FastAPI validation error structure
            if "detail" in data:
                detail = data["detail"]
                if isinstance(detail, dict) and "errors" in detail:
                    return True, "Validation errors properly returned"
            
            return True, "Error response received (format may vary)"
        
        return self._record_test(
            "Profile Save Invalid",
            response, 
            expected_status=422,  # Validation error status
            custom_validator=validate_error_response
        )
    
    def test_jobs_get(self) -> TestResult:
        """Test GET /api/jobs endpoint."""
        response = self._make_request("GET", "/api/jobs")
        
        def validate_jobs_response(data):
            if "total" not in data:
                return False, "Missing 'total' field"
            if "data" not in data:
                return False, "Missing 'data' field"
            
            total = data.get("total", 0)
            jobs_data = data.get("data", [])
            
            if not isinstance(total, int):
                return False, "Total should be integer"
            if not isinstance(jobs_data, list):
                return False, "Data should be list"
            
            return True, f"Jobs response valid (total: {total}, items: {len(jobs_data)})"
        
        return self._record_test(
            "Jobs GET",
            response,
            expected_keys=["total", "data"],
            custom_validator=validate_jobs_response
        )
    
    def test_jobs_pagination(self) -> TestResult:
        """Test GET /api/jobs with pagination parameters."""
        response = self._make_request("GET", "/api/jobs?skip=0&limit=5")
        
        def validate_pagination(data):
            jobs_data = data.get("data", [])
            if len(jobs_data) > 5:
                return False, f"Returned {len(jobs_data)} items, expected max 5"
            return True, f"Pagination working ({len(jobs_data)} items returned)"
        
        return self._record_test(
            "Jobs Pagination",
            response,
            expected_keys=["total", "data"],
            custom_validator=validate_pagination
        )
    
    def run_all_tests(self) -> bool:
        """Run all validation tests."""
        print("🧪 Starting API Validation Tests...")
        print("-" * 50)
        
        # Run all tests
        test_methods = [
            self.test_root_endpoint,
            self.test_profile_get,
            self.test_profile_save_valid,
            self.test_profile_save_invalid,
            self.test_jobs_get,
            self.test_jobs_pagination,
        ]
        
        for test_method in test_methods:
            try:
                result = test_method()
                status_icon = "✅" if result.passed else "❌"
                print(f"{status_icon} {result.name}: {result.message}")
                if result.response_time > 0:
                    print(f"   Response time: {result.response_time:.3f}s")
                if not result.passed and result.error_details:
                    print(f"   Details: {result.error_details[:200]}...")
            except Exception as e:
                print(f"❌ {test_method.__name__}: Test failed with exception: {str(e)}")
                self.test_results.append(TestResult(
                    name=test_method.__name__,
                    passed=False,
                    message=f"Test exception: {str(e)}",
                    response_time=0
                ))
            
            print()
        
        # Summary
        passed_tests = sum(1 for result in self.test_results if result.passed)
        total_tests = len(self.test_results)
        
        print("-" * 50)
        print(f"📊 Test Summary: {passed_tests}/{total_tests} passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! API is working correctly.")
            return True
        else:
            failed_tests = [r.name for r in self.test_results if not r.passed]
            print(f"💥 Failed tests: {', '.join(failed_tests)}")
            return False
    
    def save_results(self, filename: str = "validation_results.json"):
        """Save test results to JSON file."""
        results_data = {
            "timestamp": time.time(),
            "summary": {
                "total_tests": len(self.test_results),
                "passed_tests": sum(1 for r in self.test_results if r.passed),
                "failed_tests": sum(1 for r in self.test_results if not r.passed)
            },
            "tests": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "response_time": r.response_time,
                    "error_details": r.error_details
                }
                for r in self.test_results
            ]
        }
        
        with open(filename, "w") as f:
            json.dump(results_data, f, indent=2)
        
        print(f"📄 Results saved to {filename}")


def main():
    """Main function to run validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate PlsFindMeAJob API")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL for API (default: http://localhost:8000)")
    parser.add_argument("--save", default="validation_results.json",
                       help="File to save results (default: validation_results.json)")
    
    args = parser.parse_args()
    
    validator = APIValidator(args.url)
    
    try:
        success = validator.run_all_tests()
        validator.save_results(args.save)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()