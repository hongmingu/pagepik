from .base import *
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT_DIR = os.path.dirname(BASE_DIR)
SETTINGS_DIR = os.path.join(BASE_DIR, 'pagepik', 'settings')
SETTINGS_FILE = os.path.join(SETTINGS_DIR, 'local_settings.json')

with open(SETTINGS_FILE) as f:
    settings_json = json.loads(f.read())

DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'authapp',
    'baseapp',
    'object',
    'notice',
    'relation',
    'debug_toolbar',
]
# django debug-toolbar
INTERNAL_IPS = ('127.0.0.1',)

SITE_ID = 1

WSGI_APPLICATION = 'pagepik.wsgi.local.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # django debug-toolbar
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
# Authentication Backend
AUTHENTICATION_BACKENDS = [
    'authapp.backends.EmailOrUsernameAuthBackend',
    # 'django.contrib.auth.backends.ModelBackend',
]

#### Static settings
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')#이 폴더가 없으면 만들어질 것이다.

#### Media settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_dir')


SMTPusername = settings_json['django']['SMTPusername']
SMTPpassword = settings_json['django']['SMTPpassword']


# Email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-west-2.amazonaws.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = SMTPusername
EMAIL_HOST_PASSWORD = SMTPpassword
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'test-username@moneycurry.com'
