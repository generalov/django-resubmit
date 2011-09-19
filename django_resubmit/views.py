# coding: utf-8
from __future__ import absolute_import

from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, HttpResponseNotFound
from django.utils import simplejson
from django.views.generic.base import View

from .core import get_temporary_storage, get_thumbnail, ThumbnailException


class Preview(View):

    def get(self, *args, **kwargs):
        path = self.request.GET.get('path')

        try:
            thumbnail = get_thumbnail(path)
        except ThumbnailException:
            return HttpResponseNotFound(path)

        return HttpResponse(FileWrapper(thumbnail.as_file()), content_type=thumbnail.mime_type)


class Resubmit(View):

    def post(self, *args, **kwargs):
        if not self.request.FILES:
            return HttpResponse(status=200,
                    content_type='text/plain',
                    content=simplejson.dumps({'error': 'file is required'}))

        previous_key = self.request.GET.get('key', None)
        storage = get_temporary_storage()
        upload = self.request.FILES.values()[0]
        key = storage.put_file(upload)

        if previous_key:
            storage.clear_file(previous_key)

        data = {'key': key,
                'upload': {'name': upload.name}}

        try:
            thumbnail = get_thumbnail(key)
            data['preview'] = {'url': thumbnail.url}
        except ThumbnailException:
            pass

        return HttpResponse(status=201,
                content_type='text/plain; charset=utf-8',
                content = simplejson.dumps(data))

