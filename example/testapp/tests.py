import os
import re

from django_webtest import WebTest
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.models import User
from django_resubmit.test import MediaStub


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

        preview_match = re.search(ur'<img alt="preview" src="([^"]+)" />',
                response.unicode_body)
        self.assertTrue(preview_match,
                u"page contains an <img> tag with preview")
        preview_url = preview_match.group(1)
        preview_response = self.app.get(preview_url)
        self.assertEquals(200, preview_response.status_int,
                u"preview available for download")


from django.contrib import admin
admin.autodiscover()
