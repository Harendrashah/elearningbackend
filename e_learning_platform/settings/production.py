# e_learning_platform/settings/production.py

from .base import *

# Production mode
DEBUG = config('DEBUG', default=False, cast=bool)

# Secret key from Render Environment Variables
SECRET_KEY = config('SECRET_KEY')

# Allowed hosts
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,elearningbackend-ak5r.onrender.com'
).split(',')

# CORS settings
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://informaticedu.netlify.app',
]

CORS_ALLOW_CREDENTIALS = True