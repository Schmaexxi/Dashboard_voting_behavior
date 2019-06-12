import os

from dashboard_voting_behavior.settings import *

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False
ALLOWED_HOSTS = [os.environ['HOST']]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['PGDATABASE'],
        'USER': os.environ['PGUSER'],
        'PASSWORD': os.environ['PGPASSWORD'],
        'HOST': os.environ['PGHOST'],
        'PORT': os.environ['PGPORT'],
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'app': {
            'format': '%(asctime)s [%(process)d] [APP:%(module)s-%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'app'
        },
    },
    'loggers': {
        'gunicorn.errors': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': True
        },
        'django': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': True
        },
        'dashboard_voting_behavior': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': True
        },
    }
}


STATIC_ROOT = 'staticfiles'

