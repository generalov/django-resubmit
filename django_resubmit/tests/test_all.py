# coding: utf-8
from __future__ import absolute_import

import os
import unittest

from django import forms
from django import template
from django.http import HttpResponse
from django.conf.urls.defaults import patterns, url, include
from django.test import TestCase
from django_webtest import WebTest
from .tools import CacheMock
from .tools import MediaStub
from .tools import RequestFactory

from ..widgets import FileWidget
from ..widgets import FILE_INPUT_CONTRADICTION
from ..storage import CacheTemporaryStorage


class HttpResponseOk(HttpResponse):
    status_code = 200


class HttpResponseValidationError(HttpResponse):
    status_code = 200


class HttpResponseCreated(HttpResponse):
    status_code = 201


UPLOAD_TEMPLATE = u"""
<html>
  <body>
    <form action="." method="post" enctype="multipart/form-data">
      {% csrf_token %}
      {{ form.as_p }}
      <input type="submit" name="submit" />
      </form>
  </body>
</html>
"""


class SampleForm(forms.Form):
    name = forms.CharField(max_length=25)
    file = forms.FileField(widget=FileWidget)


def view_upload_file(request):
    if request.method == 'POST':
        form = SampleForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['file']
            f.seek(0)
            return HttpResponseCreated(
                    content=f.read(),
                    content_type="text/plain; charset=utf-8")
        Response = HttpResponseValidationError
    else:
        form = SampleForm()
        Response = HttpResponseOk
    t = template.Template(UPLOAD_TEMPLATE)
    data = {'form': form}
    output = t.render(template.RequestContext(request, data))
    return Response(output)


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
        f.write("some data")
        f.close()
        response = self.client.get(settings.MEDIA_URL + "upload.txt")
        self.assertEquals(response.status_code, HttpResponseOk.status_code)
        self.assertEquals(response.content, "some data")

    def test_should_get_file_using_media_url(self):
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        default_storage.save("upload.txt", ContentFile("some data"))
        response = self.client.get("/media/upload.txt")
        self.assertEquals(response.status_code, HttpResponseOk.status_code)
        self.assertEquals(response.content, "some data")


class FormTest(WebTest):
    urls = __name__

    def setUp(self):
        global urlpatterns
        urlpatterns = patterns('',
            url(r'^$', view_upload_file),
            url(r'^thumbnail/', include('django_resubmit.urls', namespace='django_resubmit')),
        )
        self.app.relative_to = os.path.join(os.path.dirname(__file__), '..')
        self.media = MediaStub(media_url='/media/')

    def tearDown(self):
        self.media.dispose()

    def test_should_preserve_file_on_form_errors(self):
        response = self.app.get('/')
        form = response.forms[0]
        form['file'] = ['test.txt', u'test content']

        response = form.submit()
        self.assertEquals(response.status_int, HttpResponseValidationError.status_code)
        self.assertEquals(len(response.context['form']['file'].errors), 0)
        self.assertEquals(len(response.context['form']['name'].errors), 1)
        form = response.forms[0]

        form['name'] = u'value for required field'
        response = form.submit()
        self.assertEquals(response.status_int, HttpResponseCreated.status_code, response.body)
        self.assertEquals(response.unicode_body, u'test content')

    def test_should_show_cached_file_without_link(self):
        response = self.app.get('/')
        form = response.forms[0]
        form['file'] = ['test.txt', u'test content']
        response = form.submit()
        self.assertEquals(response.status_int, HttpResponseValidationError.status_code)

        self.assertTrue('href' not in response.lxml.xpath("//a[contains(@class, 'resubmit-initial')]")[0],
                u"Should show cached file without link")

    def test_if_thumb_is_rendered_on_submit_errors(self):
        """ Check thumb generation for image files on submit errors"""

        response = self.app.get('/')

        form = response.forms[0]
        form['file'] = ['fixtures/test-image.png']
        response = form.submit()
        self.assertEquals(response.status_int, HttpResponseValidationError.status_code)

        preview_url = response.lxml.xpath("//img[contains(@class, 'resubmit-preview__image')]")[0].attrib.get('src')
        self.assertTrue(preview_url,
                u"page contains an <img> tag with preview")

        preview_response = self.app.get(preview_url)
        self.assertEquals(preview_response.status_int, HttpResponseOk.status_code,
                u"preview available for download")


class ClearTest(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.widget = FileWidget()

    def test_should_not_display_clear_checkbox_then_is_required(self):
        widget = self.widget
        widget.is_required = True
        request = self.factory.post('/', {
            'file': self.factory.file('test.txt', 'test content')})
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        output = widget.render('file', upload)
        self.assertTrue('resubmit-clear' not in output, output)

    def test_should_display_clear_checkbox_then_does_not_required(self):
        widget = self.widget
        widget.is_required = False
        request = self.factory.post('/', {
            'file': self.factory.file('test.txt', 'test content')})
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        output = widget.render('file', upload)
        self.assertTrue('resubmit-clear' in output, output)

    def test_should_not_to_hold_a_file_on_cotradiction(self):
        cache = CacheMock()
        self.widget.storage = CacheTemporaryStorage(cache=cache)

        widget = self.widget
        widget.is_required = False
        request = self.factory.post('/', {
            'file-clear': 'on',
            'file': self.factory.file('test.txt', 'test content')})
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        self.assertEquals(upload, FILE_INPUT_CONTRADICTION)
        self.assertEquals(cache._data, {})

    def test_should_clear_when_clear_is_checked_and_no_any_file(self):
        cache = CacheMock()
        self.widget.storage = CacheTemporaryStorage(cache=cache)

        widget = self.widget
        widget.is_required = False
        request = self.factory.post('/', {
            'file': self.factory.file('test.txt', 'test content')})
        widget.value_from_datadict(request.POST, request.FILES, 'file')
        self.assertEquals(len(cache._data.keys()), 1, "File should be hodled")

        request = self.factory.post('/', {
            'file-cachekey': widget.resubmit_key,
            'file-clear': 'on', })
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        self.assertEquals(upload, False, "Upload should be False")
        self.assertEquals(cache._data, {}, "Cache should be empty")

    def test_should_handle_large_files(self):
        """
        Should handle large files.

        Django handles files larger than FILE_UPLOAD_MAX_MEMORY_SIZE in a
        special way. It places them in real temporary files on the disk.

        I suppose we should store such files on the disk too, and place in
        the cache just metadata.
        """
        cache = CacheMock()
        self.widget.storage = CacheTemporaryStorage(cache=cache)

        widget = self.widget
        request = self.factory.post('/', {
            'file': self.factory.file('test.txt', 'x' * 10000000)})
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        output = widget.render('file', upload)
        self.assertEquals(len(cache._data.keys()), 1, "Should to remember large file")

