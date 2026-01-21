# Testing Guide for ERPNext APM

## Quick Start Testing

### Step 1: Install the App

```bash
cd /workspace/frappe-bench
bench --site devsite.localhost install-app erpnext_apm
```

### Step 2: Install Dependencies

```bash
bench pip install elastic-apm
```

### Step 3: Set Environment Variables

For testing, you can use a mock APM server URL or a real one:

**Option A: Test with Mock/Invalid URL (to verify initialization)**
```bash
export ELASTIC_APM_SERVICE_NAME=erpnext-test
export ELASTIC_APM_SERVER_URL=http://localhost:8200
export ELASTIC_APM_ENABLED=true
```

**Option B: Test with Real APM Server**
```bash
export ELASTIC_APM_SERVICE_NAME=erpnext-dev
export ELASTIC_APM_SERVER_URL=http://your-apm-server:8200
export ELASTIC_APM_ENVIRONMENT=development
export ELASTIC_APM_SECRET_TOKEN=your-secret-token  # if required
```

### Step 4: Restart Services

```bash
bench restart
```

### Step 5: Verify Installation

Check the logs to see if APM was initialized:

```bash
tail -f logs/web.log | grep -i apm
```

You should see messages like:
- "Elastic APM initialized: service=..."
- "Frappe WSGI application wrapped with Elastic APM middleware"
- "APM instrumentation setup complete - WSGI application wrapped"

## Testing Scenarios

### Test 1: Verify App is Installed

```bash
bench --site devsite.localhost list-apps | grep erpnext_apm
```

### Test 2: Check Python Imports

```bash
bench --site devsite.localhost console
```

Then in the console:
```python
from erpnext_apm import capture_exception, init_apm, get_client
print("✓ Imports work")
```

### Test 3: Test APM Initialization

```bash
bench --site devsite.localhost console
```

```python
import os
from erpnext_apm.apm import is_apm_enabled, init_apm, get_client

# Check if enabled
print(f"APM Enabled: {is_apm_enabled()}")

# Try to initialize (will fail if env vars not set, but won't crash)
client = init_apm()
print(f"APM Client: {client}")
```

### Test 4: Test Exception Capture

```bash
bench --site devsite.localhost console
```

```python
from erpnext_apm import capture_exception

try:
    raise ValueError("Test exception")
except Exception:
    capture_exception()
    print("✓ Exception captured (check APM server if configured)")
```

### Test 5: Make HTTP Requests

Generate some traffic to test instrumentation:

```bash
# Using curl
curl http://devsite.localhost:8000

# Or access the site in browser
# Then check APM dashboard for transactions
```

### Test 6: Check Logs for Errors

```bash
# Check for any APM-related errors
grep -i "apm\|elastic" logs/web.log | tail -20

# Should see initialization messages, not errors
```

## Testing Without Real APM Server

If you don't have an APM server running, you can still test:

1. **Verify initialization doesn't crash:**
   - Set invalid APM server URL
   - App should initialize but fail to connect (gracefully)
   - ERPNext should still work normally

2. **Test with disabled APM:**
   ```bash
   export ELASTIC_APM_ENABLED=false
   bench restart
   ```
   - App should skip initialization
   - Check logs: "Elastic APM is disabled"

## Troubleshooting Tests

### Test: Check Environment Variables

```bash
bench --site devsite.localhost console
```

```python
import os
required = ['ELASTIC_APM_SERVICE_NAME', 'ELASTIC_APM_SERVER_URL']
for var in required:
    value = os.getenv(var)
    print(f"{var}: {value or 'NOT SET'}")
```

### Test: Verify WSGI Wrapping

```bash
bench --site devsite.localhost console
```

```python
import frappe.app as frappe_app
print(f"Application type: {type(frappe_app.application)}")
# Should show ElasticAPM wrapper if working
```

### Test: Check Hook Execution

```bash
# After restart, check if after_migrate hook ran
grep "setup_apm\|APM instrumentation" logs/web.log
```

## Expected Behavior

✅ **Success Indicators:**
- App installs without errors
- Logs show "Elastic APM initialized"
- Logs show "WSGI application wrapped"
- ERPNext continues to work normally
- No crashes or errors in logs

❌ **Failure Indicators:**
- Import errors
- Missing environment variables cause crashes (shouldn't happen)
- ERPNext fails to start (shouldn't happen)

## Next Steps After Testing

1. If testing with real APM server:
   - Check Elastic APM dashboard
   - Verify service appears in "Services" list
   - Generate traffic and check for transactions

2. If issues found:
   - Check logs for specific error messages
   - Verify environment variables are set
   - Ensure elastic-apm package is installed
   - Try disabling APM to isolate issues

