# e_learning_platform/settings/production.py

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
# This will be loaded from an environment variable
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Add your production domain(s) here
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Database configuration is already in base.py, using environment variables
# Make sure to set the DB_* environment variables on your server

# Static files configuration for production (e.g., using Whitenoise or S3)
# STATIC_ROOT = '/var/www/myproject/static/' # Example for a server