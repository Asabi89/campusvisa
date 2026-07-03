"""
Development settings for CampusVisa.
"""

import os

from .base import *  # noqa: F401, F403

# ---------- DEBUG ----------
DEBUG = True

# ---------- SECRET KEY ----------
SECRET_KEY = 'dev-secret-key-change-in-production'

# ---------- ALLOWED HOSTS ----------
# For LAN testing on another device:
# - Start server with: python manage.py runserver 0.0.0.0:8000
# - Use a DNS host such as: staff.<YOUR_IP>.nip.io:8000
ALLOWED_HOSTS = ['*', 'staff.localhost', 'localhost', '127.0.0.1', '.nip.io', '.sslip.io']

# ---------- DATABASE ----------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------- CHANNEL LAYERS ----------
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# ---------- EMAIL ----------
if os.environ.get('EMAIL_HOST_USER') and os.environ.get('EMAIL_HOST_PASSWORD'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ---------- CORS ----------
CORS_ALLOW_ALL_ORIGINS = True

# ---------- GOOGLE CALENDAR / MEET ----------
# To enable automatic Google Meet link generation:
# 1. Go to https://console.cloud.google.com
# 2. Create a project → Enable "Google Calendar API"
# 3. Create a Service Account → Download JSON key
# 4. Place the JSON file in env/ folder
# 5. Uncomment the lines below:
GOOGLE_CALENDAR_CREDENTIALS_FILE = BASE_DIR / 'env' / 'google-credentials.json'
GOOGLE_CALENDAR_ID = 'idowuasabidavid@gmail.com'  # or a specific calendar ID
