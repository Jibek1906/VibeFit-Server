from pathlib import Path
import os
from dotenv import load_dotenv


load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'your-secret-key'


SESSION_ENGINE = 'django.contrib.sessions.backends.db'


LOGIN_REDIRECT_URL = '/users/profile/'


DEBUG = True


ALLOWED_HOSTS = []


DATE_INPUT_FORMATS = ['%Y-%m-%d']


CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = True


CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000']
INSTALLED_APPS = [
   'django.contrib.admin',
   'django.contrib.auth',
   'django.contrib.contenttypes',
   'django.contrib.sessions',
   'django.contrib.messages',
   'django.contrib.staticfiles',
   'users',
   'workouts',
   'nutrition',
   'rest_framework',
]


MIDDLEWARE = [
   'django.middleware.security.SecurityMiddleware',
   'django.contrib.sessions.middleware.SessionMiddleware',
   'django.middleware.common.CommonMiddleware',
   'django.middleware.csrf.CsrfViewMiddleware',
   'django.contrib.auth.middleware.AuthenticationMiddleware',
   'django.contrib.messages.middleware.MessageMiddleware',
   'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'vibefit.urls'


AUTHENTICATION_BACKENDS = [
   'django.contrib.auth.backends.ModelBackend',
   'users.backends.EmailAuthBackend',
]


TEMPLATES = [
   {
       'BACKEND': 'django.template.backends.django.DjangoTemplates',
       'DIRS': ['templates'],
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


WSGI_APPLICATION = 'vibefit.wsgi.application'

CACHES = {
   'default': {
       'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
       'TIMEOUT': 3600 * 6,
   }
}


DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.sqlite3',
       'NAME': BASE_DIR / 'db.sqlite3',
   }
}


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


LANGUAGE_CODE = 'en-us'


TIME_ZONE = 'UTC'


USE_I18N = True


USE_TZ = True


STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
   BASE_DIR / "vibefit/static",
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'