import dj_database_url
import django_heroku

from .settings import *

django_heroku.settings(locals(), logging=False)

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = True

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
USE_HTTPS_IN_ABSOLUTE_URLS = True

MAX_CONN_AGE = 600

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

if "DATABASE_URL" in os.environ:
    DATABASES["default"] = dj_database_url.config(
        conn_max_age=MAX_CONN_AGE, ssl_require=True
    )
