"""
Settings package for library_management_system project.
Import from development by default for local development.
"""

import os

environment = os.environ.get('DJANGO_ENV', 'development')

if environment == 'production':
    from .production import *
else:
    from .development import *
