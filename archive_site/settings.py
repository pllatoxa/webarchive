import os
from pathlib import Path

# ======================
# BASE
# ======================

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in (
        "1", "true", "yes", "y", "on"
    )


def env_list(name, default=""):
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]


# ======================
# SECURITY
# ======================

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-CHANGE_THIS")
DEBUG = env_bool("DJANGO_DEBUG", False)

RENDER_HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME", "").strip()

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,.railway.app,.onrender.com,webarchive.com")
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)
ALLOWED_HOSTS += ["localhost", "127.0.0.1"]

CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "https://web-production-d4846.up.railway.app,https://webarchive.com,https://*.onrender.com",
)
if RENDER_HOST:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_HOST}")


# ======================
# APPLICATIONS
# ======================

INSTALLED_APPS = [
    # django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # apps
    "hub",
    "archive.apps.ArchiveConfig",

    # third-party
    "social_django",
]


# ======================
# MIDDLEWARE
# ======================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]


# ======================
# URLS / WSGI
# ======================

ROOT_URLCONF = "archive_site.urls"

WSGI_APPLICATION = "archive_site.wsgi.application"


# ======================
# TEMPLATES
# ======================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]


# ======================
# DATABASE
# ======================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ======================
# PASSWORDS
# ======================

AUTH_PASSWORD_VALIDATORS = []


# ======================
# LOCALIZATION
# ======================

LANGUAGE_CODE = "ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True


# ======================
# STATIC / MEDIA
# ======================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = []
if (BASE_DIR / "static").exists():
    STATICFILES_DIRS.append(BASE_DIR / "static")

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
WHITENOISE_USE_FINDERS = True

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ======================
# EMAIL
# ======================

# Почта: по умолчанию пишем в консоль (Render часто режет SMTP). Включай SMTP через EMAIL_USE_SMTP=1.
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_USE_SMTP = env_bool("EMAIL_USE_SMTP", False)
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend" if EMAIL_USE_SMTP else "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
# Fallback, чтобы не падать, если переменные не заданы
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL") or EMAIL_HOST_USER or "noreply@webarchive.com"
SERVER_EMAIL = os.environ.get("SERVER_EMAIL") or DEFAULT_FROM_EMAIL


# ======================
# AUTH / SOCIAL AUTH
# ======================

AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", ""
)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", ""
)

SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = os.environ.get(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI",
    f"https://{RENDER_HOST}/oauth/complete/google-oauth2/"
    if RENDER_HOST
    else "http://127.0.0.1:8000/oauth/complete/google-oauth2/",
)

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ["email", "profile"]

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "archive.pipeline.save_profile",
)

SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/"
SOCIAL_AUTH_LOGIN_ERROR_URL = "/login-error/"

# Django auth redirects
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"


# ======================
# MISC
# ======================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
