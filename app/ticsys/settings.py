import environ
from pathlib import Path

env = environ.Env(
    DEBUG=(bool, False),
    PROTOCOL=(str, "https"),
    EMAIL_HOST=(str, "localhost"),
    EMAIL_PORT=(int, 465),
    EMAIL_USE_SSL=(bool, True),
    EMAIL_IMAP_PORT=(int, 993),
    EMAIL_IMAP_HOST=(str, "localhost"),
    EMAIL_INITIAL_FOLDER=(str, "INBOX"),
    PERIOD_CHECK_EMAIL=(float, 60.0),  # seconds
    SUBJECT_TO_TICKET=(str, "ticket"),
    RABBIT_HOST=(str, "localhost"),
    RABBIT_LOGIN=(str, "guest"),
    RABBIT_PASSWORD=(str, "guest"),
    RABBIT_VHOST=(str, "/"),
    MANAGER_EMAIL=(str, "manager@localhost"),
)
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(BASE_DIR / ".env")

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS").split(" ")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS").split(" ")
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "additionally",
    "ticsys",
    "ticket",
    "users",
    "notifications",
    "reports",
]

SITE_ID = 1
PROTOCOL = env("PROTOCOL")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ticsys.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ticsys.wsgi.application"

DATABASES = {
    "default": env.db(),
}
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-RU"

USE_I18N = True

TIME_ZONE = "Europe/Moscow"

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = str(BASE_DIR / "static")

MEDIA_ROOT = str(BASE_DIR / "media")
MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

TICKET_CREATOR_USERNAME = "email_robot"
# Ticket email
DEFAULT_FROM_EMAIL = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_USE_SSL = env("EMAIL_USE_SSL")
EMAIL_IMAP_PORT = env("EMAIL_IMAP_PORT")
EMAIL_IMAP_HOST = env("EMAIL_IMAP_HOST")
SUBJECT_TO_TICKET = env("SUBJECT_TO_TICKET")

EMAIL_INITIAL_FOLDER = env("EMAIL_INITIAL_FOLDER")
PERIOD_CHECK_EMAIL = env("PERIOD_CHECK_EMAIL")

RABBIT_HOST = env("RABBIT_HOST")
RABBIT_LOGIN = env("RABBIT_LOGIN")
RABBIT_PASSWORD = env("RABBIT_PASSWORD")
RABBIT_VHOST = env("RABBIT_VHOST")

CELERY_BROKER_URL = (
    f"amqp://{RABBIT_LOGIN}:{RABBIT_PASSWORD}@{RABBIT_HOST}/{RABBIT_VHOST}"
)
CELERY_ACCEPT_CONTENT = ("application/json",)
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"

MANAGER_EMAIL = env("MANAGER_EMAIL")
