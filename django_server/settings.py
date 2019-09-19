"""
Django settings for survey project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from os import path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = BASE_DIR  # rename variable for clarity
FRONTEND_DIR = os.path.abspath(os.path.join(BACKEND_DIR, 'frontend', 'survey_dashboard'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@haq8t@d)n4w5r4a#79ghmpr#e3)gx3eu%i!v%po_00+akwk6v'

# SECURITY WARNING: don't run with debug tudjango_server/settings.pyrned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'junglesurvey.com',
    'dev.junglesurvey.com',
    'dashboard.junglesurvey.com',
    'jungleofferwall.com',
    'dev.jungleofferwall.com',
    'surveytimeforme.com',
    'dev.surveytimeforme.com',
    'dev.moretvtime.com',
    'www.moretvtime.com',
    'moretvtime.com',
    'localhost',
    '127.0.0.1',
]


STATIC_URL = '/static/'
STATIC_ROOT = path.join(BASE_DIR, 'static')
# STATIC_ROOT = path.join(FRONTEND_DIR, 'build', 'static')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django_countries',
    'rest_framework',
    'social_django',
    'import_export',
    'corsheaders',
    'survey',
    'dashboard',
    'django_user_agents',
    'translations'
]

MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',

    'survey.middleware.social_auth.AuthAssociatedMiddleware',
    'survey.middleware.referer.RefererMiddleware',
    'survey.middleware.user.UserMiddleware',
    'survey.middleware.vpn.VPNMiddleware'
]

X_FRAME_OPTIONS = 'DENY'
ROOT_URLCONF = 'django_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(FRONTEND_DIR, 'build'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'survey.context_processor.context',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'survey.pagination.CustomPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    )
}

WSGI_APPLICATION = 'django_server.wsgi.application'

GEOIP_PATH = os.path.abspath(os.path.join(BASE_DIR, 'django_server/geoip'))

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'survey',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'TEST': {
            'NAME': 'survey_test',
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
USER_AGENTS_CACHE = 'default'

AUTH_USER_MODEL = 'survey.SurveyUser'
SOCIAL_AUTH_POSTGRES_JSONFIELD = True

AUTHENTICATION_BACKENDS = (
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.google.GoogleOAuth',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.yahoo.YahooOpenId',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.twitch.TwitchOAuth2',
    'social_core.backends.discord.DiscordOAuth2',
    'social_core.backends.vk.VKOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Social
LOGIN_REDIRECT_URL = '/survey'

SOCIAL_AUTH_FACEBOOK_API_VERSION = '3.2'
SOCIAL_AUTH_FACEBOOK_KEY = '586198878457634'
SOCIAL_AUTH_FACEBOOK_SECRET = '9b1872214cbaaa5ba9ad93a41f837d47'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '280720990614-rdgek8h3h5flfi1kpmdhuk81c0755kkk.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '13weM0wzhUG-7L3aA7bNJ3yq'

SOCIAL_AUTH_TWITCH_KEY = '6pv4eaib5o93z7k80zev4xcyt59y47'
SOCIAL_AUTH_TWITCH_SECRET = '93r7n6yu26pzo2f6801472dfrvfaul'

SOCIAL_AUTH_TWITTER_KEY = 'nmi325L3FfiqDzT5TfQrZlLig'
SOCIAL_AUTH_TWITTER_SECRET = 'gdAe9wBB50BJXsdB4swgHi2iMT3146H1HNCVTm7TCdf0Ii3e4H'

SOCIAL_AUTH_DISCORD_KEY = '585387944865431552'
SOCIAL_AUTH_DISCORD_SECRET = 'CC94COF1E6b7aZuBTROYoZXSHuFrktLf'

SOCIAL_AUTH_VK_OAUTH2_KEY = '7010091'
SOCIAL_AUTH_VK_OAUTH2_SECRET = 'yUuqWcEDFS2UWmE5bG0h'

SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'survey.middleware.social_auth_pipeline.existing_user_email'
)

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

LANGUAGES = (            # supported languages
    ('en', 'English'),
    ('de', 'German'),
    ('tr', 'Turkish'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/survey/app.log',
            'maxBytes': 1024*1024*500,
            'backupCount': 2,
            'formatter':'standard',
        },
        'request_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/survey/django_request.log',
            'maxBytes': 1024*1024*500,
            'backupCount': 2,
            'formatter':'standard',
        },
        'command_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/survey/command.log',
            'maxBytes': 1024*1024*500,
            'backupCount': 2,
            'formatter':'standard',
        },
        'db_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/survey/postgres.log',
            'maxBytes': 1024*1024*500,
            'backupCount': 2,
            'formatter':'standard',
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        'survey.management.commands': {
            'handlers': ['command_handler', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'ddtrace': {
            'handlers': ['default'],
            'level': 'WARNING',
        },
    }
}

EMAIL_USE_TLS = False
# EMAIL_HOST = 'https://mail.junglesurvey.com/mail/'
# EMAIL_HOST_USER = 'support@junglesurvey.com'
# EMAIL_HOST_PASSWORD = 'W44gUBNa'
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 25
EMAIL_RECIPIENTS = ['gitt613@gmail.com', 'support@moretvtime.com', 'zadonsedon@gmail.com', 'vankyver007@gmail.com']

FAUCETHUB_API_KEY = 'cfe6a58aa806304c5ea47d022eee53e4'

RECAPTCHA_V2_SITE_KEY = '6Lc-nZ8UAAAAAFmtz0FKe_WRzyzSLOZwto2DxlQT'
RECAPTCHA_V2_SECRET_KEY = '6Lc-nZ8UAAAAAOmKXyPDctNrLl0tHnR3Q1mRwTfq'


MINUTE = 60
MINUTES_15 = 15 * MINUTE
HOURS_24 = 24 * 60 * MINUTE
DAYS_7 = 7 * 24 * 60 * MINUTE

##
# Application Level:
#
if os.environ.get('APP_DEBUG'):
    DEBUG = True
    SOCIAL_AUTH_REDIRECT_IS_HTTPS = False

    SURVEY_DEFAULT_QUESTION_TIMEOUT = 0.1
else:
    SURVEY_DEFAULT_QUESTION_TIMEOUT = 5
