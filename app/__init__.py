"""
FastAPI Authentication Service

A production-ready authentication service with Auth0 integration,
role-based access control, and async support.
"""

__version__ = "1.0.0"
__author__ = "Farai Wande"
__email__ = "faraiwande@gmail.com"

from .config import settings

# Package imports
from .main import app

__all__ = ["app", "settings"]
