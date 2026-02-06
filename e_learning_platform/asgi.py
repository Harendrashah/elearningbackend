import os

from django.core.wsgi import get_wsgi_application

# यहाँ तपाईंको settings फाइलको सही path हुनुपर्छ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_learning_platform.settings.development')

application = get_wsgi_application()
