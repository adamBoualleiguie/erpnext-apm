# Copyright (c) 2024
# License: MIT

"""
Monkey patch module to wrap Frappe WSGI application with Elastic APM

This module is imported in hooks.py to ensure APM wrapping happens early,
similar to how Sentry wraps the application in frappe.app.
"""

import logging

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
		from erpnext_apm.apm import init_apm, is_apm_enabled
		
		# Check if APM is enabled
		if not is_apm_enabled():
			logger.debug("APM is disabled, skipping WSGI wrapping")
			return
		
		# Initialize APM client early
		init_apm()
		
		# Try to import and wrap frappe.app.application
		# This might fail if frappe.app hasn't been imported yet,
		# which is okay - we'll wrap it later via the startup hook
		try:
			import frappe.app as frappe_app
			
			if hasattr(frappe_app, "application"):
				from erpnext_apm.wsgi import wrap_application
				# Wrap the application
				frappe_app.application = wrap_application(frappe_app.application)
				logger.info("Frappe WSGI application wrapped with Elastic APM (monkey_patch)")
			else:
				logger.debug("frappe.app.application not found yet, will wrap via startup hook")
				
		except (ImportError, AttributeError):
			# frappe.app might not be imported yet, that's okay
			logger.debug("frappe.app not available yet, will wrap via startup hook")
			
	except Exception as e:
		logger.error(f"Failed to wrap Frappe application with APM: {e}", exc_info=True)
		# Don't crash if APM setup fails


# Execute wrapping at module import time
# This will attempt to wrap, but won't fail if frappe.app isn't ready
_wrap_frappe_application()
