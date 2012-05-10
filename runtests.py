#!/usr/bin/env python

# Application test settings

from django_resubmit.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = ['django_resubmit']

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    'resubmit': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/resubmit-data',
    }
}

STATIC_URL = '/static/'

ROOT_URLCONF = ''


# Configure settings

import sys
from django.conf import settings

settings.configure(**dict([(k,v) for k,v in globals().items() if k.isupper()]))

# setup.py test runner
def runtests():
    from django.test.utils import get_runner

    test_runner = get_runner(settings)(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(INSTALLED_APPS)
    sys.exit(failures)


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv[:1] + ['test'] + sys.argv[1:])
