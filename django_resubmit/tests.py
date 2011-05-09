import unittest
from django_webtest import WebTest

from django import forms
from django import template
from django.http import HttpResponse
from django.conf.urls.defaults import patterns, include, url
from django_resubmit.test import CacheMock
from django_resubmit.test import RequestFactory

from django_resubmit.forms.widgets import FileCacheWidget
from django_resubmit.forms.widgets import FILE_INPUT_CONTRADICTION


class HttpResponseOk(HttpResponse):
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
    file = forms.FileField(widget=FileCacheWidget())


def view_upload_file(request):
    if request.method == 'POST':
        form = SampleForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['file']
            f.seek(0)
            return HttpResponseCreated(
                    content=f.read(),
                    content_type="text/plain; charset=utf-8")
    else:
        form = SampleForm()
    t = template.Template(UPLOAD_TEMPLATE)
    data = {'form': form}
    output = t.render(template.RequestContext(request, data))
    return HttpResponseOk(output)


urlpatterns = patterns('',
    url(r'^$', view_upload_file),
)


class FormTest(WebTest):
    urls = 'django_resubmit.tests'

    def test_should_preserve_file_on_form_errors(self):
        response = self.app.get('/')
        form = response.forms[0]
        form['file'] = ['test.txt', u'test content']
        self.assertEquals(sorted(form.fields.keys()),
                [u'csrfmiddlewaretoken', u'file', u'name', u'submit'])

        response = form.submit()
        self.assertEquals(response.status_int, HttpResponseOk.status_code)
        self.assertEquals(len(response.context['form']['file'].errors), 0)
        self.assertEquals(len(response.context['form']['name'].errors), 1)
        form = response.forms[0]
        self.assertEquals(sorted(form.fields.keys()),
                [u'csrfmiddlewaretoken', u'file', u'file-cachekey', u'name', u'submit'])

        form['name'] = u'value for required field'
        response = form.submit()
        self.assertEquals(response.status_int, HttpResponseCreated.status_code, response.body)
        self.assertEquals(response.unicode_body, u'test content')


class ClearTest(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.cache = CacheMock()
        self.widget = FileCacheWidget(cache=self.cache)

    def test_should_not_display_clear_checkbox_then_is_required(self):
        widget = self.widget
        widget.is_required = True
        request = self.factory.post('/', {
            'file': self.factory.file('test.txt', 'test content')})
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        output = widget.render('file', upload)
        self.assertTrue('clear' not in output, output)

    def test_should_display_clear_checkbox_then_does_not_required(self):
        widget = self.widget
        widget.is_required = False
        request = self.factory.post('/', {
            'file': self.factory.file('test.txt', 'test content')})
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        output = widget.render('file', upload)
        self.assertTrue('<input type="checkbox" name="file-clear"' in output, output)

    def test_should_not_to_cache_on_cotradiction(self):
        widget = self.widget
        widget.is_required = False
        request = self.factory.post('/', {
            'file-clear': 'on',
            'file': self.factory.file('test.txt', 'test content')})
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        self.assertEquals(upload, FILE_INPUT_CONTRADICTION)
        self.assertEquals(self.cache._data, {})

    def test_should_clear_cache_when_clear_is_checked_and_no_any_file(self):
        widget = self.widget
        widget.is_required = False
        request = self.factory.post('/', {
            'file': self.factory.file('test.txt', 'test content')})
        widget.value_from_datadict(request.POST, request.FILES, 'file')
        self.assertEquals(len(self.cache._data.keys()), 1, "File should be in the cache")

        request = self.factory.post('/', {
            'file-cachekey': widget.hidden_key,
            'file-clear': 'on',})
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        self.assertEquals(upload, False, "Upload should be False")
        self.assertEquals(self.cache._data, {}, "Cache should be empty")

    def test_should_handle_large_files(self):
        """
        Should handle large files.

        Django handles files larger than FILE_UPLOAD_MAX_MEMORY_SIZE in a
        special way. It places them in real temporary files on the disk.

        I suppose we should store such files on the disk too, and place in
        the cache just metadata.
        """
        widget = self.widget
        widget.is_required = True
        request = self.factory.post('/', {
            'file': self.factory.file('test.txt', 'x' * 10000000)})
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        output = widget.render('file', upload)
        self.assertEquals(len(self.cache._data.keys()), 1, "Should cache large file")
