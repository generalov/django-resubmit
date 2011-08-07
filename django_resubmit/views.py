# coding: utf-8
from __future__ import absolute_import

from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound
from django.utils import simplejson
from django.views.generic.base import View

from .storage import get_default_storage
from .thumbnails import ThumbnailFactory
from .conf import settings


class Preview(View):

    def get(self, *args, **kwargs):
        key = self.kwargs['key']
        width, height = settings.RESUBMIT_THUMBNAIL_SIZE
        thumbnail = self._thumbnail(key, width, height)
        
        if thumbnail:
            return HttpResponse(FileWrapper(thumbnail), content_type=thumbnail.content_type)
        return HttpResponseNotFound(key)

    def post(self, *args, **kwargs):
        if not self.request.FILES:
            return HttpResponse(status=200,
                    content_type="text/plain",
                    content=simplejson.dumps({'error': "file is required"}))
        storage = get_default_storage()
        #key = storage.put_file(self.request.FILES.values()[0], key=self.kwargs['key'])
        upload = self.request.FILES.values()[0]
        key = storage.put_file(upload)
        data = {'preview': { 'url': reverse('django_resubmit:preview', args=[key])},
                'key': key,
                'upload': {'name': upload.name}
                }
        return HttpResponse(status=201,
                content_type="text/plain; charset=utf-8",
                content = simplejson.dumps(data))
        
    def _thumbnail(self, key, width, height):
        storage = get_default_storage()
        restored = storage.get_file(key, u'dummy-field-name')
        if not restored:
            return None
        buf = StringIO()
        try:
            thumbnail = ThumbnailFactory().thumbnail(restored, width, height)
            thumbnail.write(buf)
            return SimpleUploadedFile(restored.name, buf.getvalue(), restored.content_type)
        except IOError:
            return None


class Resubmit(View):

    def post(self, *args, **kwargs):
        if not self.request.FILES:
            return HttpResponse(status=200,
                    content_type="text/plain",
                    content=simplejson.dumps({'error': "file is required"}))

        storage = get_default_storage()
        key = storage.put_file(self.request.FILES.values()[0])
            
        data = {'preview': { 'url': reverse('django_resubmit:preview', args=[key])},
                'key': key}
        return HttpResponse(status=201,
                content_type="text/plain; charset=utf-8",
                content = simplejson.dumps(data))

