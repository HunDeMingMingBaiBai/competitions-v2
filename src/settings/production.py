from .base import *  # noqa: F401,F403


ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(",")

CORS_ORIGIN_ALLOW_ALL = False
DEBUG = False

# =========================================================================
# SSL
# =========================================================================
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True


# =========================================================================
# Email
# =========================================================================
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
