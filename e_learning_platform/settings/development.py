from .base import *
from urllib.parse import quote
import dj_database_url

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'elearningbackend-ak5r.onrender.com']

# डेटाबेस सेटिङ - यसरी हाल्दा सबैभन्दा सुरक्षित हुन्छ
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.whwzsjamfweosiijeysf',
        'PASSWORD': 'ShahBro2060', 
        'HOST': 'aws-1-ap-northeast-2.pooler.supabase.com',
        'PORT': '6543',
        # यो सही तरिका हो:
        'DISABLE_SERVER_SIDE_CURSORS': True, 
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]
# CORS_ALLOW_CREDENTIALS = True

