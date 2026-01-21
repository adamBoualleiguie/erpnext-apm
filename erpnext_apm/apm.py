# Copyright (c) 2024
# License: MIT

"""
Elastic APM initialization and configuration
"""

import os
import logging

logger = logging.getLogger(__name__)

# Global APM client instance
_apm_client = None
_initialized = False


def is_apm_enabled():
	"""Check if APM is enabled via environment variable"""
	enabled = os.getenv("ELASTIC_APM_ENABLED", "true").lower()
	return enabled in ("true", "1", "yes", "on")


def get_config():
	"""Get APM configuration from environment variables"""
	config = {}
	
	# Required
	service_name = os.getenv("ELASTIC_APM_SERVICE_NAME")
	server_url = os.getenv("ELASTIC_APM_SERVER_URL")
	
	if not service_name:
		raise ValueError("ELASTIC_APM_SERVICE_NAME environment variable is required")
	if not server_url:
		raise ValueError("ELASTIC_APM_SERVER_URL environment variable is required")
	
	config["SERVICE_NAME"] = service_name
	config["SERVER_URL"] = server_url
	
	# Optional
	if secret_token := os.getenv("ELASTIC_APM_SECRET_TOKEN"):
		config["SECRET_TOKEN"] = secret_token
	
	if environment := os.getenv("ELASTIC_APM_ENVIRONMENT"):
		config["ENVIRONMENT"] = environment
	
	# Additional optional configs
	if service_version := os.getenv("ELASTIC_APM_SERVICE_VERSION"):
		config["SERVICE_VERSION"] = service_version
	
	if service_node_name := os.getenv("ELASTIC_APM_SERVICE_NODE_NAME"):
		config["SERVICE_NODE_NAME"] = service_node_name
	
	# Framework name
	config["FRAMEWORK_NAME"] = "frappe"
	config["FRAMEWORK_VERSION"] = "14+"
	
	return config


def init_apm():
	"""Initialize Elastic APM client"""
	global _apm_client, _initialized
	
	if _initialized:
		return _apm_client
	
	if not is_apm_enabled():
		logger.info("Elastic APM is disabled (ELASTIC_APM_ENABLED=false)")
		_initialized = True
		return None
	
	try:
		import elasticapm
	except ImportError:
		logger.error(
			"elastic-apm package not found. Install it with: pip install elastic-apm"
		)
		_initialized = True
		return None
	
	try:
		config = get_config()
		
		# Build config dict for elasticapm.Client
		client_config = {
			"SERVICE_NAME": config["SERVICE_NAME"],
			"SERVER_URL": config["SERVER_URL"],
			"FRAMEWORK_NAME": config["FRAMEWORK_NAME"],
			"FRAMEWORK_VERSION": config["FRAMEWORK_VERSION"],
		}
		
		if "SECRET_TOKEN" in config:
			client_config["SECRET_TOKEN"] = config["SECRET_TOKEN"]
		
		if "ENVIRONMENT" in config:
			client_config["ENVIRONMENT"] = config["ENVIRONMENT"]
		
		if "SERVICE_VERSION" in config:
			client_config["SERVICE_VERSION"] = config["SERVICE_VERSION"]
		
		if "SERVICE_NODE_NAME" in config:
			client_config["SERVICE_NODE_NAME"] = config["SERVICE_NODE_NAME"]
		
		# Create client
		_apm_client = elasticapm.Client(client_config)
		
		logger.info(
			f"Elastic APM initialized: service={config['SERVICE_NAME']}, "
			f"server={config['SERVER_URL']}"
		)
		
		_initialized = True
		return _apm_client
		
	except Exception as e:
		logger.error(f"Failed to initialize Elastic APM: {e}", exc_info=True)
		# Don't crash the application if APM fails
		_initialized = True
		return None


def get_client():
	"""Get the initialized APM client"""
	return _apm_client


def capture_exception(exc_info=None, **kwargs):
	"""
	Capture an exception to Elastic APM
	
	Usage:
		from erpnext_apm import capture_exception
		
		try:
			# some code
		except Exception:
			capture_exception()
	"""
	global _apm_client
	
	if not _apm_client:
		return
	
	try:
		_apm_client.capture_exception(exc_info=exc_info, **kwargs)
	except Exception as e:
		# Don't let APM errors break the application
		logger.debug(f"Failed to capture exception to APM: {e}")
