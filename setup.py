#!/usr/bin/env python
# coding: utf-8
import sys, itertools

version = __import__('django_resubmit').__version__
description = __import__('django_resubmit').__doc__.split('\n')[0]
long_description = open('README.rst', 'r').read()
install_requires = filter(None,
        itertools.takewhile(lambda x: x != '# testing',
        open('requirements.txt').read().split('\n')))

setup_data = {
    'name': 'django-resubmit',
    'version': version,
    'description': description,
    'long_description': long_description,
    'license': 'BSD',
    'packages': [
        'django_resubmit',
        'django_resubmit.thumbnailer'],
    'package_data': {
        'django_resubmit': [
            'static/django_resubmit/*',
            'templates/django_resubmit/*',
        ]
    },
    'install_requires': install_requires,
    'platforms': "All",
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
}

setuptools_extensions = {
    'zip_safe': True,
    'test_suite': "runtests.runtests",
    #'include_package_data': True,
}

if 'develop' in sys.argv:
    setup_data['scripts'] = ['runtests.py']

try:
    from setuptools import setup
    setup_data.update(setuptools_extensions)
except ImportError:
    print("Cannot load setuptool, revert to distutils")
    from distutils.core import setup

setup(**setup_data)
