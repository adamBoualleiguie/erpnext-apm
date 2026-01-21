# APM Diagnostics - Service Not Appearing in Observability

## Problem
APM server is receiving requests (you see logs), but the service doesn't appear in Elastic Observability UI.

## Root Cause Analysis

From your logs, I see:
- ✅ One request with `apm-agent-python/6.25.0 (erpnext-prod)` - Python agent is connecting
- ❌ Most requests are from `elasticapm-go/1.15.0` - Go agent (different service)
- ❌ Service not appearing in Observability UI

This suggests:
1. APM client is initialized and connecting
2. But **transactions are not being captured/sent**
3. Only metadata/health checks are being sent

## Solution

The issue is likely that:
1. **WSGI wrapping might not be working** in all pods
2. **Transactions need to be explicitly captured** 
3. **The gunicorn pod needs to be restarted** after code changes

## Diagnostic Steps

### 1. Run Verification Script

```bash
bench --site erp.localhost console
```

```python
from erpnext_apm.verify import verify_apm_setup
verify_apm_setup()
```

This will show:
- Environment variables
- APM client status
- WSGI wrapping status
- Transaction capture capability

### 2. Check Gunicorn Pod Logs

```bash
kubectl logs erpnext-gunicorn-6df697f99c-rgdnr | grep -i apm
```

Look for:
- "Elastic APM initialized"
- "Frappe WSGI application wrapped"
- Any errors

### 3. Verify WSGI Wrapping in Gunicorn Pod

```bash
kubectl exec -it erpnext-gunicorn-6df697f99c-rgdnr -- bash
bench --site erp.localhost console
```

```python
import frappe.app as frappe_app
print(type(frappe_app.application))
# Should show: <class 'elasticapm.contrib.wsgi.ElasticAPM'>
```

### 4. Generate Test Traffic

Make actual HTTP requests to trigger transactions:

```bash
# From outside the cluster or from another pod
curl http://erpnext-nginx-service/api/method/ping
curl http://erpnext-nginx-service/
```

Then check APM server logs for Python agent requests with transaction data.

### 5. Check APM Server for Transaction Data

Look for requests with larger body sizes (transaction data):
- Metadata requests: ~400-500 bytes
- Transaction requests: 1000+ bytes

## Common Issues

### Issue 1: WSGI Not Wrapped in Gunicorn

**Symptom**: No Python agent requests in APM server logs

**Fix**: 
1. Ensure code is updated in the pod
2. Restart gunicorn pod:
   ```bash
   kubectl rollout restart deployment erpnext-gunicorn
   ```

### Issue 2: Transactions Not Being Captured

**Symptom**: Python agent connects but no transaction data

**Fix**: The WSGI middleware should automatically capture, but verify:
1. Check that `frappe.app.application` is wrapped
2. Ensure HTTP requests are going through the wrapped application
3. Check for any errors in logs

### Issue 3: Service Name Mismatch

**Symptom**: Service appears but with wrong name

**Fix**: Verify environment variable:
```bash
kubectl get deployment erpnext-gunicorn -o yaml | grep ELASTIC_APM_SERVICE_NAME
```

## Expected Behavior

After fixing:

1. **APM Server Logs** should show:
   - Regular requests from `apm-agent-python/6.25.0 (erpnext-prod)`
   - Larger request bodies (1000+ bytes) indicating transaction data
   - Requests to `/intake/v2/events` with transaction payloads

2. **Elastic Observability UI** should show:
   - Service: `erpnext-prod`
   - Transactions appearing after HTTP requests
   - Service map with connections

3. **Gunicorn Logs** should show:
   - "Elastic APM initialized: service=erpnext-prod"
   - "Frappe WSGI application wrapped with Elastic APM middleware"

## Next Steps

1. **Update code** in your repository
2. **Restart gunicorn pod** to load new code
3. **Run verification script** to confirm setup
4. **Generate HTTP traffic** to create transactions
5. **Check Observability UI** - should appear within 1-2 minutes

## Quick Fix Command

```bash
# Restart gunicorn to reload code
kubectl rollout restart deployment erpnext-gunicorn

# Wait for pod to be ready
kubectl rollout status deployment erpnext-gunicorn

# Check logs
kubectl logs -f deployment/erpnext-gunicorn | grep -i apm
```

