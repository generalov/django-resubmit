import settings
from django.conf.urls.static import static
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('example.views',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^django_resubmit/', include('django_resubmit.urls', namespace="django_resubmit")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
