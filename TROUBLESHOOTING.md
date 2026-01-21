# Troubleshooting: APM Not Working

## Problem

APM is installed and environment variables are set, but it's not reporting data.

## Root Cause

The `after_migrate` hook only runs during `bench migrate`, not on every request. This means APM might not initialize until a migration runs.

## Solution Applied

The code has been updated to initialize APM at module import time (similar to how Sentry works), ensuring it wraps the WSGI application early.

## Steps to Fix

### Option 1: Run Migration (Quick Fix)

```bash
bench --site erp.localhost migrate
```

This will trigger the `after_migrate` hook and initialize APM.

### Option 2: Restart Services (Recommended)

```bash
bench restart
```

The new code will automatically initialize APM when hooks are loaded.

### Option 3: Verify Setup

After restarting, check if APM is working:

```bash
bench --site erp.localhost console
```

```python
# Check if APM client is initialized
from erpnext_apm.apm import get_client
client = get_client()
print(f"APM Client: {client}")

# Check if WSGI is wrapped
import frappe.app as frappe_app
print(f"Application type: {type(frappe_app.application)}")
# Should show ElasticAPM if working
```

## Check Logs

```bash
# Site-specific logs
tail -f sites/erp.localhost/logs/*.log | grep -i apm

# Or bench logs (if available)
tail -f logs/web.log | grep -i apm
```

## Expected Log Messages

You should see:
- `"Elastic APM initialized: service=erpnext-prod, server=..."`
- `"Frappe WSGI application wrapped with Elastic APM middleware"`
- `"APM instrumentation setup complete - WSGI application wrapped"`

## Verification Checklist

- [ ] Environment variables are set (`ELASTIC_APM_SERVICE_NAME`, `ELASTIC_APM_SERVER_URL`)
- [ ] `elastic-apm` package is installed (`bench pip list | grep elastic-apm`)
- [ ] App is installed (`bench --site erp.localhost list-apps | grep erpnext_apm`)
- [ ] Services have been restarted after code update
- [ ] Logs show APM initialization messages
- [ ] APM client is not None in console

## If Still Not Working

1. **Manually trigger setup:**
   ```python
   from erpnext_apm.startup import setup_apm
   setup_apm()
   ```

2. **Check environment variables in Python:**
   ```python
   import os
   print("SERVICE_NAME:", os.getenv('ELASTIC_APM_SERVICE_NAME'))
   print("SERVER_URL:", os.getenv('ELASTIC_APM_SERVER_URL'))
   print("ENABLED:", os.getenv('ELASTIC_APM_ENABLED', 'true'))
   ```

3. **Verify APM server connectivity:**
   ```bash
   curl http://apm.elasticsearch.svc:8200
   # Should return some response (even if error)
   ```

4. **Check for errors in logs:**
   ```bash
   grep -i "error\|exception\|fail" sites/erp.localhost/logs/*.log | grep -i apm
   ```

## Code Changes Made

1. **Added `monkey_patch.py`**: Wraps application at module import time
2. **Updated `hooks.py`**: Imports monkey_patch to trigger early initialization
3. **Updated `startup.py`**: Also tries to setup at import time as fallback

The app now uses a dual approach:
- Early initialization via module import (monkey_patch)
- Fallback via after_migrate hook

This ensures APM initializes regardless of when migrations run.

