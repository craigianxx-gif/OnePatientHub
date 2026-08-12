import os
from pathlib import Path


# ==========================================
# BASE DIRECTORY
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================
# SECURITY
# ==========================================

SECRET_KEY = (
    "django-insecure-change-this-key"
)


DEBUG = True


ALLOWED_HOSTS = []


# ==========================================
# INSTALLED APPLICATIONS
# ==========================================

INSTALLED_APPS = [

    # Django Core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",


    # REST API
    "rest_framework",
    "rest_framework.authtoken",  # Added for Token Authentication
    "django_filters",


    # OnePatient Hub Applications
    "accounts.apps.AccountsConfig",
    "dashboard",
    "patients",
    "visits",
    "referrals",
    "billing",
    "reports",
    "api",
    "hiv_testing",
    "audit",
    "facilities",
    "consent",

]


# ==========================================
# MIDDLEWARE
# ==========================================

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]


# ==========================================
# URL CONFIGURATION
# ==========================================

ROOT_URLCONF = "config.urls"


# ==========================================
# TEMPLATES
# ==========================================

TEMPLATES = [

    {

        "BACKEND": (

            "django.template.backends."

            "django.DjangoTemplates"

        ),

        "DIRS": [

            BASE_DIR / "templates"

        ],

        "APP_DIRS": True,

        "OPTIONS": {

            "context_processors": [

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.pending_account_requests",

            ],

        },

    },

]


# ==========================================
# WSGI / ASGI
# ==========================================

WSGI_APPLICATION = "config.wsgi.application"

ASGI_APPLICATION = "config.asgi.application"


# ==========================================
# DATABASE
# ==========================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "onepatienthub"),
        "USER": os.environ.get("POSTGRES_USER", "craigianxx"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "1629"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}


# ==========================================
# PASSWORD VALIDATION
# ==========================================

AUTH_PASSWORD_VALIDATORS = []


# ==========================================
# INTERNATIONALIZATION
# ==========================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Harare"

USE_I18N = True

USE_TZ = True


# ==========================================
# STATIC FILES
# ==========================================

STATIC_URL = "static/"


# ==========================================
# DEFAULT PRIMARY KEY
# ==========================================

DEFAULT_AUTO_FIELD = (

    "django.db.models.BigAutoField"

)


# ==========================================
# AUTHENTICATION REDIRECTS
# ==========================================

LOGIN_URL = "/"

LOGIN_REDIRECT_URL = "/dashboard/"

LOGOUT_REDIRECT_URL = "/"


# ==========================================
# EMAIL CONFIGURATION
# ==========================================

# Development mode:
# Emails will be printed in the terminal.

EMAIL_BACKEND = (

    "django.core.mail.backends.console.EmailBackend"

)


DEFAULT_FROM_EMAIL = (

    "OnePatient Hub Administration "

    "<noreply@onepatienthub.org>"

)


# ==========================================
# FHIR API SETTINGS
# ==========================================

# Prevent Django from automatically appending slashes to FHIR routes
APPEND_SLASH = False

# Tell Django REST Framework to use our custom FHIR error handler, Token Auth, and IsAuthenticated permissions
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'api.exceptions.fhir_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}