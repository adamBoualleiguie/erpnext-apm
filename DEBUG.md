# Debugging APM Not Working

## Issue: APM not initializing/reporting

The `after_migrate` hook only runs during `bench migrate`, not on every request. We need to ensure APM initializes earlier.

## Solution Applied

Updated the code to initialize APM at module import time (similar to how Sentry works in Frappe).

## Steps to Fix

1. **Run a migration to trigger the hook:**
   ```bash
   bench --site erp.localhost migrate
   ```

2. **Or restart services** (the new code will initialize on import):
   ```bash
   bench restart
   ```

3. **Check logs:**
   ```bash
   # Check site-specific logs
   tail -f sites/erp.localhost/logs/*.log | grep -i apm
   
   # Or check bench logs
   tail -f logs/web.log | grep -i apm
   ```

4. **Verify in console:**
   ```bash
   bench --site erp.localhost console
   ```
   ```python
   import frappe.app as frappe_app
   print(type(frappe_app.application))
   # Should show ElasticAPM wrapper if working
   
   from erpnext_apm.apm import get_client
   client = get_client()
   print(f"APM Client: {client}")
   ```

## Expected Log Messages

You should see:
- "Elastic APM initialized: service=erpnext-prod, server=..."
- "Frappe WSGI application wrapped with Elastic APM middleware"
- "APM instrumentation setup complete - WSGI application wrapped"

## If Still Not Working

1. **Check environment variables are accessible:**
   ```python
   import os
   print(os.getenv('ELASTIC_APM_SERVICE_NAME'))
   print(os.getenv('ELASTIC_APM_SERVER_URL'))
   ```

2. **Manually trigger setup:**
   ```python
   from erpnext_apm.startup import setup_apm
   setup_apm()
   ```

3. **Check if elastic-apm is installed:**
   ```bash
   bench pip list | grep elastic-apm
   ```

4. **Verify the app is installed:**
   ```bash
   bench --site erp.localhost list-apps | grep erpnext_apm
   ```

