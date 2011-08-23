import os

from django_webtest import WebTest
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.models import User
from django_resubmit.tests import MediaStub


class AdminEditTopicTest(WebTest):
    urls = __name__

    def setUp(self):
        global urlpatterns
        self.app.relative_to = os.path.join(os.path.dirname(__file__))
        self.media = MediaStub(media_url='/media/')
        self.superuser = User.objects.create_superuser(
                username=u'admin',
                email=u'admin@admin.com',
                password=u'letmein')
        urlpatterns = patterns('',
            url(r'^admin/', include(admin.site.urls)),
            url(r'^django_resubmit/', include('django_resubmit.urls', namespace="django_resubmit")),
            *self.media.url_patterns())

        response = self.app.get('/admin/testapp/topic/add/',
                user=self.superuser)
        form = response.forms['topic_form']
        form.set('title', u"Penguin")
        form.set('icon', ["fixtures/penguin.png"])
        post = form.submit(u"_continue")
        self.topic = post.follow().context["original"]

    def tearDown(self):
        self.media.dispose()

    def test_should_see_icon_preview(self):
        response = self.app.get('/admin/testapp/topic/%d/' % self.topic.pk,
                user=self.superuser)
        preview_url = response.lxml.xpath("//img[contains(@class, 'resubmit-preview__image')]")[0].attrib.get('src')
        self.assertTrue(preview_url,
                "Preview url should be not empty")
        preview_response = self.app.get(preview_url)
        self.assertEquals(200, preview_response.status_int,
                u"preview available for download")


from django.contrib import admin
admin.autodiscover()
