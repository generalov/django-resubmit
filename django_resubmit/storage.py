# coding: utf-8
import string
import random
import time
from cStringIO import StringIO
from django.core.cache import get_cache
from django.core.files.uploadedfile import InMemoryUploadedFile

from django_resubmit.conf import settings


FIELD_FILE_NAME = "name"
FIELD_FILE_SIZE = "size"
FIELD_CONTENT_TYPE = "content_type"
FIELD_CHARSET = "charset"
FIELD_CONTENT = "content"

def get_default_storage():
    backend = get_cache(settings.BACKEND)
    return TemporaryFileStorage(backend)


class TemporaryFileStorage(object):
    def __init__(self, backend, prefix=None):
        if prefix is None:
            prefix = 'cachefile-'
        self.backend = backend
        self.prefix = prefix

    def put_file(self, upload, key=None):
        upload.file.seek(0)
        if not key:
            key = string.replace(unicode(random.random() * time.time()), ".", "")
        state = {
            FIELD_FILE_NAME: upload.name,
            FIELD_FILE_SIZE: upload.size,
            FIELD_CONTENT_TYPE: upload.content_type,
            FIELD_CHARSET: upload.charset,
            FIELD_CONTENT: upload.file.read()}
        self.backend.set(self._getid(key), state)
        upload.file.seek(0)
        return key

    def get_file(self, key, field_name):
        upload = None
        state = self.backend.get(self._getid(key))
        if state:
            size = state[FIELD_FILE_SIZE]
            file = StringIO()
            file.write(state[FIELD_CONTENT])
            upload = InMemoryUploadedFile(
                    file=file,
                    field_name=field_name,
                    name=state[FIELD_FILE_NAME],
                    content_type=state[FIELD_CONTENT_TYPE],
                    size=size,
                    charset=state[FIELD_CHARSET])
            upload.file.seek(0)
        return upload

    def clear_file(self, key):
        self.backend.delete(self._getid(key))

    def _getid(self, key):
        return self.prefix + key

