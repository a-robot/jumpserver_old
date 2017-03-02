"""
Django settings for jumpserver project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import configparser

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xv_aywu54z_jz16%x9i!&e_^+evj#ail+d#$n$qzjsh%9y9zb9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_crontab',
    'bootstrapform',
    'jumpserver',
    'jasset',
    'juser',
    'jproject',
    'jperm',
    'jlog',
    'jsetting',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jumpserver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'jumpserver.context_processors.name_proc',
            ],
        },
    },
]

WSGI_APPLICATION = 'jumpserver.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'


# ----------------- additional config ---------------- #
# ========== static dir =========
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

# ======== replace default user model ========
AUTH_USER_MODEL = 'juser.User'

config = configparser.ConfigParser()
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
config.read(os.path.join(BASE_DIR, 'jumpserver.conf'))
KEY_DIR = os.path.join(BASE_DIR, 'keys')

# ======== mail config =======
MAIL_ENABLE = config.get('mail', 'mail_enable')
EMAIL_HOST = config.get('mail', 'email_host')
EMAIL_PORT = config.get('mail', 'email_port')
EMAIL_HOST_USER = config.get('mail', 'email_host_user')
EMAIL_HOST_PASSWORD = config.get('mail', 'email_host_password')
EMAIL_USE_TLS = config.getboolean('mail', 'email_use_tls')
try:
    EMAIL_USE_SSL = config.getboolean('mail', 'email_use_ssl')
except configparser.NoOptionError:
    EMAIL_USE_SSL = False
EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend' if EMAIL_USE_SSL else 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_TIMEOUT = 5

# ======== Log ==========
LOG_DIR = os.path.join(BASE_DIR, 'logs')
SSH_KEY_DIR = os.path.join(BASE_DIR, 'keys/role_keys')
KEY = config.get('base', 'key')
URL = config.get('base', 'url')
LOG_LEVEL = config.get('base', 'log')
IP = config.get('base', 'ip')
PORT = config.get('base', 'port')

# ======== Connect ==========
try:
    NAV_SORT_BY = config.get('connect', 'nav_sort_by')
except (configparser.NoSectionError, configparser.NoOptionError):
    NAV_SORT_BY = 'ip'

# ======== database =========
DATABASES = {}
if config.get('db', 'engine') == 'mysql':
    DB_HOST = config.get('db', 'host')
    DB_PORT = config.getint('db', 'port')
    DB_USER = config.get('db', 'user')
    DB_PASSWORD = config.get('db', 'password')
    DB_DATABASE = config.get('db', 'database')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': DB_DATABASE,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }
    }
elif config.get('db', 'engine') == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': config.get('db', 'database'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }


# ========== cron job =========
CRONJOBS = [
    ('0 1 * * *', 'jasset.asset_api.asset_ansible_update_all'),
    ('*/10 * * * *', 'jlog.log_api.kill_invalid_connection'),
]
