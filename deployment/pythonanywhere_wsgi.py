# WSGI Configuration for PythonAnywhere
# Replace 'yourusername' with your actual PythonAnywhere username

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/mercedes-finder'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables if needed
os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from web_app import app as application

# For debugging (remove in production)
# application.debug = False
