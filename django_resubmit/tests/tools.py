from shutil import rmtree
from tempfile import mkdtemp
from StringIO import StringIO

from django.conf.urls.defaults import url
from django.core.handlers.wsgi import WSGIRequest
from django.core.handlers.base import BaseHandler
from django.test import Client


class CacheMock(object):
    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        return self._data[key]

    def delete(self, key):
        self._data.pop(key)


# http://djangosnippets.org/snippets/2231/
# Adapted from Simon Willison's snippet: http://djangosnippets.org/snippets/963/.
class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.
    
    Usage:
    
    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})
    
    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client
    
    Once you have a request object you can pass it to any view function, 
    just as if that view had been hooked up using a URLconf.
    
    """
    def request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        request = WSGIRequest(environ)
        
        handler = BaseHandler()
        handler.load_middleware()
        for middleware_method in handler._request_middleware:
            if middleware_method(request):
                raise Exception("Couldn't create request object - "
                                "request middleware returned a response")
        
        return request

    def file(self, name, content=''):
        return ContentFile(content, name=name)


class ContentFile(StringIO):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name')
        StringIO.__init__(self, *args, **kwargs)
        
        

class MediaStub(object):
    """Stub for settings.MEDIA_ROOT and settings.MEDIA_URL."""

    def __init__(self, media_url, media_root=None, settings=None):
        if not settings:
            from django.conf import settings
        self._use_termporary_root = None
        self.old_root = None
        self.old_url = None
        self.show_indexes = False
        self.settings = settings
        self._root = media_root or self._make_temporary_root()
        self._url = media_url or '/media/'
        self._stub_settings()
        self._recreate_default_storage()

    def dispose(self):
        self.settings.MEDIA_ROOT = self.old_root
        self.settings.MEDIA_URL = self.old_url
        if self._use_temporary_root:
            rmtree(self._root)
        self._recreate_default_storage()

    def url_patterns(self):
        """Return list of url patterns for serve static.

        This is situable to append into urls.py"""
        return [
                url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                    'document_root': self.settings.MEDIA_ROOT,
                    'show_indexes': self.show_indexes}),
                ]

    def _stub_settings(self):
        self.old_root = self.settings.MEDIA_ROOT
        self.old_url = self.settings.MEDIA_URL
        self.settings.MEDIA_ROOT = self._root
        self.settings.MEDIA_URL = self._url

    def _make_temporary_root(self):
        """Make temporary directory for media root"""
        self._use_temporary_root = True
        return mkdtemp()

    def _recreate_default_storage(self):
        """Install default storage.

        It is nessesary to reinstall default_storage because of it
        memorizes settings.MEDIA_ROOT and settings.MEDIA_URL
        """
        from django.core.files import storage
        storage.default_storage = storage.DefaultStorage()

        
