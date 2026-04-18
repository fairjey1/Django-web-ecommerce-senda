from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' # This is the default primary key field type for models in Django 3.2 and later.
    name = 'apps.core'
