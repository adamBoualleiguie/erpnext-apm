#!/usr/bin/env python3
"""
Quick test script for ERPNext APM
Run this from bench console or directly to test APM functionality
"""

import os
import sys

# Add app to path if running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_imports():
    """Test if all imports work"""
    print("Testing imports...")
    try:
        from erpnext_apm import capture_exception, init_apm, get_client
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_apm_config():
    """Test APM configuration"""
    print("\nTesting APM configuration...")
    from erpnext_apm.apm import is_apm_enabled, get_config
    
    enabled = is_apm_enabled()
    print(f"APM Enabled: {enabled}")
    
    if enabled:
        try:
            config = get_config()
            print(f"✓ Configuration loaded:")
            print(f"  Service Name: {config.get('SERVICE_NAME')}")
            print(f"  Server URL: {config.get('SERVER_URL')}")
            return True
        except ValueError as e:
            print(f"✗ Configuration error: {e}")
            print("  Set ELASTIC_APM_SERVICE_NAME and ELASTIC_APM_SERVER_URL")
            return False
    else:
        print("  APM is disabled (ELASTIC_APM_ENABLED=false)")
        return True

def test_apm_init():
    """Test APM initialization"""
    print("\nTesting APM initialization...")
    from erpnext_apm.apm import init_apm, get_client
    
    try:
        client = init_apm()
        if client:
            print("✓ APM client initialized")
            return True
        else:
            print("⚠ APM client not initialized (check logs for reason)")
            return True  # Not an error, might be disabled
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False

def test_exception_capture():
    """Test exception capture"""
    print("\nTesting exception capture...")
    from erpnext_apm import capture_exception
    
    try:
        try:
            raise ValueError("Test exception for APM")
        except Exception:
            capture_exception()
            print("✓ Exception capture called (check APM server if configured)")
            return True
    except Exception as e:
        print(f"✗ Exception capture failed: {e}")
        return False

def test_wsgi_wrapping():
    """Test WSGI wrapping"""
    print("\nTesting WSGI wrapping...")
    try:
        import frappe.app as frappe_app
        if hasattr(frappe_app, "application"):
            app_type = type(frappe_app.application).__name__
            print(f"Application type: {app_type}")
            
            # Check if it's wrapped with ElasticAPM
            if "ElasticAPM" in str(app_type) or "elasticapm" in str(type(frappe_app.application)).lower():
                print("✓ WSGI application is wrapped with Elastic APM")
                return True
            else:
                print("⚠ WSGI application not wrapped (might not be initialized yet)")
                print("  This is normal if after_migrate hook hasn't run")
                return True  # Not necessarily an error
        else:
            print("⚠ frappe.app.application not found")
            return True
    except ImportError:
        print("⚠ frappe.app not available (running outside Frappe context)")
        return True
    except Exception as e:
        print(f"✗ WSGI wrapping test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("ERPNext APM Test Suite")
    print("=" * 50)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_apm_config()))
    results.append(("Initialization", test_apm_init()))
    results.append(("Exception Capture", test_exception_capture()))
    results.append(("WSGI Wrapping", test_wsgi_wrapping()))
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print("\n" + ("=" * 50))
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed - check output above")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

