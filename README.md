# ERPNext APM

Elastic APM integration for ERPNext. This app automatically instruments all HTTP requests, captures transactions, spans, and errors, and sends them to Elastic APM Server.

## Features

- ✅ Automatic instrumentation of all ERPNext HTTP requests
- ✅ Transaction and span capture
- ✅ Error and exception tracking
- ✅ Zero code changes required in ERPNext core
- ✅ Enable/disable by installing/uninstalling the app
- ✅ Environment variable configuration only

## Installation

1. **Install the app:**

```bash
cd /path/to/your/bench
bench --site [your-site] install-app erpnext_apm
```

2. **Install dependencies:**

The `elastic-apm` package will be installed automatically via `pyproject.toml`. If needed, you can also install manually:

```bash
bench pip install elastic-apm
```

3. **Configure environment variables** (see Configuration section below)

4. **Restart your Frappe/ERPNext services:**

```bash
bench restart
```

## Configuration

The app reads configuration **only** from environment variables. Set these in your environment or in your site's configuration.

### Required Variables

| Variable                   | Description                          | Example                             |
| -------------------------- | ------------------------------------ | ----------------------------------- |
| `ELASTIC_APM_SERVICE_NAME` | Name of your service in APM          | `erpnext-prod`                      |
| `ELASTIC_APM_SERVER_URL`   | URL of your Elastic APM Server        | `http://apm.elasticsearch.svc:8200` |

### Optional Variables

| Variable                   | Description                          | Example      |
| -------------------------- | ------------------------------------ | ------------ |
| `ELASTIC_APM_SECRET_TOKEN` | Secret token for APM Server          | `xxxx`       |
| `ELASTIC_APM_ENVIRONMENT`  | Environment name (e.g., production)  | `production` |
| `ELASTIC_APM_ENABLED`      | Enable/disable APM (default: true)   | `true/false` |

### Example Configuration

For **Kubernetes/Docker**, set environment variables in your deployment:

```yaml
env:
  - name: ELASTIC_APM_SERVICE_NAME
    value: "erpnext-prod"
  - name: ELASTIC_APM_SERVER_URL
    value: "http://apm-server:8200"
  - name: ELASTIC_APM_ENVIRONMENT
    value: "production"
  - name: ELASTIC_APM_SECRET_TOKEN
    valueFrom:
      secretKeyRef:
        name: apm-secret
        key: token
```

For **local development**, export in your shell:

```bash
export ELASTIC_APM_SERVICE_NAME=erpnext-dev
export ELASTIC_APM_SERVER_URL=http://localhost:8200
export ELASTIC_APM_ENVIRONMENT=development
```

## Usage

### Automatic Instrumentation

Once installed and configured, the app automatically:

- Instruments all HTTP requests to ERPNext
- Captures transactions and spans
- Tracks errors and exceptions
- Sends data to Elastic APM Server

### Manual Exception Capture

You can manually capture exceptions in your code:

```python
from erpnext_apm import capture_exception

try:
    # your code
    pass
except Exception:
    capture_exception()
```

## Verification

1. **Check Elastic APM Server:**

   - Open your Elastic APM dashboard
   - Navigate to **APM → Services**
   - You should see your service name (from `ELASTIC_APM_SERVICE_NAME`)

2. **Generate some traffic:**

   - Make some HTTP requests to your ERPNext instance
   - Check the APM dashboard for transactions and traces

3. **Check logs:**

   - Look for "Frappe WSGI application wrapped with Elastic APM" in your logs
   - This confirms the app is working

## Troubleshooting

### APM not appearing in Elastic

1. **Check environment variables:**
   ```bash
   bench --site [your-site] console
   >>> import os
   >>> os.getenv('ELASTIC_APM_SERVICE_NAME')
   >>> os.getenv('ELASTIC_APM_SERVER_URL')
   ```

2. **Check if APM is enabled:**
   ```bash
   >>> os.getenv('ELASTIC_APM_ENABLED', 'true')
   ```

3. **Check logs:**
   ```bash
   tail -f logs/web.log
   ```
   Look for APM-related messages

4. **Verify APM Server connectivity:**
   - Ensure your APM Server is reachable from the ERPNext instance
   - Check firewall rules and network policies

### APM causing errors

The app is designed to **never crash ERPNext** if APM fails. If you see errors:

1. Check that `elastic-apm` is installed:
   ```bash
   bench pip list | grep elastic-apm
   ```

2. Check logs for specific error messages

3. Disable APM temporarily:
   ```bash
   export ELASTIC_APM_ENABLED=false
   bench restart
   ```

## Uninstallation

To remove APM instrumentation:

```bash
bench --site [your-site] uninstall-app erpnext_apm
bench restart
```

## Architecture

- **Zero modifications** to ERPNext or Frappe core
- **WSGI middleware** wraps `frappe.app.application`
- **after_migrate hook** ensures early initialization
- **Non-blocking** - APM failures don't affect ERPNext

## Compatibility

- ERPNext v14+
- Frappe v14+
- Python 3.10+
- Elastic APM Server 7.0+

## License

MIT
