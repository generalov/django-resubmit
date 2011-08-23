from __future__ import absolute_import

from django.core.urlresolvers import reverse

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image

from urllib import urlencode

from .interfaces import IThumbnailer, IThumbnail


class Thumbnail(IThumbnail):

    def __init__(self, size, thumbnail_image, source_path):
        self.__im = thumbnail_image
        self.__size = size
        self.__format = 'PNG'
        self.__mimetype = 'image/png'
        self.__url = reverse('django_resubmit:preview') + '?' + urlencode({'path': source_path.encode('utf-8')})

    @property
    def mime_type(self):
        """Return thumbnail MIME type"""
        return self.__mimetype

    @property
    def size(self):
        """Return thumbnail size"""
        return self.__size

    @property
    def url(self):
        """Return thumbnail url"""
        return self.__url

    def as_file(self):
        """Return thumbnail as file-like object."""
        buf = StringIO()
        self.__im.save(buf, self.__format)
        return buf


class Thumbnailer(IThumbnailer):

    def create_thumbnail(self, size, source):
        im = Image.open(source.as_file())
        im.thumbnail(size, Image.ANTIALIAS)
        return Thumbnail(size, im, source.path)

