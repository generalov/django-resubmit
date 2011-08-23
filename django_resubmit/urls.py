# coding: utf-8
from __future__ import absolute_import

from django.conf.urls.defaults import patterns, url
from .views import Preview, Resubmit


urlpatterns = patterns('django_resubmit.views',
    url(r'^$', Resubmit.as_view(), name='create'),
    url(r'^preview/$', Preview.as_view(), name='preview'),
)
