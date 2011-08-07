import mimetypes
import Image

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.fields.files import FieldFile


class ThumbnailFactory(object):

    def __init__(self):
        self._thumbnailers = (
                (ImageThumb, set([
                    'image/png', 'image/jpeg', 'image/gif',
                    'image/x-icon', 'image/vnd.microsoft.icon',
                ])),
        )

    def thumbnail(self, value, width, height):
        guess_type = self.guess_type(value)
        for cls, mime_types in self._thumbnailers:
            if guess_type in mime_types:
                return cls(value, width, height)
        return None

    def guess_type(self, value):
        if isinstance(value, InMemoryUploadedFile):
            return value.content_type
        elif isinstance(value, FieldFile):
            guess_types = mimetypes.guess_type(value.file.name)
            if guess_types and isinstance(guess_types, tuple):
                return guess_types[0]


class ImageThumb(object):

    def __init__(self, value, width, height):
        self.value = value
        self.width = width
        self.height = height

    def write(self, output):
        f = self.value.file
        img = Image.open(f)
        output_format = img.format if img.format.upper() in set(['PNG', 'JPEG', 'GIF']) else 'PNG'
        img.thumbnail((self.width, self.height), Image.ANTIALIAS)
        img.save(output, output_format)

