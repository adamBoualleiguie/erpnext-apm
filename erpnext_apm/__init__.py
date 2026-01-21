# Copyright (c) 2024
# License: MIT

"""
ERPNext APM - Elastic APM integration for ERPNext
"""

__version__ = "1.0.0"

# Export APM functions
from erpnext_apm.apm import init_apm, get_client, capture_exception

__all__ = ["init_apm", "get_client", "capture_exception"]

