# coding: utf-8
from __future__ import absolute_import

import random
import time
try:
    from io import BytesIO
except:
    from cStringIO import StringIO as BytesIO
from django.core.cache import get_cache
from django.core.files.uploadedfile import InMemoryUploadedFile


FIELD_FILE_NAME = 'name'
FIELD_FILE_SIZE = 'size'
FIELD_CONTENT_TYPE = 'content_type'
FIELD_CHARSET = 'charset'
FIELD_CONTENT = 'content'

DJANGO_CACHE_NAME = 'resubmit'


class CacheTemporaryStorage(object):
    def __init__(self, cache=None, prefix=None):
        if prefix is None:
            prefix = 'cachefile-'
        self.cache = cache or get_cache(DJANGO_CACHE_NAME)
        self.prefix = prefix

    def put_file(self, upload, key=None):
        upload.file.seek(0)
        if not key:
            key = self._generate_key()
        state = {
            FIELD_FILE_NAME: upload.name,
            FIELD_FILE_SIZE: upload.size,
            FIELD_CONTENT_TYPE: upload.content_type,
            FIELD_CHARSET: upload.charset,
            FIELD_CONTENT: upload.file.read()}
        self.cache.set(self._getid(key), state)
        upload.file.seek(0)
        return key

    def get_file(self, key, field_name):
        upload = None
        state = self.cache.get(self._getid(key))
        if state:
            size = state[FIELD_FILE_SIZE]
            file = BytesIO()
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
        self.cache.delete(self._getid(key))

    def _generate_key(self):
        return str(random.random() * time.time()).replace('.', '')

    def _getid(self, key):
        return self.prefix + key

