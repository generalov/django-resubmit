# coding: utf-8
from __future__ import absolute_import

import os

from django import forms
from django import template
from django.http import HttpResponse
from django_webtest import WebTest
from django.conf.urls.defaults import patterns, url, include
from .tools import MediaStub

from ..widgets import FileWidget


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

