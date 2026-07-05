"""
Base settings for CampusVisa — Digital Campus France Student Portal.

Color Palette: #C81025 (red/accent), #FFFFFF (white/primary), #002654 (blue/secondary)
Fonts: Satoshi, Inter
Frontend: Django templates + TailwindCSS 3 CDN
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------- PATH CONFIGURATION ----------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env')


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}

# ---------- APPLICATION DEFINITION ----------
INSTALLED_APPS = [
    # ASGI server (must be before staticfiles to override runserver)
    'daphne',

    # Django built-in
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party
    'rest_framework',
    'channels',
    'corsheaders',
    'crispy_forms',
    'crispy_tailwind',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'phonenumber_field',
    'django_countries',

    # Project apps
    'apps.accounts',
    'apps.pages',
    'apps.nextstep',
    'apps.onboarding',
    'apps.plans',
    'apps.documents',
    'apps.chat',
    'apps.meetings',
    'apps.notifications',
    'apps.dashboard',
    'apps.admin_panel',
]

SITE_ID = 1

# ---------- MIDDLEWARE ----------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'config.middleware.SubdomainRoutingMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.admin_panel.middleware.MaintenanceModeMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'apps.admin_panel.middleware.SubdomainMiddleware',
]

ROOT_URLCONF = 'config.urls'
STAFF_URLCONF = 'config.urls_staff'
STAFF_SUBDOMAIN_PREFIX = 'staff'
STUDENT_SPACE_PATH_PREFIXES = (
    '/dashboard/',
    '/onboarding/',
    '/plans/',
    '/documents/',
    '/chat/',
    '/meetings/',
    '/notifications/',
)

# ---------- TEMPLATES ----------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.nextstep.context_processors.nextstep_settings',
                'apps.pages.context_processors.site_settings',
            ],
        },
    },
]

# ---------- PASSWORD VALIDATION ----------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------- INTERNATIONALIZATION ----------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------- STATIC FILES ----------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ---------- MEDIA FILES ----------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---------- CUSTOM USER MODEL ----------
AUTH_USER_MODEL = 'accounts.CustomUser'

# ---------- AUTHENTICATION BACKENDS (allauth) ----------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ---------- ALLAUTH SETTINGS ----------
LOGIN_REDIRECT_URL = '/dashboard/'
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']

# ---------- CRISPY FORMS ----------
CRISPY_ALLOWED_TEMPLATE_PACKS = 'tailwind'
CRISPY_TEMPLATE_PACK = 'tailwind'

# ---------- ASGI / CHANNELS ----------
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379/0')],
        },
    },
}

# Celery Configuration Options
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# ---------- DJANGO REST FRAMEWORK ----------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# ---------- EMAIL (SMTP) ----------
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
EMAIL_USE_SSL = env_bool('EMAIL_USE_SSL', False)
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', 20))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL') or EMAIL_HOST_USER or 'no-reply@campusvisa.local'

# ---------- FCM / Firebase Push ----------
FCM_ENABLED = env_bool('FCM_ENABLED', False)
FCM_DRY_RUN = env_bool('FCM_DRY_RUN', False)
FCM_PROJECT_ID = os.environ.get('FCM_PROJECT_ID', '')
_fcm_credentials_file = os.environ.get('FCM_CREDENTIALS_FILE', '').strip()
if _fcm_credentials_file:
    _fcm_path = Path(_fcm_credentials_file)
    if not _fcm_path.is_absolute():
        _fcm_path = BASE_DIR / _fcm_path
    FCM_CREDENTIALS_FILE = _fcm_path
else:
    FCM_CREDENTIALS_FILE = None

# ---------- DEFAULT PRIMARY KEY FIELD TYPE ----------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




# Share sessions across all subdomains
SESSION_COOKIE_DOMAIN = '.nextstepc.com'
CSRF_COOKIE_DOMAIN = '.nextstepc.com'

# Trust all subdomains for CSRF (Django 4.0+)
CSRF_TRUSTED_ORIGINS = [
    'https://nextstepc.com',
    'https://*.nextstepc.com',
]
