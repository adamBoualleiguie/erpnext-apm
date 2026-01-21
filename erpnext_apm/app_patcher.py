# Copyright (c) 2024
# License: MIT

"""
Application patcher that wraps frappe.app.application when it's accessed

This module uses a property descriptor to intercept access to frappe.app.application
and wrap it with APM middleware on first access.
"""

import logging

logger = logging.getLogger(__name__)

_wrapped = False


def patch_application():
	"""
	Patch frappe.app.application to wrap it with APM on first access
	
	This is called from hooks.py to set up the patching mechanism
	"""
	global _wrapped
	
	if _wrapped:
		return
	
	try:
		import frappe.app as frappe_app
		
		# Check if already wrapped
		if hasattr(frappe_app, "application"):
			app = frappe_app.application
			
			# Check if it's already our wrapper
			if hasattr(app, "__class__") and "ElasticAPMWSGI" in str(app.__class__):
				logger.debug("Application already wrapped with APM")
				_wrapped = True
				return
			
			# Try to wrap it
			from erpnext_apm.apm import init_apm, get_client
			from erpnext_apm.wsgi import wrap_application
			
			# Initialize client
			client = init_apm(force=True)
			if not client:
				logger.warning("Cannot wrap application - APM client not initialized")
				_wrapped = True
				return
			
			# Wrap the application
			wrapped = wrap_application(app)
			if wrapped != app:
				frappe_app.application = wrapped
				logger.info("Successfully wrapped frappe.app.application with APM")
				_wrapped = True
			else:
				logger.warning("WSGI wrapping returned original application")
				_wrapped = True
		
	except Exception as e:
		logger.error(f"Failed to patch application: {e}", exc_info=True)
		_wrapped = True  # Don't retry if it fails

