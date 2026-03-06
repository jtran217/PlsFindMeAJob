#!/usr/bin/env python3
"""
Test script for OpenAI Client inject_prompt functionality.
Tests the complete workflow of loading templates, schemas, and injecting data.

Usage: python test_inject_prompt.py
"""

import unittest
import json
import sys
import re
import os
from pathlib import Path

# Set test environment variables before importing config
os.environ.setdefault("OPENROUTER_API_KEY", "test-key-for-testing")
os.environ.setdefault("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
os.environ.setdefault("OPENROUTER_MODEL", "test-model")

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.utils.openai_client import OpenAIClient
from app.core.config import settings


class TestInjectPrompt(unittest.TestCase):
    """Test cases for inject_prompt method and workflow."""
    
    def setUp(self):
        """Initialize test fixtures and OpenAI client."""
        self.client = OpenAIClient()
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self.app_dir = Path(__file__).parent.parent / "app"
        
        # Load test data
        self.test_jobs = self._load_test_fixture("fake_job_descriptions.json")
        self.test_profiles = self._load_test_fixture("test_profiles.json")
        self.test_schema = self._load_test_fixture("simple_schema.json")

    def test_inject_prompt_basic(self):
        """Test basic prompt injection functionality with real template."""
        print("\n🧪 Testing basic prompt injection...")
        
        # Load the real resume optimizer prompt
        prompt_path = self.app_dir / "prompts" / "resume_optimizer_prompt.txt"
        prompt_template = self.client.load_prompt(str(prompt_path))
        
        # Prepare test data
        test_data = {
            "job_description": self.test_jobs["software_engineer"]["description"],
            "profile_json": self.test_profiles["complete_profile"],
            "schema": self.test_schema
        }
        
        # Inject data into prompt
        result = self.client.inject_prompt(prompt_template, test_data)
        
        # Verify all placeholders are replaced
        self.assertNotIn("{job_description}", result)
        self.assertNotIn("{profile_json}", result)
        self.assertNotIn("{payload_schema}", result)
        
        # Verify job description content is present  
        job_desc = self.test_jobs["software_engineer"]["description"]
        self.assertIn("Senior Software Engineer", result)
        self.assertIn("React", result)
        
        # Verify profile content is present
        self.assertIn("Alex Developer", result)
        self.assertIn("TechStartup Inc", result)
        
        print("✅ Basic injection test passed")

    def test_inject_prompt_json_formatting(self):
        """Test that JSON data is properly formatted in output."""
        print("\n🧪 Testing JSON formatting...")
        
        # Simple template for focused testing
        template = "Profile: {profile_json}\nSchema: {payload_schema}\nJob: {job_description}"
        
        test_data = {
            "job_description": "Sample job description",
            "profile_json": self.test_profiles["minimal_profile"],
            "schema": {"simple": "schema", "with": ["array"]}
        }
        
        result = self.client.inject_prompt(template, test_data)
        
        # Check that JSON is properly indented (2 spaces)
        lines = result.split('\n')
        profile_section_found = False
        for line in lines:
            if '"basics": {' in line:
                profile_section_found = True
                # Check for 2-space indentation
                self.assertTrue(line.startswith('  "basics"'), 
                              f"Expected 2-space indentation, got: '{line}'")
        
        self.assertTrue(profile_section_found, "Profile JSON section not found")
        
        # Verify JSON is valid by parsing sections
        profile_start = result.find('Profile: ') + len('Profile: ')
        profile_end = result.find('\nSchema:')
        profile_json = result[profile_start:profile_end]
        
        # Should be able to parse as valid JSON
        try:
            parsed_profile = json.loads(profile_json)
            self.assertEqual(parsed_profile["basics"]["name"], "Sam Smith")
        except json.JSONDecodeError as e:
            self.fail(f"Profile JSON is not valid: {e}")
        
        print("✅ JSON formatting test passed")

    def test_full_workflow_realistic(self):
        """Test complete end-to-end workflow with real files and realistic data."""
        print("\n🧪 Testing full workflow end-to-end...")
        
        # Load actual files
        prompt_path = self.app_dir / "prompts" / "resume_optimizer_prompt.txt"
        schema_path = self.app_dir / "models" / "resume_schema.json"
        
        prompt_template = self.client.load_prompt(str(prompt_path))
        
        # Load real schema (handle potential JSON comments)
        try:
            with open(schema_path, 'r') as f:
                schema_content = f.read()
                # Remove comments for valid JSON
                schema_lines = [line for line in schema_content.split('\n') 
                              if not line.strip().startswith('//')]
                clean_schema = '\n'.join(schema_lines)
                real_schema = json.loads(clean_schema)
        except json.JSONDecodeError:
            # Fallback to test schema if real schema has issues
            real_schema = self.test_schema
        
        # Test with different job types and profiles
        test_cases = [
            ("software_engineer", "complete_profile"),
            ("data_scientist", "minimal_profile"),
            ("frontend_developer", "complete_profile")
        ]
        
        for job_type, profile_type in test_cases:
            with self.subTest(job=job_type, profile=profile_type):
                test_data = {
                    "job_description": self.test_jobs[job_type]["description"],
                    "profile_json": self.test_profiles[profile_type],
                    "schema": real_schema
                }
                
                result = self.client.inject_prompt(prompt_template, test_data)
                
                # Verify structure
                self.assertIn("JOB DESCRIPTION", result)
                self.assertIn("CANDIDATE PROFILE JSON", result)
                self.assertIn("REQUIRED OUTPUT FORMAT", result)
                
                # Verify no placeholders remain
                self._assert_no_placeholders(result)
                
                # Verify job-specific content (from job description, not company name)
                job_desc = self.test_jobs[job_type]["description"]
                if "React" in job_desc:
                    self.assertIn("React", result)
                if "Python" in job_desc:
                    self.assertIn("Python", result)
                
                # Verify profile-specific content
                profile_info = self.test_profiles[profile_type]
                self.assertIn(profile_info["basics"]["name"], result)
        
        print("✅ Full workflow test passed")

    def test_inject_prompt_minimal_data(self):
        """Test injection with minimal data to ensure basic functionality."""
        print("\n🧪 Testing minimal data injection...")
        
        simple_template = "Job: {job_description}\nProfile: {profile_json}\nSchema: {payload_schema}"
        
        minimal_data = {
            "job_description": "Simple job description",
            "profile_json": {"name": "Test User"},
            "schema": {"type": "object"}
        }
        
        result = self.client.inject_prompt(simple_template, minimal_data)
        
        # Check all data is present
        self.assertIn("Simple job description", result)
        self.assertIn("Test User", result)
        self.assertIn('"type": "object"', result)
        
        # Verify no placeholders
        self._assert_no_placeholders(result)
        
        print("✅ Minimal data test passed")

    # Helper methods
    def _load_test_fixture(self, filename: str) -> dict:
        """Load JSON test fixture from fixtures directory."""
        fixture_path = self.fixtures_dir / filename
        with open(fixture_path, 'r') as f:
            return json.load(f)

    def _assert_no_placeholders(self, text: str):
        """Assert that no template placeholder patterns remain in the text."""
        # Only look for the specific placeholders used in inject_prompt
        template_placeholders = [
            "{job_description}",
            "{profile_json}",
            "{payload_schema}"
        ]
        
        found_placeholders = []
        for placeholder in template_placeholders:
            if placeholder in text:
                found_placeholders.append(placeholder)
        
        if found_placeholders:
            self.fail(f"Found unreplaced template placeholders: {found_placeholders}")


def main():
    """Run the test suite with detailed output."""
    print("🚀 Starting inject_prompt test suite...")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestInjectPrompt)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 All tests passed! inject_prompt is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        if result.failures:
            print(f"Failures: {len(result.failures)}")
        if result.errors:
            print(f"Errors: {len(result.errors)}")
    
    print(f"Tests run: {result.testsRun}")
    print("=" * 60)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())