"""
Django settings for rental API project.

In Node.js, this would be similar to your config.js or environment setup files
where you configure your Express app, database connections, middleware, etc.
"""

from pathlib import Path
from decouple import config
import os

# Build paths inside the project
# Similar to __dirname in Node.js
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Similar to JWT_SECRET or SESSION_SECRET in Node.js
SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-change-this')

# SECURITY WARNING: don't run with debug turned on in production!
# Similar to NODE_ENV === 'development' in Node.js
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)

# Similar to CORS allowed origins in Node.js
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
# Similar to registering routes/controllers in Express.js
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',  # PostGIS support for geolocation

    # Third party apps
    'rest_framework',  # Similar to Express + body-parser + routing
    'corsheaders',     # Similar to cors middleware in Express
    'django_filters',  # Similar to query-string parsing in Express

    # Our app
    'backend.rentals',
]

# Middleware (similar to Express middleware stack)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files in production
    'corsheaders.middleware.CorsMiddleware',  # CORS - must be before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS settings (similar to cors options in Express)
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only for development

# Production CORS - use environment variable
if not DEBUG:
    CORS_ALLOWED_ORIGINS = config(
        'CORS_ALLOWED_ORIGINS',
        default='https://your-app.vercel.app'
    ).split(',')
else:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",  # React/Next.js frontend
        "http://localhost:8080",  # Vue frontend
    ]

ROOT_URLCONF = 'backend.config.urls'

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

WSGI_APPLICATION = 'backend.config.wsgi.application'

# Database configuration
# Similar to Sequelize, TypeORM, or Prisma config in Node.js
import dj_database_url

# Use DATABASE_URL in production (Railway/Render), individual vars in development
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Production: Use DATABASE_URL (Railway/Render auto-provides this)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            engine='django.contrib.gis.db.backends.postgis'
        )
    }
else:
    # Development: Use individual environment variables
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',  # PostGIS engine
            'NAME': config('POSTGRES_DB', default='rental_db'),
            'USER': config('POSTGRES_USER', default='rental_user'),
            'PASSWORD': config('POSTGRES_PASSWORD', default='rental_password'),
            'HOST': config('POSTGRES_HOST', default='localhost'),
            'PORT': config('POSTGRES_PORT', default='5432'),
            'OPTIONS': {
                'options': '-c search_path=public'
            }
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise configuration for serving static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
# Similar to configuring response formatting in Express
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,  # Similar to limit in SQL queries
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Nice web UI for testing
    ],
    # Response format settings
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
}

# GDAL library path (required for PostGIS)
if os.name == 'nt':  # Windows
    GDAL_LIBRARY_PATH = config('GDAL_LIBRARY_PATH', default=None)
    GEOS_LIBRARY_PATH = config('GEOS_LIBRARY_PATH', default=None)
