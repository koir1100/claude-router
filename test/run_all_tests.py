#!/usr/bin/env python3
"""
Claude Router Comprehensive Test Runner
Runs all Claude Code tools tests and generates detailed reports
"""
import sys
import time
import subprocess
import requests
from pathlib import Path
import json
from datetime import datetime

class ClaudeRouterTestRunner:
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.router_url = "http://localhost:4000"
        self.results = {}
        self.start_time = None
        self.end_time = None
        
    def check_router_health(self):
        """Verify Claude Router is running and healthy"""
        print("🔍 Checking Claude Router health...")
        try:
            response = requests.get(f"{self.router_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("status") == "ok":
                    print(f"✅ Router healthy - Model: {health_data.get('model', 'unknown')}")
                    return True
            print(f"❌ Router health check failed - Status: {response.status_code}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Router connection failed: {e}")
            return False
    
    def run_test_file(self, test_file):
        """Run a single test file and capture results"""
        test_name = test_file.stem
        print(f"\n🧪 Running {test_name}...")
        
        try:
            start_time = time.time()
            result = subprocess.run([
                sys.executable, str(test_file)
            ], 
            capture_output=True, 
            text=True, 
            timeout=120,  # 2 minute timeout per test file
            cwd=self.test_dir.parent
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.results[test_name] = {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
            if result.returncode == 0:
                print(f"✅ {test_name} PASSED ({duration:.2f}s)")
            else:
                print(f"❌ {test_name} FAILED ({duration:.2f}s)")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
                    
        except subprocess.TimeoutExpired:
            self.results[test_name] = {
                "status": "TIMEOUT",
                "duration": 120.0,
                "stdout": "",
                "stderr": "Test timed out after 120 seconds",
                "return_code": -1
            }
            print(f"⏰ {test_name} TIMEOUT (120.0s)")
            
        except Exception as e:
            self.results[test_name] = {
                "status": "ERROR",
                "duration": 0.0,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }
            print(f"💥 {test_name} ERROR: {e}")
    
    def run_all_tests(self):
        """Run all test files in the test directory"""
        test_files = [
            "test_claude_tools_comprehensive.py",
            "test_file_operations.py",
            "test_execution_tools.py", 
            "test_search_tools.py",
            "test_web_tools.py",
            "test_notebook_and_ide_tools.py",
            "test_task_management_tools.py"
        ]
        
        print("🚀 Starting Claude Router comprehensive test suite...")
        self.start_time = datetime.now()
        
        # Check router health first
        if not self.check_router_health():
            print("\n❌ Router health check failed. Please ensure Claude Router is running.")
            print("   Run: ./run.sh")
            return False
        
        # Run each test file
        for test_file_name in test_files:
            test_file = self.test_dir / test_file_name
            if test_file.exists():
                self.run_test_file(test_file)
            else:
                print(f"⚠️  Test file not found: {test_file_name}")
                self.results[test_file_name.replace('.py', '')] = {
                    "status": "NOT_FOUND",
                    "duration": 0.0,
                    "stdout": "",
                    "stderr": f"Test file {test_file_name} not found",
                    "return_code": -1
                }
        
        self.end_time = datetime.now()
        return True
    
    def generate_report(self):
        """Generate comprehensive test report"""
        if not self.results:
            print("No test results to report")
            return
            
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        # Count results by status
        passed = sum(1 for r in self.results.values() if r["status"] == "PASSED")
        failed = sum(1 for r in self.results.values() if r["status"] == "FAILED") 
        timeout = sum(1 for r in self.results.values() if r["status"] == "TIMEOUT")
        error = sum(1 for r in self.results.values() if r["status"] == "ERROR")
        not_found = sum(1 for r in self.results.values() if r["status"] == "NOT_FOUND")
        
        total_tests = len(self.results)
        
        print(f"\n{'='*60}")
        print(f"📊 CLAUDE ROUTER TEST RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"🕐 Total Runtime: {total_duration:.2f}s")
        print(f"📁 Total Test Suites: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏰ Timeout: {timeout}")
        print(f"💥 Error: {error}")
        print(f"🔍 Not Found: {not_found}")
        print(f"📈 Success Rate: {(passed/total_tests)*100:.1f}%")
        
        print(f"\n{'='*60}")
        print(f"📋 DETAILED RESULTS")
        print(f"{'='*60}")
        
        for test_name, result in self.results.items():
            status_emoji = {
                "PASSED": "✅",
                "FAILED": "❌", 
                "TIMEOUT": "⏰",
                "ERROR": "💥",
                "NOT_FOUND": "🔍"
            }.get(result["status"], "❓")
            
            print(f"{status_emoji} {test_name:<35} {result['status']:<10} ({result['duration']:.2f}s)")
            
            if result["status"] in ["FAILED", "ERROR", "TIMEOUT"] and result["stderr"]:
                print(f"   └─ {result['stderr'].strip()}")
        
        # Show failed test details
        failed_tests = {name: result for name, result in self.results.items() 
                       if result["status"] in ["FAILED", "ERROR", "TIMEOUT"]}
        
        if failed_tests:
            print(f"\n{'='*60}")
            print(f"🔍 FAILED TESTS ANALYSIS")
            print(f"{'='*60}")
            
            for test_name, result in failed_tests.items():
                print(f"\n❌ {test_name}:")
                print(f"   Status: {result['status']}")
                print(f"   Duration: {result['duration']:.2f}s")
                if result['stderr']:
                    print(f"   Error: {result['stderr'].strip()}")
                if result['stdout']:
                    print(f"   Output: {result['stdout'].strip()}")
        
        # Save detailed report to file
        report_data = {
            "timestamp": self.start_time.isoformat(),
            "total_duration": total_duration,
            "summary": {
                "total": total_tests,
                "passed": passed,
                "failed": failed,
                "timeout": timeout,
                "error": error,
                "not_found": not_found,
                "success_rate": (passed/total_tests)*100
            },
            "results": self.results
        }
        
        report_file = self.test_dir / "test_results.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        # Return overall success
        return failed + timeout + error == 0

def main():
    """Main test runner entry point"""
    runner = ClaudeRouterTestRunner()
    
    print("🧪 Claude Router Comprehensive Test Suite")
    print("=" * 50)
    
    success = runner.run_all_tests()
    if success:
        overall_success = runner.generate_report()
        
        if overall_success:
            print("\n🎉 All tests passed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Check the report above for details.")
            sys.exit(1)
    else:
        print("\n💥 Test execution failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()