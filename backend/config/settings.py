"""Configuración inicial; la persistencia se integrará en una fase posterior."""

import os

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
DEBUG = False
ALLOWED_HOSTS = []
ROOT_URLCONF = "config.urls"
INSTALLED_APPS = ["rest_framework"]
MIDDLEWARE = []

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}
