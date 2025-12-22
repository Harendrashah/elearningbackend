from django.apps import AppConfig

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    # label = 'chat'  # optional, remove if you set it explicitly somewhere else
