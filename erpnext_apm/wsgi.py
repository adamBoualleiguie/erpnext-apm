# Copyright (c) 2024
# License: MIT

"""
WSGI middleware wrapper for Elastic APM
"""

import logging
import sys

logger = logging.getLogger(__name__)


class ElasticAPMWSGI:
	"""
	WSGI middleware that captures transactions and exceptions for Elastic APM
	
	This wraps the Frappe WSGI application and automatically:
	- Starts a transaction for each HTTP request
	- Captures request context (method, URL, headers)
	- Captures exceptions
	- Ends the transaction with proper result
	"""
	
	def __init__(self, application, client):
		self.application = application
		self.client = client
	
	def __call__(self, environ, start_response):
		# Extract request information
		method = environ.get("REQUEST_METHOD", "GET")
		path = environ.get("PATH_INFO", "/")
		
		# Start transaction
		transaction_name = f"{method} {path}"
		transaction_type = "request"
		
		transaction = self.client.begin_transaction(transaction_type)
		
		# Set transaction name
		self.client.set_transaction_name(transaction_name, override=False)
		
		# Set request context
		try:
			from elasticapm.utils.wsgi import get_current_url, get_headers, get_environ
			
			url = get_current_url(environ)
			headers = dict(get_headers(environ))
			env = dict(get_environ(environ))
			
			self.client.set_context(
				"request",
				{
					"method": method,
					"url": url,
					"headers": headers,
					"env": env,
				}
			)
		except Exception as e:
			logger.debug(f"Failed to set request context: {e}")
		
		# Track response
		status_code = None
		response_headers = []
		
		def custom_start_response(status, response_headers_list, exc_info=None):
			nonlocal status_code, response_headers
			status_code = int(status.split()[0]) if status else 500
			response_headers = response_headers_list
			
			# Set transaction result based on status code
			if status_code < 400:
				self.client.set_transaction_result("success", override=False)
			elif status_code < 500:
				self.client.set_transaction_result("client_error", override=False)
			else:
				self.client.set_transaction_result("server_error", override=False)
			
			return start_response(status, response_headers_list, exc_info)
		
		# Execute the application
		try:
			response = self.application(environ, custom_start_response)
			
			# Handle response (can be list or generator)
			if isinstance(response, list):
				# List response - end transaction after returning
				try:
					return response
				finally:
					# End transaction
					self.client.end_transaction(transaction_name, transaction_type)
			else:
				# Generator response - wrap it to handle exceptions and end transaction
				def response_wrapper():
					try:
						for chunk in response:
							yield chunk
					except Exception:
						exc_info = sys.exc_info()
						self.client.capture_exception(exc_info=exc_info)
						self.client.set_transaction_result("error", override=True)
						exc_info = None
						raise
					finally:
						# End transaction
						self.client.end_transaction(transaction_name, transaction_type)
				
				return response_wrapper()
		
		except Exception:
			exc_info = sys.exc_info()
			
			# Capture exception
			self.client.capture_exception(exc_info=exc_info)
			
			# Set transaction result to error
			self.client.set_transaction_result("error", override=True)
			
			# End transaction
			self.client.end_transaction(transaction_name, transaction_type)
			
			exc_info = None
			raise


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
		# Wrap the application with our custom WSGI middleware
		wrapped_app = ElasticAPMWSGI(application, client)
		
		logger.info(
			f"Frappe WSGI application wrapped with Elastic APM middleware. "
			f"Client: {client}, Service: {client.config.service_name if client else 'None'}"
		)
		return wrapped_app
		
	except Exception as e:
		logger.error(f"Failed to wrap WSGI application with APM: {e}", exc_info=True)
		# Return original application if wrapping fails
		return application
