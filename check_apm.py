#!/usr/bin/env python3
"""
Quick APM status check script

Run this in your gunicorn pod to verify APM is working:
    bench --site erp.localhost execute erpnext_apm.check_apm.check_status
"""

import frappe


def check_status():
	"""Check APM status and print results"""
	print("=" * 60)
	print("ERPNext APM Status Check")
	print("=" * 60)
	
	# 1. Check environment variables
	print("\n1. Environment Variables:")
	import os
	env_vars = [
		"ELASTIC_APM_SERVICE_NAME",
		"ELASTIC_APM_SERVER_URL",
		"ELASTIC_APM_ENABLED",
		"ELASTIC_APM_ENVIRONMENT",
	]
	for var in env_vars:
		value = os.getenv(var, "NOT SET")
		print(f"   {var}: {value}")
	
	# 2. Check APM client
	print("\n2. APM Client:")
	try:
		from erpnext_apm.apm import get_client, init_apm, is_apm_enabled
		
		enabled = is_apm_enabled()
		print(f"   APM Enabled: {enabled}")
		
		client = get_client()
		if not client:
			print("   Client: None - attempting initialization...")
			client = init_apm(force=True)
		
		if client:
			print(f"   ✓ Client: Initialized")
			print(f"   Service: {client.config.service_name}")
			print(f"   Server: {client.config.server_url}")
		else:
			print("   ✗ Client: None (not initialized)")
	except Exception as e:
		print(f"   ✗ Error: {e}")
		import traceback
		traceback.print_exc()
	
	# 3. Check WSGI wrapping (only relevant in gunicorn pod)
	print("\n3. WSGI Application Wrapping:")
	try:
		import frappe.app as frappe_app
		
		if hasattr(frappe_app, "application"):
			app_type = type(frappe_app.application)
			print(f"   Application type: {app_type}")
			
			if "ElasticAPMWSGI" in str(app_type):
				print("   ✓ WSGI application is wrapped with Elastic APM")
			else:
				print("   ✗ WSGI application is NOT wrapped")
				print(f"   (This is OK in worker pods - only gunicorn needs wrapping)")
				
				# Try to wrap it
				print("   Attempting to wrap now...")
				try:
					from erpnext_apm.app_patcher import patch_application
					patch_application()
					
					# Check again
					app_type = type(frappe_app.application)
					if "ElasticAPMWSGI" in str(app_type):
						print("   ✓ Successfully wrapped!")
					else:
						print("   ✗ Wrapping failed")
				except Exception as e:
					print(f"   ✗ Wrapping error: {e}")
		else:
			print("   ✗ frappe.app.application not found")
	except Exception as e:
		print(f"   ✗ Error: {e}")
		import traceback
		traceback.print_exc()
	
	# 4. Package check
	print("\n4. Package Installation:")
	try:
		import elasticapm
		version = getattr(elasticapm, 'VERSION', getattr(elasticapm, '__version__', 'unknown'))
		print(f"   ✓ elastic-apm installed: {version}")
	except ImportError:
		print("   ✗ elastic-apm not installed")
	
	print("\n" + "=" * 60)
	print("Check complete!")
	print("=" * 60)

