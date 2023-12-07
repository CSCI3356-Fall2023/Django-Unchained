# apps.py
from django.apps import AppConfig
from django.apps.registry import apps
from django.db.models.signals import post_migrate

class EaglevisionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'EagleVision'
