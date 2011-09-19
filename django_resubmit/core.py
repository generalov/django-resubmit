from __future__ import absolute_import

from django.conf import settings

from .thumbnailer.resources import ResourceManager, ThumbnailException
from .utils import import_configurable_object


__all__ = ['get_temporary_storage', 'get_thumbnail', 'ThumbnailException']


def get_temporary_storage():
    TemporaryStorage = import_configurable_object(settings.RESUBMIT_TEMPORARY_STORAGE, u'temporary storage')
    return TemporaryStorage()

def get_thumbnail(path):
    locator = ResourceManager(get_temporary_storage())
    resource = locator.resolve(path)
    thumbnail_factory = ThumbnailFactory(settings.RESUBMIT_THUMBNAILERS)
    thumbnailer = thumbnail_factory.get_thumbnailer(resource)
    thumbnail = thumbnailer.create_thumbnail(settings.RESUBMIT_THUMBNAIL_SIZE, resource)
    return thumbnail


class UnsupportedMimeType(ThumbnailException):
    pass


class ThumbnailFactory(object):

    def __init__(self, options):
        self.__options = options

    def get_thumbnailer(self, resource):
        description = self._get_thumbnailer_description(resource.mime_type)
        if not description:
            raise UnsupportedMimeType(resource.mime_type)
        Thumbnailer = import_configurable_object(description['NAME'], u'thumbnailer')
        return Thumbnailer()

    def _get_thumbnailer_description(self, mime_type):
        for description in self.__options:
            if mime_type in description['MIME_TYPES']:
                return description
        return False

