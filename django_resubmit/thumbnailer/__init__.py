from __future__ import absolute_import

import os
import mimetypes

from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.core.files.uploadedfile import InMemoryUploadedFile

from ..conf import settings
from ..storage import get_default_storage
from .interfaces import ThumbnailException, IResource


class CantGuessMimeType(ThumbnailException): pass
class UnsupportedMimeType(ThumbnailException): pass


class ThumbnailManager(object):

    def __init__(self, resubmit_thumbnailers=None):
        self.__resubmit_thumbnailers = resubmit_thumbnailers or settings.RESUBMIT_THUMBNAILERS

    def thumbnail(self, size, source_path):
        resource = self._locate(source_path)
        thumbnailer = self._get_thumbnailer(resource.mime_type)
        thumbnail = thumbnailer.create_thumbnail(size, resource)
        return thumbnail

    def _locate(self, path):
        # FIXME: it is a hack
        # Really, the `path` is either storage key or filename.
        # I suppose storage key is something like 123456789
        # opposite to files, which contains the dot 'image.png'
        # In the end, we need to come up with a better scheme.
        if '.' in path:
            return FilesystemResource(path)
        else:
            return StorageResource(path)

    def _get_thumbnailer(self, mimetype):
        description = self._get_thumbnailer_description(mimetype)
        if not description:
            raise UnsupportedMimeType(mimetype)
        loader = description['NAME']
        try:
            Thumbnailer = import_name(loader)
        except ImportError, e:
            raise ImproperlyConfigured('Error importing thumbnailer %s: "%s"' % (loader, e))
        return Thumbnailer()

    def _get_thumbnailer_description(self, mimetype):
        for description in self.__resubmit_thumbnailers:
            if mimetype in description['MIME_TYPES']:
                return description
        return False


class StorageResource(IResource):

    def __init__(self, path, storage=None):
        storage = storage or get_default_storage()
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
        from django.conf import settings
        absolute_filename = os.path.join(settings.MEDIA_ROOT, self.__path)
        return absolute_filename.encode(settings.FILE_CHARSET)

    def _guess_type(self, value):
        if isinstance(value, InMemoryUploadedFile):
            return value.content_type

        guess_types = mimetypes.guess_type(value)
        if guess_types and isinstance(guess_types, tuple):
            return guess_types[0]

        raise CantGuessMimeType("%s" % str(value))


def import_name(name):
    module, attr = name.rsplit('.', 1)
    mod = import_module(module)
    try:
        return getattr(mod, attr)
    except AttributeError:
        raise ImportError("'%s' module has no attribute '%s'" % (module, attr))

