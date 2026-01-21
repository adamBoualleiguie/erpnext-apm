# Copyright (c) 2024
# License: MIT

"""
Monkey patch module to wrap Frappe WSGI application with Elastic APM

This module is imported in hooks.py to ensure APM wrapping happens early,
similar to how Sentry wraps the application in frappe.app.
"""

import logging
import os

logger = logging.getLogger(__name__)

# Track if we've attempted wrapping
_wrapping_attempted = False


def _wrap_frappe_application():
	"""
	Wrap frappe.app.application with Elastic APM middleware
	
	This function is called at module import time to ensure
	the WSGI application is wrapped before any requests are handled.
	"""
	global _wrapping_attempted
	
	if _wrapping_attempted:
		return
	
	_wrapping_attempted = True
	
	try:
		# Check if APM is enabled first
		enabled = os.getenv("ELASTIC_APM_ENABLED", "true").lower()
		if enabled not in ("true", "1", "yes", "on"):
			logger.debug("APM is disabled, skipping WSGI wrapping")
			return
		
		from erpnext_apm.apm import init_apm, get_client
		
		# Initialize APM client - force initialization to ensure it works
		client = init_apm(force=True)
		if not client:
			logger.warning("APM client initialization returned None - check configuration and logs")
			# Try once more without force
			client = init_apm(force=False)
			if not client:
				logger.error("APM client still None after retry - cannot wrap WSGI")
				return
		
		logger.info(f"APM client initialized in monkey_patch: {client}")
		
		# Try to import and wrap frappe.app.application
		# This might fail if frappe.app hasn't been imported yet,
		# which is okay - we'll wrap it later via the startup hook
		try:
			import frappe.app as frappe_app
			
			if hasattr(frappe_app, "application"):
				from erpnext_apm.wsgi import wrap_application
				# Wrap the application
				original_app = frappe_app.application
				wrapped_app = wrap_application(original_app)
				
				if wrapped_app != original_app:
					frappe_app.application = wrapped_app
					logger.info("Frappe WSGI application wrapped with Elastic APM (monkey_patch)")
				else:
					logger.warning("WSGI wrapping returned original application - wrapping may have failed")
			else:
				logger.debug("frappe.app.application not found yet, will wrap via startup hook")
				
		except (ImportError, AttributeError) as e:
			# frappe.app might not be imported yet, that's okay
			logger.debug(f"frappe.app not available yet ({e}), will wrap via startup hook")
		except Exception as e:
			logger.error(f"Error wrapping frappe.app.application: {e}", exc_info=True)
			
	except Exception as e:
		logger.error(f"Failed to wrap Frappe application with APM: {e}", exc_info=True)
		# Don't crash if APM setup fails


# Execute wrapping at module import time
# This will attempt to wrap, but won't fail if frappe.app isn't ready
_wrap_frappe_application()
