import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-9au#3urwafp*a%)a=+cn0mr_r5ft80w4o0ln+n7+wvlo8nmwns'

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'artem',
        'USER': 'artem',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}