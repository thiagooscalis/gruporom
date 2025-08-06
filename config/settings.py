import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-8z1mj9hc@9l5lv7+u8)#h#k!*ctfr6@$yfn&s6p2)gt=rjx-q#",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG") == "on"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

SITE_URL = os.getenv("SITE_URL", "http://localhost:8000")

# Application definition

INSTALLED_APPS = [
    "daphne",
    "core",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "crispy_bootstrap5",
    "channels",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.middleware.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.cambio_do_dia",
                "core.context_processors.dados_globais",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "gruporom"),
        "USER": os.getenv("DB_USER", "thiago"),
        "PASSWORD": os.getenv("DB_PASS", "teste"),
        "HOST": os.getenv("DB_HOST", ""),
        "ATOMIC_REQUESTS": True,
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

pv = "django.contrib.auth.password_validation"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": f"{pv}.UserAttributeSimilarityValidator",
    },
    {
        "NAME": f"{pv}.MinimumLengthValidator",
    },
    {
        "NAME": f"{pv}.CommonPasswordValidator",
    },
    {
        "NAME": f"{pv}.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = os.getenv("STATIC_ROOT", BASE_DIR / "core" / "static")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model
AUTH_USER_MODEL = "core.Usuario"

LOGIN_URL = "/login/"

LOGOUT_URL = "/logout/"

LOGIN_REDIRECT_URL = "/"

# URLs que não precisam de autenticação (webhooks, APIs públicas)
LOGIN_EXEMPT_URLS = [
    r"^/webhook/",  # Todos os webhooks
    r"^/api/public/",  # APIs públicas futuras
]

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Channels Configuration
ASGI_APPLICATION = "config.asgi.application"

# Channel layer para WebSocket
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "production": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "simple",
            "filters": ["require_debug_true"],
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": (
                "/home/thiago/logs/django.log" if not DEBUG else "django.log"
            ),
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "production" if not DEBUG else "verbose",
        },
        "production_console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "filters": ["require_debug_false"],
        },
    },
    "root": {
        "handlers": ["console"] if DEBUG else ["file"],
        "level": "WARNING" if not DEBUG else "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"] if DEBUG else ["file"],
            "level": "INFO" if DEBUG else "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": (
                ["file", "production_console"]
                if not DEBUG
                else ["console", "file"]
            ),
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": (
                ["file", "production_console"]
                if not DEBUG
                else ["console", "file"]
            ),
            "level": "ERROR",
            "propagate": False,
        },
        "core": {
            "handlers": ["console", "file"] if DEBUG else ["file"],
            "level": "DEBUG" if DEBUG else "WARNING",
            "propagate": False,
        },
    },
}

# ==========================================
# SECURITY SETTINGS
# ==========================================

# Security headers and cookies configuration
if DEBUG is False:
    # CSRF Protection
    CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", SITE_URL).split(
        ","
    )
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = "Strict"
    CSRF_FAILURE_VIEW = "django.views.csrf.csrf_failure"
    CSRF_USE_SESSIONS = False  # Use cookies for better performance

    # Session Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"
    SESSION_COOKIE_AGE = 60 * 60 * 12  # 12 hours
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    SESSION_ENGINE = (
        "django.contrib.sessions.backends.db"  # Database-backed sessions
    )

    # Security Headers
    SECURE_BROWSER_XSS_FILTER = True  # X-XSS-Protection: 1; mode=block
    SECURE_CONTENT_TYPE_NOSNIFF = True  # X-Content-Type-Options: nosniff
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

    # Clickjacking Protection
    X_FRAME_OPTIONS = "DENY"

    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # SSL Redirect
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True") == "True"
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Content Security Policy (basic - customize as needed)
    CSP_DEFAULT_SRC = ("'self'",)
    CSP_SCRIPT_SRC = (
        "'self'",
        "'unsafe-inline'",
        "cdn.jsdelivr.net",
        "cdnjs.cloudflare.com",
    )
    CSP_STYLE_SRC = (
        "'self'",
        "'unsafe-inline'",
        "cdn.jsdelivr.net",
        "cdnjs.cloudflare.com",
        "fonts.googleapis.com",
    )
    CSP_FONT_SRC = ("'self'", "fonts.gstatic.com", "cdnjs.cloudflare.com")
    CSP_IMG_SRC = ("'self'", "data:", "https:")
    CSP_CONNECT_SRC = ("'self'",)
    CSP_FRAME_ANCESTORS = ("'none'",)
    CSP_BASE_URI = ("'self'",)
    CSP_FORM_ACTION = ("'self'",)

    # Permissions Policy (Feature Policy)
    PERMISSIONS_POLICY = {
        "accelerometer": [],
        "camera": [],
        "geolocation": [],
        "gyroscope": [],
        "magnetometer": [],
        "microphone": [],
        "payment": [],
        "usb": [],
    }

    # Additional Security Settings
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # File Upload Security
    FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
    DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
    DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

    # Silenced checks (only if you understand the implications)
    SILENCED_SYSTEM_CHECKS = ["security.W008", "security.W004"]
else:
    # Development settings (less restrictive)
    CSRF_COOKIE_HTTPONLY = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week in dev
    X_FRAME_OPTIONS = "SAMEORIGIN"

# ==========================================
# AUTHENTICATION & PASSWORD SETTINGS
# ==========================================

# Account lockout protection (requires django-axes or similar)
AXES_FAILURE_LIMIT = 5  # Lock after 5 failed attempts
AXES_COOLOFF_TIME = 1  # 1 hour cooldown
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True


# Authentication backend with rate limiting
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# ==========================================
# API & RATE LIMITING
# ==========================================

# REST Framework security (if using DRF)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# ==========================================
# EMAIL SECURITY
# ==========================================

# Email configuration with security
if not DEBUG:
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST = os.getenv("EMAIL_HOST", "")
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
    DEFAULT_FROM_EMAIL = os.getenv(
        "DEFAULT_FROM_EMAIL", "noreply@gruporom.com"
    )
    SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ==========================================
# ADDITIONAL SECURITY MEASURES
# ==========================================

# Prevent host header attacks
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
if not DEBUG:
    # Validate ALLOWED_HOSTS is not using wildcards in production
    for host in ALLOWED_HOSTS:
        if "*" in host:
            raise ValueError(
                "Wildcards in ALLOWED_HOSTS are not allowed in production!"
            )

# Admin security
ADMIN_URL = os.getenv("ADMIN_URL", "admin/")  # Consider changing from default

# Sensitive settings that should never be in code
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-development-key-change-in-production"
    else:
        raise ValueError("SECRET_KEY must be set in production!")

# Database connection pooling and security
DATABASES["default"]["CONN_MAX_AGE"] = 0 if DEBUG else 600
DATABASES["default"]["OPTIONS"] = {
    "sslmode": "prefer" if DEBUG else "require",
}

# Cache security (if using cache)
CACHES = {
    "default": {
        "BACKEND": (
            "django.core.cache.backends.locmem.LocMemCache"
            if DEBUG
            else "django.core.cache.backends.redis.RedisCache"
        ),
        "LOCATION": "redis://127.0.0.1:6379/1" if not DEBUG else "",
        "OPTIONS": (
            {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
            if not DEBUG
            else {}
        ),
        "KEY_PREFIX": "gruporom",
        "TIMEOUT": 300,
    }
}
