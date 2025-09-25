import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security ---
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1")
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost").split(",")
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "False").lower() in ("true", "1")

# --- Applications ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'mozilla_django_oidc',
    'drf_spectacular',
    'corsheaders',
    'src.users',
    'src.catalog',
    'src.orders',
    'src.tests',
    'src.core',

]

# --- Middleware ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'src.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'src.config.wsgi.application'

# --- Database ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set in .env")

DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

# --- Email ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# --- Django REST Framework + OIDC ---
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'mozilla_django_oidc.contrib.drf.OIDCAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# --- Auth0 OIDC ---
AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = (
    "src.users.backends.MyOIDCBackend",
    "django.contrib.auth.backends.ModelBackend",
)

OIDC_RP_SIGN_ALGO = "RS256"

LOGIN_URL = "/oidc/authenticate/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
OIDC_RP_CLIENT_ID = os.getenv("OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = os.getenv("OIDC_RP_CLIENT_SECRET")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")

# Build endpoints dynamically from domain
OIDC_OP_AUTHORIZATION_ENDPOINT = f"https://{AUTH0_DOMAIN}/authorize"
OIDC_OP_TOKEN_ENDPOINT = f"https://{AUTH0_DOMAIN}/oauth/token"
OIDC_OP_USER_ENDPOINT = f"https://{AUTH0_DOMAIN}/userinfo"
OIDC_OP_JWKS_ENDPOINT = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"

# --- Auth0 M2M (Management API App) ---
AUTH0_M2M_CLIENT_ID = os.getenv("AUTH0_M2M_CLIENT_ID")
AUTH0_M2M_CLIENT_SECRET = os.getenv("AUTH0_M2M_CLIENT_SECRET")
AUTH0_M2M_AUDIENCE = os.getenv("AUTH0_M2M_AUDIENCE")


OIDC_RP_SCOPES = "openid email profile"

# --- Africa's Talking ---
AFRICA_TALKING_USERNAME = os.getenv("AFRICA_TALKING_USERNAME")
AFRICA_TALKING_APIKEY = os.getenv("AFRICA_TALKING_APIKEY")
AFRICA_TALKING_CODE = os.getenv("AFRICA_TALKING_CODE")

# --- API Docs ---
SPECTACULAR_SETTINGS = {
    'TITLE': 'Savannah Backend API',
    'DESCRIPTION': 'Backend API documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'oauth2': ['openid', 'email', 'profile']}],
    'COMPONENTS': {
        'securitySchemes': {
            'oauth2': {
                'type': 'oauth2',
                'flows': {
                    'authorizationCode': {
                        'authorizationUrl': f"https://{AUTH0_DOMAIN}/authorize",
                        'tokenUrl': f"https://{AUTH0_DOMAIN}/oauth/token",
                        'scopes': {
                            'openid': 'OpenID Connect scope',
                            'email': 'Access to email',
                            'profile': 'Access to profile',
                        },
                    }
                },
            }
        }
    }
}


# --- Static & Media ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

import src.config.spectacular_extensions
