from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('django_resubmit.views',
    url(r'^$', 'thumbnail', name='thumbnail'),
)
