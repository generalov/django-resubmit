from __future__ import absolute_import

import os
import mimetypes

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from .interfaces import ThumbnailException, IResource


class CantGuessMimeType(ThumbnailException):
    pass


class ResourceManager(object):

    def __init__(self, temporary_storage):
        self.__temporary_storage = temporary_storage

    def resolve(self, path):
        # FIXME: it is a hack
        # Really, the `path` is either storage key or filename.
        # I suppose storage key is something like 123456789
        # opposite to files, which contains the dot 'image.png'
        # In the end, we need to come up with a better scheme.
        if '.' in path:
            return FilesystemResource(path)
        else:
            return StorageResource(path, self.__temporary_storage)


class StorageResource(IResource):

    def __init__(self, path, storage):
        storage = storage
        self.__key = path
        self.__data = storage.get_file(self.__key, u'dummy-field-name')

    @property
    def path(self):
        return self.__key

    @property
    def mime_type(self):
        return self.__data.content_type

    def as_file(self):
        return self.__data


class FilesystemResource(IResource):

    def __init__(self, path):
        self.__path = path

    @property
    def path(self):
        return self.__path

    @property
    def mime_type(self):
        return self._guess_type(self.__path)

    def as_file(self):
        return open(self._absolute_path(), 'r')

    def _absolute_path(self):
        absolute_filename = os.path.join(settings.MEDIA_ROOT, self.__path)
        return absolute_filename.encode(settings.FILE_CHARSET)

    def _guess_type(self, value):
        if isinstance(value, InMemoryUploadedFile):
            return value.content_type

        guess_types = mimetypes.guess_type(value)
        if guess_types and isinstance(guess_types, tuple):
            return guess_types[0]

        raise CantGuessMimeType('%s' % str(value))
