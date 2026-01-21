# Copyright (c) 2024
# License: MIT

"""
Verification script to check if APM is working correctly
Run this in bench console to diagnose issues
"""

import logging

logger = logging.getLogger(__name__)


def verify_apm_setup():
	"""
	Verify APM setup and print diagnostic information
	"""
	print("=" * 60)
	print("ERPNext APM Verification")
	print("=" * 60)
	
	# 1. Check environment variables
	print("\n1. Environment Variables:")
	import os
	service_name = os.getenv("ELASTIC_APM_SERVICE_NAME")
	server_url = os.getenv("ELASTIC_APM_SERVER_URL")
	environment = os.getenv("ELASTIC_APM_ENVIRONMENT")
	enabled = os.getenv("ELASTIC_APM_ENABLED", "true")
	
	print(f"   ELASTIC_APM_SERVICE_NAME: {service_name}")
	print(f"   ELASTIC_APM_SERVER_URL: {server_url}")
	print(f"   ELASTIC_APM_ENVIRONMENT: {environment}")
	print(f"   ELASTIC_APM_ENABLED: {enabled}")
	
	# 2. Check if APM client is initialized
	print("\n2. APM Client Status:")
	try:
		from erpnext_apm.apm import get_client, is_apm_enabled
		
		enabled_status = is_apm_enabled()
		print(f"   APM Enabled: {enabled_status}")
		
		client = get_client()
		if client:
			print(f"   ✓ APM Client: {client}")
			print(f"   Service Name: {client.config.service_name}")
			print(f"   Server URL: {client.config.server_url}")
			print(f"   Environment: {getattr(client.config, 'environment', 'not set')}")
		else:
			print("   ✗ APM Client: None (not initialized)")
	except Exception as e:
		print(f"   ✗ Error checking client: {e}")
	
	# 3. Check WSGI wrapping
	print("\n3. WSGI Application Wrapping:")
	try:
		import frappe.app as frappe_app
		
		if hasattr(frappe_app, "application"):
			app_type = type(frappe_app.application).__name__
			print(f"   Application type: {app_type}")
			
			# Check if wrapped
			if "ElasticAPM" in str(app_type) or "elasticapm" in str(type(frappe_app.application)).lower():
				print("   ✓ WSGI application is wrapped with Elastic APM")
			else:
				print("   ✗ WSGI application is NOT wrapped")
				print(f"   Application: {frappe_app.application}")
		else:
			print("   ✗ frappe.app.application not found")
	except Exception as e:
		print(f"   ✗ Error checking WSGI: {e}")
	
	# 4. Test transaction capture
	print("\n4. Transaction Capture Test:")
	try:
		from erpnext_apm.apm import get_client
		client = get_client()
		
		if client:
			# Try to start a transaction
			transaction = client.begin_transaction("test", "test")
			if transaction:
				print("   ✓ Can create transactions")
				client.end_transaction("test", "ok")
			else:
				print("   ✗ Cannot create transactions")
		else:
			print("   ✗ No client available for testing")
	except Exception as e:
		print(f"   ✗ Error testing transactions: {e}")
	
	# 5. Check if elastic-apm is installed
	print("\n5. Package Installation:")
	try:
		import elasticapm
		version = getattr(elasticapm, '__version__', 'unknown')
		print(f"   ✓ elastic-apm installed: {version}")
	except ImportError:
		print("   ✗ elastic-apm not installed")
	
	# 6. Try to manually initialize
	print("\n6. Manual Initialization Test:")
	try:
		from erpnext_apm.apm import init_apm, get_client
		client = init_apm()
		if client:
			print(f"   ✓ Manual init successful: {client}")
			print(f"   Service: {client.config.service_name}")
			print(f"   Server: {client.config.server_url}")
		else:
			print("   ✗ Manual init returned None")
			print("   Check environment variables and error logs")
	except Exception as e:
		print(f"   ✗ Manual init failed: {e}")
		import traceback
		traceback.print_exc()
	
	print("\n" + "=" * 60)
	print("Verification Complete")
	print("=" * 60)
	
	# Recommendations
	print("\nRecommendations:")
	if not service_name or not server_url:
		print("  - Set ELASTIC_APM_SERVICE_NAME and ELASTIC_APM_SERVER_URL")
	
	client = get_client() if 'get_client' in locals() else None
	if not client:
		print("  - APM client not initialized - check logs for errors")
	
	try:
		import frappe.app as frappe_app
		if hasattr(frappe_app, "application"):
			app_type = type(frappe_app.application).__name__
			if "ElasticAPM" not in str(app_type):
				print("  - WSGI application not wrapped - restart services or run bench migrate")
	except:
		pass

