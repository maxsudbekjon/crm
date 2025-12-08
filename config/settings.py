import os
from pathlib import Path
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-so_eox^=#=syxam$$1cn!dv24u+4^6b-#e94n60z_r=d+h6gg%'
DEBUG = True
ALLOWED_HOSTS = ["*", "192.168.0.241"]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',  # Bu **majburiy**
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',


    # Project apps
    'apps',
    'user',
    'analytics',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',

    'social_django',
    'drf_yasg',

    'dj_rest_auth',
    'dj_rest_auth.registration',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Providers
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.instagram',
]


AUTH_USER_MODEL = 'user.CustomUser'  # <-- user emas, users

# ================= REST FRAMEWORK =====================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


REST_USE_JWT = True

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


# =================== MIDDLEWARE =======================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

MIDDLEWARE += [
    'apps.middleware.UTMMiddleware',
]


ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


# ====================== TEMPLATES =========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

# ==================== DATABASE ============================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ================= STATIC / MEDIA ==============================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"


# ================== CUSTOM USER MODEL ===========================

AUTHENTICATION_BACKENDS = [
    'user.backends.UsernameOrEmailOrPhoneBackend',
    'django.contrib.auth.backends.ModelBackend',
]



# ===================== ALLAUTH ==============================
SITE_ID = 1

ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email', 'password1', 'password2']


# ===================== SOCIAL AUTH =============================
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": "YOUR_GOOGLE_ID",
            "secret": "YOUR_GOOGLE_SECRET",
            "key": ""
        }
    },
    "facebook": {
        "APP": {
            "client_id": "YOUR_FB_ID",
            "secret": "YOUR_FB_SECRET",
        }
    },
    "instagram": {
        "APP": {
            "client_id": "YOUR_IG_ID",
            "secret": "YOUR_IG_SECRET",
            "key": ""
        }
    }
}

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "YOUR_GOOGLE_ID"
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "YOUR_GOOGLE_SECRET"

SOCIAL_AUTH_FACEBOOK_KEY = "YOUR_FB_ID"
SOCIAL_AUTH_FACEBOOK_SECRET = "YOUR_FB_SECRET"


# ==================== CHANNELS (REDIS) ===========================

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# ======================= CELERY ================================
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_TIMEZONE = 'Asia/Tashkent'
CELERY_ENABLE_UTC = False

# Beat KERAK EMAS → OCHIRILADI

from celery.schedules import crontab

from celery.schedules import crontab

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'auto-penalty-check-every-minute': {
        'task': 'apps.tasks.auto_penalty_checker',
        'schedule': crontab(minute='*/1'),
    },
    'process-lead-commission-every-minute': {
        'task': 'apps.tasks.process_lead_commission_all_sold',
        'schedule': crontab(minute='*/1'),
    },
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}



LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True
USE_TZ = True


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


STATIC_ROOT = BASE_DIR / "staticfiles"

