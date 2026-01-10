"""
WSGI entry point for PythonAnywhere
"""
import sys
import os

# Add project directory to path
project_home = '/home/YOUR_USERNAME/mercedes-diesel-finder'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set working directory
os.chdir(project_home)

# Import the Flask app
from web_app import app as application
