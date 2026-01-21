# Quick Testing Guide

## ✅ Current Status

The app is **installed** and **ready to test**! Here's what's working:

- ✓ App installed on site
- ✓ elastic-apm package installed (v6.25.0)
- ✓ All imports working
- ✓ APM initialization working
- ✓ Exception capture working

## 🚀 Quick Test Steps

### 1. Set Environment Variables

```bash
export ELASTIC_APM_SERVICE_NAME=erpnext-test
export ELASTIC_APM_SERVER_URL=http://localhost:8200
export ELASTIC_APM_ENABLED=true
```

### 2. Restart Services

```bash
bench restart
```

### 3. Check Logs

```bash
tail -f logs/web.log | grep -i apm
```

You should see:
- "Elastic APM initialized: service=erpnext-test"
- "Frappe WSGI application wrapped with Elastic APM middleware"

### 4. Run Test Script

```bash
# From bench root
export ELASTIC_APM_SERVICE_NAME=erpnext-test
export ELASTIC_APM_SERVER_URL=http://localhost:8200
python apps/erpnext_apm/test_apm.py
```

### 5. Test in Console

```bash
bench --site devsite.localhost console
```

```python
# Test imports
from erpnext_apm import capture_exception
print("✓ Import works")

# Test exception capture
try:
    raise ValueError("Test")
except:
    capture_exception()
    print("✓ Exception captured")
```

### 6. Generate HTTP Traffic

```bash
# Make a request
curl http://devsite.localhost:8000

# Or access in browser
# Then check APM dashboard (if server is running)
```

## 📊 Expected Results

### ✅ Success Indicators:
- No errors in logs
- "APM initialized" messages in logs
- ERPNext works normally
- Test script shows all tests passing

### ⚠️ Expected Warnings (Normal):
- "Connection to APM Server timed out" - This is **normal** if you don't have an APM server running
- The app will still work, it just can't send data to APM server

## 🔧 Testing with Real APM Server

If you have an Elastic APM server:

1. Set the correct server URL:
   ```bash
   export ELASTIC_APM_SERVER_URL=http://your-apm-server:8200
   export ELASTIC_APM_SECRET_TOKEN=your-token  # if required
   ```

2. Restart:
   ```bash
   bench restart
   ```

3. Check Elastic APM dashboard:
   - Navigate to **APM → Services**
   - You should see "erpnext-test" (or your service name)
   - Generate traffic and check for transactions

## 🧪 Test Scenarios

### Test 1: Disable APM
```bash
export ELASTIC_APM_ENABLED=false
bench restart
# Should see: "Elastic APM is disabled" in logs
```

### Test 2: Missing Required Vars
```bash
unset ELASTIC_APM_SERVICE_NAME
unset ELASTIC_APM_SERVER_URL
bench restart
# Should see error in logs but ERPNext still works
```

### Test 3: Invalid Server URL
```bash
export ELASTIC_APM_SERVER_URL=http://invalid:8200
bench restart
# Should initialize but fail to connect (gracefully)
```

## 📝 Next Steps

1. **If testing locally without APM server:**
   - The app works but can't send data (expected)
   - All functionality is tested and working

2. **If you have an APM server:**
   - Set correct environment variables
   - Restart services
   - Check APM dashboard for your service
   - Generate traffic and verify transactions appear

3. **For production:**
   - Set environment variables in your deployment config
   - Use proper APM server URL
   - Set secret token if required
   - Monitor APM dashboard for performance data

## 🐛 Troubleshooting

If something doesn't work:

1. **Check logs:**
   ```bash
   grep -i apm logs/web.log | tail -20
   ```

2. **Verify environment variables:**
   ```bash
   bench --site devsite.localhost console
   >>> import os
   >>> os.getenv('ELASTIC_APM_SERVICE_NAME')
   >>> os.getenv('ELASTIC_APM_SERVER_URL')
   ```

3. **Verify package is installed:**
   ```bash
   source env/bin/activate
   pip list | grep elastic
   ```

4. **Re-run test script:**
   ```bash
   python apps/erpnext_apm/test_apm.py
   ```

