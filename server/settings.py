from pathlib import Path
from os import getenv as os_getenv
from secrets import token_hex


# Base settings
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os_getenv("SECRET_KEY", token_hex(32))
DEBUG = bool(os_getenv("DEBUG", True)) # TODO set True to False
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]

ROOT_URLCONF = "server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request"
            ],
        },
    },
]

WSGI_APPLICATION = "server.wsgi.application"


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
