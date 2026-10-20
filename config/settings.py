"""Sterr Agency — Django settings. Every secret/deploy value comes from .env."""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-insecure-change-me")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS", default=["sterragency.com", "www.sterragency.com", "localhost", "127.0.0.1"]
)
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS", default=["https://sterragency.com", "https://www.sterragency.com"]
)
# Render sets this to the service's *.onrender.com host; allow it so the deploy
# works before the custom domain is attached.
RENDER_EXTERNAL_HOSTNAME = env("RENDER_EXTERNAL_HOSTNAME", default="")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# Canonical origin used for canonical URLs, sitemap and OG tags (no trailing slash).
SITE_URL = env("SITE_URL", default="https://sterragency.com").rstrip("/")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "apps.core",
    "apps.leads",
    "apps.works",
    "apps.seo",
    "apps.dental",
    "apps.intl",
    "apps.growth",
]

MIDDLEWARE = [
    "apps.core.health.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "apps.core.middleware.CanonicalHostMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Local: SQLite. Production (Render): DATABASE_URL to Postgres, e.g. Supabase's
# "Session pooler" connection string (Render has no IPv6, so not the direct one).
DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = env.path("MEDIA_ROOT", default=BASE_DIR / "media")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        if not DEBUG
        else "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

# Uploaded media on S3-compatible storage (Supabase Storage, R2, S3). Render's own
# disk is wiped on every deploy, so production uploads must live here or on a
# Render persistent disk (MEDIA_ROOT=/var/data/media).
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")
if AWS_STORAGE_BUCKET_NAME:
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "access_key": env("AWS_ACCESS_KEY_ID"),
            "secret_key": env("AWS_SECRET_ACCESS_KEY"),
            "endpoint_url": env("AWS_S3_ENDPOINT_URL", default=None),
            "region_name": env("AWS_S3_REGION_NAME", default=None),
            # Public URL host+path, e.g. <ref>.supabase.co/storage/v1/object/public/media
            "custom_domain": env("AWS_S3_CUSTOM_DOMAIN", default=None),
            "addressing_style": "path",
            "signature_version": "s3v4",
            "querystring_auth": False,
            "file_overwrite": False,
            "default_acl": None,
        },
    }
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Email (Resend HTTP API) ------------------------------------------------
RESEND_API_KEY = env("RESEND_API_KEY", default="")
if RESEND_API_KEY:
    EMAIL_BACKEND = "apps.leads.resend_backend.ResendEmailBackend"
else:
    # Local dev without a key: print emails to the console.
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="Sterr Agency <noreply@sterragency.com>")
# Who gets the "yeni lead geldi" email. Comma-separated for multiple recipients.
LEAD_NOTIFY_EMAILS = env.list("LEAD_NOTIFY_EMAILS", default=[])

# --- Stripe (organic Instagram growth subscription) -------------------------------
# Run `python manage.py setup_stripe` once with STRIPE_SECRET_KEY set; it creates the
# $99/month price, the customer portal and the webhook, and prints the other values.
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_PRICE_ID = env("STRIPE_PRICE_ID", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")
STRIPE_PORTAL_CONFIG = env("STRIPE_PORTAL_CONFIG", default="")
GROWTH_PRICE_USD = env.int("GROWTH_PRICE_USD", default=99)

# --- Contact ----------------------------------------------------------------
WHATSAPP_NUMBER = env("WHATSAPP_NUMBER", default="905414487561")
WHATSAPP_DISPLAY = env("WHATSAPP_DISPLAY", default="+90 541 448 75 61")
CONTACT_EMAIL = env("CONTACT_EMAIL", default="hello@sterragency.com")

# --- Analytics (optional) ---------------------------------------------------
# sterragency.com GA4 property. Off in local dev (DEBUG) unless set in .env, so
# test traffic never reaches the live reports.
GA4_ID = env("GA4_ID", default="" if DEBUG else "G-XZTV0GHKJ2")
# GA4 → Admin → Data streams → Measurement Protocol API secrets. Enables server-side
# lead lifecycle events (qualify_lead, close_convert_lead…) from the admin.
GA4_API_SECRET = env("GA4_API_SECRET", default="")
GTM_ID = env("GTM_ID", default="")
META_PIXEL_ID = env("META_PIXEL_ID", default="")
GOOGLE_SITE_VERIFICATION = env("GOOGLE_SITE_VERIFICATION", default="")

# Serve uploaded media through Django in production (fine for a small site;
# put media behind nginx/S3 when traffic grows).
SERVE_MEDIA = env.bool("SERVE_MEDIA", default=True)

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_CONTENT_TYPE_NOSNIFF = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
