# Copyright (c) 2024
# License: MIT

"""
Startup module for APM initialization

This module wraps the Frappe WSGI application with Elastic APM middleware.
It's called both at module import time (via hooks.py) and via the after_migrate hook.
"""

import logging

logger = logging.getLogger(__name__)

# Track if we've already set up APM
_apm_setup_done = False


def setup_apm():
	"""
	Setup APM instrumentation
	
	This function is called:
	1. At module import time (via hooks.py import)
	2. Via the after_migrate hook (as fallback)
	
	It initializes APM and wraps the WSGI application.
	"""
	global _apm_setup_done
	
	if _apm_setup_done:
		return
	
	try:
		from erpnext_apm.apm import init_apm
		from erpnext_apm.wsgi import wrap_application
		
		# Initialize APM client
		init_apm()
		
		# Wrap the WSGI application
		# This must be done after frappe.app.application is defined
		try:
			# Import frappe.app to get access to the application
			import frappe.app as frappe_app
			
			# Wrap the application if it exists
			if hasattr(frappe_app, "application"):
				frappe_app.application = wrap_application(frappe_app.application)
				logger.info("APM instrumentation setup complete - WSGI application wrapped")
			else:
				logger.warning("frappe.app.application not found, APM WSGI wrapping skipped")
		
		except ImportError as e:
			logger.warning(f"Could not import frappe.app: {e}. APM WSGI wrapping skipped.")
		except Exception as e:
			logger.error(f"Failed to wrap WSGI application: {e}", exc_info=True)
		
		_apm_setup_done = True
		
	except Exception as e:
		logger.error(f"Failed to setup APM: {e}", exc_info=True)
		# Don't crash the application if APM setup fails
		_apm_setup_done = True  # Mark as done to avoid retry loops


# Try to setup APM at module import time
# This ensures it runs early, even if after_migrate hasn't run
try:
	setup_apm()
except Exception:
	# Silently fail at import time - setup_apm will be called again via hook
	pass
