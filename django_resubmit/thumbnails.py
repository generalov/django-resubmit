import mimetypes
import Image
import urllib
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.db.models.fields.files import FieldFile
from django.utils.encoding import iri_to_uri
from sorl.thumbnail.main import DjangoThumbnail
from sorl.thumbnail.templatetags.thumbnail import PROCESSORS


class ThumbFactory(object):
    def __init__(self, value, widget):
        self.value = value
        self.widget = widget

    def thumb(self):
        guess_type = self.guess_type()
        if guess_type in ['image/png', 'image/jpeg', 'image/gif', 'image/x-icon']:
            return ImageThumb(self.value, self.widget)
        elif guess_type in ['video/mpeg', 'video/quicktime']:
            pass # return VideoThumb(self.value, self.size) 

    def guess_type(self):
        if isinstance(self.value, InMemoryUploadedFile):
            return self.value.content_type
        elif isinstance(self.value, FieldFile):
            guess_types = mimetypes.guess_type(self.value.file.name)
            if guess_types and isinstance(guess_types, tuple):
                return guess_types[0]


class ImageThumb(object):
    def __init__(self, value, widget):
        self.value = value
        self.widget = widget

    def _memory(self, upload):
        """ Return image thumbnail as SimpleUploadedFile (subclass of InMemoryUploadedFile) """
        upload.file.seek(0)
        img = Image.open(upload.file)
        img.thumbnail(self.widget.thumb_size, Image.ANTIALIAS)
        buf = StringIO()
        img.save(buf, img.format)
        buf.seek(0)
        thumb = SimpleUploadedFile(upload.name, buf.read(), upload.content_type)
        buf.close()
        return thumb

    def _filesystem(self, value):
        """ Make real filesystem thumbnail and return url"""
        image_path = unicode(value)
        t = DjangoThumbnail(relative_source=image_path,
                            requested_size=self.widget.thumb_size,
                            processors=PROCESSORS)
        return t.absolute_url

    def _src(self):
        """ Get SRC attribute for HTML tag IMG"""
        if isinstance(self.value, InMemoryUploadedFile):
            return "%s?%s" % (
                reverse('django_resubmit.views.thumbnail'),
                urllib.urlencode(dict(
                    key=self.widget.hidden_key,
                    name=self.value.name,
                    width=self.widget.thumb_size[0],
                    height=self.widget.thumb_size[1])))
        elif isinstance(self.value, FieldFile):
            return self._filesystem(self.value)

    def render(self):
        """ Render thumbnail """
        html = '';
        src = self._src()
        if src:
            html += """<img alt="preview" src="%s" class="resubmit" style="display:block" /> """ % src
        return html

