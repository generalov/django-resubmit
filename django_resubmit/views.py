# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django_resubmit.storage import TemporaryFileStorage
from django.core.cache import get_cache
from django.conf import settings
import Image
from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile

from django_resubmit.storage import get_default_storage


def thumbnail(request):
    try:
        key = request.GET['key']
        name = request.GET['name']
        width = int(request.GET['width'])
        height = int(request.GET['height'])
        storage = get_default_storage()

        restored = storage.get_file(key, name)
        if not restored:
            raise
        restored.seek(0)
        img = Image.open(restored.file)
        img.thumbnail([width, height], Image.ANTIALIAS)
        buf = StringIO()
        img.save(buf, img.format)
        buf.seek(0)
        thumb = SimpleUploadedFile(restored.name, buf.read(), restored.content_type)
        buf.close()
        response = HttpResponse(FileWrapper(thumb), content_type=restored.content_type)
    except:
        response = HttpResponse('', content_type='image/jpg')
    return response



