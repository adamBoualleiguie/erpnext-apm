# Copyright (c) 2024
# License: MIT

"""
WSGI middleware wrapper for Elastic APM
"""

import logging

logger = logging.getLogger(__name__)


def wrap_application(application):
	"""
	Wrap the Frappe WSGI application with Elastic APM middleware
	
	This function should be called once at startup to instrument all HTTP requests
	"""
	from erpnext_apm.apm import get_client, is_apm_enabled
	
	if not is_apm_enabled():
		logger.debug("APM is disabled, skipping WSGI wrapping")
		return application
	
	client = get_client()
	if not client:
		logger.debug("APM client not initialized, skipping WSGI wrapping")
		return application
	
	try:
		from elasticapm.contrib.wsgi import ElasticAPM
		
		# Wrap the application with Elastic APM middleware
		wrapped_app = ElasticAPM(application, client=client)
		
		logger.info("Frappe WSGI application wrapped with Elastic APM middleware")
		return wrapped_app
		
	except ImportError:
		logger.error("elastic-apm package not found. Cannot wrap WSGI application.")
		return application
	except Exception as e:
		logger.error(f"Failed to wrap WSGI application with APM: {e}", exc_info=True)
		# Return original application if wrapping fails
		return application
