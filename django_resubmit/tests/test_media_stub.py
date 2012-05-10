# coding: utf-8
from __future__ import absolute_import

import os
from django.conf.urls.defaults import patterns
from django.test import TestCase
from .tools import b
from .tools import MediaStub


class MediaStubTest(TestCase):
    urls = __name__

    def setUp(self):
        global urlpatterns
        self.media = MediaStub(media_url="/media/")
        urlpatterns = patterns('', *self.media.url_patterns())

    def tearDown(self):
        self.media.dispose()

    def test_should_get_uploaded_file(self):
        from django.conf import settings

        uploaded_path = os.path.join(settings.MEDIA_ROOT, "upload.txt")
        f = open(uploaded_path, 'wb')
        f.write(b("some data"))
        f.close()
        response = self.client.get(settings.MEDIA_URL + "upload.txt")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, b("some data"))

    def test_should_get_file_using_media_url(self):
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        default_storage.save("upload.txt", ContentFile(b("some data")))
        response = self.client.get("/media/upload.txt")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, b("some data"))

