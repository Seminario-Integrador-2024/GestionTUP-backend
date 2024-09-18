# ruff: noqa: ERA001, E501
"""Base settings to build other settings files upon."""
# classy drf docs
# https://www.cdrf.co/
import datetime
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
# server/
APPS_DIR = BASE_DIR / "server"
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "America/Argentina/Cordoba"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "es-ar"
# https://docs.djangoproject.com/en/dev/ref/settings/#languages
# from django.utils.translation import gettext_lazy as _
# LANGUAGES = [
#     ('en', _('English')),
#     ('fr-fr', _('French')),
#     ('pt-br', _('Portuguese')),
# ]
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [str(BASE_DIR / "locale")]

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    # "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "django.contrib.admin",
    "django.forms",
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "allauth.socialaccount",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "dj_rest_auth",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
]

LOCAL_APPS = [
    "server.users",
    "server.alumnos",
    "server.materias",
    "server.pagos",
    "server.excel",
    # Your stuff: custom apps go here
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "server.contrib.sites.migrations"}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "users:redirect"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(BASE_DIR / "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR / "static")]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR / "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#dirs
        "DIRS": [str(APPS_DIR / "templates")],
        # https://docs.djangoproject.com/en/dev/ref/settings/#app-dirs
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "server.users.context_processors.allauth_settings",
            ],
        },
    },
]

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""Seminario-Integrador-2024""", "eduferreyraok@gmail.com")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
# https://cookiecutter-django.readthedocs.io/en/latest/settings.html#other-environment-settings
# Force the `admin` sign in process to go through the `django-allauth` workflow
DJANGO_ADMIN_FORCE_ALLAUTH = env.bool("DJANGO_ADMIN_FORCE_ALLAUTH", default=False)

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}


# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = "email"
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_EMAIL_REQUIRED = True
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_USERNAME_REQUIRED = False
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "optional"
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_ADAPTER = "server.users.adapters.AccountAdapter"
# https://docs.allauth.org/en/latest/account/forms.html
ACCOUNT_FORMS = {"signup": "server.users.forms.UserSignupForm"}
# https://docs.allauth.org/en/latest/socialaccount/configuration.html
SOCIALACCOUNT_ADAPTER = "server.users.adapters.SocialAccountAdapter"
# https://docs.allauth.org/en/latest/socialaccount/configuration.html
SOCIALACCOUNT_FORMS = {"signup": "server.users.forms.UserSocialSignupForm"}

# django-rest-framework
# -------------------------------------------------------------------------------
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# djangorestframework-simplejwt
# -------------------------------------------------------------------------------
# djangorestframework-simplejwt - https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": env.int(
        "DJANGO_ACCESS_TOKEN_LIFE",
        default=datetime.timedelta(minutes=3600),
    ),
    "REFRESH_TOKEN_LIFETIME": env.int(
        "DJANGO_REFRESH_TOKEN_LIFE",
        default=datetime.timedelta(days=1),
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "UPDATE_LAST_LOGIN": True,
    "USER_ID_FIELD": "dni",
}

# dj-rest-auth
# -------------------------------------------------------------------------------
# dj-rest-auth - https://dj-rest-auth.readthedocs.io/en/latest/configuration.html
REST_AUTH = {
    "LOGIN_SERIALIZER": "server.users.api.serializers.LoginSerializer",
    "USER_DETAILS_SERIALIZER": "server.users.api.serializers.UserDetailsSerializer",
    "USE_JWT": True,
    "TOKEN_MODEL": None,
    "SESSION_LOGIN": True,
    "JWT_AUTH_SECURE": False,  # if true, JWT will be set with secure flag and only sent over https
    "JWT_AUTH_COOKIE": "access_token",
    "JWT_AUTH_COOKIE_REFRESH": "refresh_token",
    "JWT_AUTH_COOKIE_USE_CSRF": True,  # forces to use CSRF token in the cookie
    "JWT_AUTH_RETURN_EXPIRATION": True,
}

# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
# CORS_URLS_REGEX = r"^/api/.*$"
CORS_ALLOW_ALL_ORIGINS = True
# By Default swagger ui is available only to admin user(s). You can change permission classes to change that
# See more configuration options at https://drf-spectacular.readthedocs.io/en/latest/settings.html#settings
# DRF Spectacular settings
# https://drf-spectacular.readthedocs.io/en/latest/settings.html
SPECTACULAR_SETTINGS = {
    "TITLE": "Gestion TUP API",
    "DESCRIPTION": "API Endpoint Documentation for Gestion TUP",
    "VERSION": "0.1.0",
    "TOS": "https://github.com/Seminario-Integrador-2024/GestionTUP-backend/blob/main/README.md",
    "CONTACT": {
        "name": "API Support",
        "url": "https://github.com/carlosferreyra",
        "email": "eduferreyraok@gmail.com",
    },
    "LICENSE": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    "SERVERS": [
        {
            "url": "{protocol}://{host}{port}/",
            "description": "Development server",
            "variables": {
                "protocol": {
                    "description": "Protocol (http only for now)",
                    "default": "http",
                    "enum": ["http", "https"],
                },
                "host": {
                    "description": "Hostname (FQDN)",
                    "default": "localhost",
                    "enum": [
                        "gestiontup-42tx6kvt3q-uc.a.run.app",
                        "localhost",
                    ],
                },
                "port": {
                    "description": "server port",
                    "default": ":8000",
                    "enum": ["", ":8000"],
                },
            },
        },
    ],
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    "SWAGGER_UI_SETTINGS": {  # Swagger UI settings
        "deepLinking": True,
        "persist authorization": True,
        "showExtensions": True,  # Display vendor-specific extensions
        "showCommonExtensions": True,  # Display common extensions
        "docExpansion": "none",  # Expand operations by default
        "displayOperationId": True,  # Display operationId in operations
        # Appearance and Branding (mostly defaults)
        # Sorting and Filtering (mostly defaults)
        "filter": True,  # Show filtering {true, false, string}
        "operationsSorter": "alpha",  # Sort by method {alpha, method, ordered}
        "tagsSorter": "alpha",  # Sort by tag {alpha, order}
        "withCredentials": False,  # Avoid unless necessary
        "displayRequestDuration": True,  # Display request duration
        # Advanced Options (mostly defaults)
        "syntaxHighlight.activated": True,  # Syntax highlighter flag
        "url": "/api/schema/",  # URL to fetch the OpenAPI schema from
    },
    # OTHER SPECTACULAR SETTINGS
}
# Your stuff...
# ------------------------------------------------------------------------------
