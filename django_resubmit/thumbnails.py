import os
import urllib
import mimetypes
import Image
 
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.fields.files import FieldFile

from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from sorl.thumbnail.base import Thumbnail, ThumbnailException as SorlThumbnailException
from sorl.thumbnail.main import get_thumbnail_setting, build_thumbnail_name
from sorl.thumbnail.templatetags.thumbnail import PROCESSORS


class ThumbnailException(Exception): pass


def can_create_thumbnail(upload):
    try:
        mimetype = _guess_type(upload) 
        return mimetype in set([
                        'image/bmp',
                        'image/png', 'image/jpeg', 'image/gif',
                        'image/x-icon', 'image/vnd.microsoft.icon',
                    ])
    except Exception:
        return False

def _guess_type(value):
    if isinstance(value, InMemoryUploadedFile):
        return value.content_type

    if isinstance(value, FieldFile):
        upload  = value.file
    else:
        upload = value

    guess_types = mimetypes.guess_type(upload.name)
    if guess_types and isinstance(guess_types, tuple):
        return guess_types[0]

def create_thumbnail(size, source, destination=None):
    try:
        return DjangoThumbnail(relative_source=source,
                relative_dest=destination,
                requested_size=size)
    except (SorlThumbnailException, IOError), e:
        raise ThumbnailException(e)


class DjangoThumbnail(Thumbnail):
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
        super(DjangoThumbnail, self).__init__(source, requested_size,
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
            self.relative_url = self._path_to_uri(relative_dest)
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

    def _path_to_uri(self, path):
        """Convert an file system path to a URI portion that is suitable for
        inclusion in a URL.

        We are assuming input is either UTF-8 or unicode already and want to
        reproduce behaviour of encodeURIComponent() JavaScript function.

        Returns an ASCII string containing the encoded result.
        """
        if path is None:
            return path
        return urllib.quote('/'.join(smart_str(path).split(os.sep)),
                            safe='/!~*()')
