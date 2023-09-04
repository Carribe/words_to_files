import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-9au#3urwafp*a%)a=+cn0mr_rtrdfytjgujhn7+wvlo8nmwns'

DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1"]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', #'django.db.backends.postgresql_psycopg2'
        'NAME': 'words_to_files',
        'USER': 'artem',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}