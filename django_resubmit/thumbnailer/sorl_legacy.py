from __future__ import absolute_import

import os
from urllib import urlencode

from cStringIO import StringIO
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.encoding import filepath_to_uri, force_unicode
from sorl.thumbnail.base import (
        Thumbnail as SorlThumbnail,
        ThumbnailException as SorlThumbnailException)
from sorl.thumbnail.main import get_thumbnail_setting, build_thumbnail_name
from sorl.thumbnail.templatetags.thumbnail import PROCESSORS

from .resources import FilesystemResource
from .interfaces import IThumbnail, IThumbnailer, ThumbnailException


class Thumbnail(IThumbnail):

    def __init__(self, size, django_thumbnail, source_path):
        self.__dt = django_thumbnail
        self.__url =  getattr(self.__dt, 'absolute_url', reverse('django_resubmit:preview') + '?' + urlencode({'path': source_path.encode('utf-8')}))
        self.__size = size

    @property
    def mime_type(self):
        extension = get_thumbnail_setting('EXTENSION')
        subtype = 'jpeg' if extension == 'jpg' else extension
        return 'image/%s'  % subtype

    @property
    def size(self):
        return self.__size

    @property
    def url(self):
        return self.__url

    def as_file(self):
        self.__dt.dest.seek(0)
        return self.__dt.dest


class Thumbnailer(IThumbnailer):

    def create_thumbnail(self, size, source):
        try:
            if isinstance(source, FilesystemResource):
                t = _DjangoThumbnail(relative_source=source.path, requested_size=size)
            else:
                t = _DjangoThumbnail(relative_source=source.as_file(), relative_dest=StringIO(), requested_size=size)
            return Thumbnail(size, t, source.path)
        except (SorlThumbnailException, IOError), e:
            raise ThumbnailException(e)



class _DjangoThumbnail(SorlThumbnail):
    imagemagick_file_types = get_thumbnail_setting('IMAGEMAGICK_FILE_TYPES')

    def __init__(self, relative_source, requested_size, opts=None,
                 quality=None, basedir=None, subdir=None, prefix=None,
                 relative_dest=None, processors=None, extension=None):

        if isinstance(relative_source, basestring):
            relative_source = force_unicode(relative_source)
            # Set the absolute filename for the source file
            source = self._absolute_path(relative_source)
        else:
            source = relative_source

        quality = get_thumbnail_setting('QUALITY', quality)
        convert_path = get_thumbnail_setting('CONVERT')
        wvps_path = get_thumbnail_setting('WVPS')
        if processors is None:
            processors = PROCESSORS #dynamic_import(get_thumbnail_setting('PROCESSORS'))

        # Call super().__init__ now to set the opts attribute. generate() won't
        # get called because we are not setting the dest attribute yet.
        super(_DjangoThumbnail, self).__init__(source, requested_size,
            opts=opts, quality=quality, convert_path=convert_path,
            wvps_path=wvps_path, processors=processors)

        # Get the relative filename for the thumbnail image, then set the
        # destination filename
        if relative_dest is None:
            relative_dest = \
               self._get_relative_thumbnail(relative_source, basedir=basedir,
                                            subdir=subdir, prefix=prefix,
                                            extension=extension)
        filelike = not isinstance(relative_dest, basestring)
        if filelike:
            self.dest = relative_dest
        else:
            self.dest = self._absolute_path(relative_dest)

        # Call generate now that the dest attribute has been set
        self.generate()

        # Set the relative & absolute url to the thumbnail
        if not filelike:
            self.relative_url = filepath_to_uri(relative_dest)
            self.absolute_url = '%s%s' % (settings.MEDIA_URL,
                                          self.relative_url)

    def _get_relative_thumbnail(self, relative_source,
                                basedir=None, subdir=None, prefix=None,
                                extension=None):
        """
        Returns the thumbnail filename including relative path.
        """
        return build_thumbnail_name(relative_source, self.requested_size,
                                    self.opts, self.quality, basedir, subdir,
                                    prefix, extension)

    def _absolute_path(self, filename):
        absolute_filename = os.path.join(settings.MEDIA_ROOT, filename)
        return absolute_filename.encode(settings.FILE_CHARSET)

    def __unicode__(self):
        return self.absolute_url

