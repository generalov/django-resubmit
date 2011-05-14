# coding: utf-8
from cStringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile


FIELD_FILE_NAME = "name"
FIELD_FILE_SIZE = "size"
FIELD_CONTENT_TYPE = "content_type"
FIELD_CHARSET = "charset"
FIELD_CONTENT = "content"


class TemporaryFileStorage(object):
    def __init__(self, backend=None, prefix=None, max_in_memory_size=None):
        if backend is None:
            from django.core.cache import cache as backend
        if prefix is None:
            prefix = 'cachefile-'
        if max_in_memory_size is None:
            from django.conf import settings
            max_in_memory_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
        self.max_in_memory_size = max_in_memory_size
        self.backend = backend
        self.prefix = prefix

    def put_file(self, key, upload):
        state = {
            FIELD_FILE_NAME: upload.name,
            FIELD_FILE_SIZE: upload.size,
            FIELD_CONTENT_TYPE: upload.content_type,
            FIELD_CHARSET: upload.charset,
            FIELD_CONTENT: upload.file.read()}
        self.backend.set(self._getid(key), state)

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
        return upload

    def clear_file(self, key):
        self.backend.delete(self._getid(key))

    def _getid(self, key):
        return self.prefix + key

