import random
import string
import time

from django.conf import settings
from django.contrib.admin.widgets import AdminFileWidget
from django.core.urlresolvers import NoReverseMatch
from django.forms.widgets import Input
from django.forms.widgets import CheckboxInput
from django.forms.widgets import HiddenInput
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.encoding import force_unicode


from django_resubmit.storage import get_default_storage
from django_resubmit.thumbnails import ThumbFactory


FILE_INPUT_CLEAR = False


class FileWidget(AdminFileWidget):

    class Media:
        js = (settings.STATIC_URL + 'django_resubmit/jquery.input_image_preview.js',)

    def __init__(self, *args, **kwargs):
        """
        thumb_size - preview image size, default [50,50]. 
        """
        self.thumb_size = kwargs.pop("thumb_size", [50, 50])
        self.set_storage(get_default_storage())
        self.hidden_keyname = u""
        self.hidden_key = u""
        self.isSaved = False
        super(FileWidget, self).__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        self.hidden_keyname = "%s-cachekey" % name
        self.hidden_key = data.get(self.hidden_keyname, "")

        upload = super(FileWidget, self).value_from_datadict(data, files, name)

        # user checks 'clear' or checks 'clear' and uploads a file
        if upload is FILE_INPUT_CLEAR or upload is FILE_INPUT_CONTRADICTION:
            if self.hidden_key:
                self._storage.clear_file(self.hidden_key)
                self.hidden_key = u""
            return upload

        if files and name in files:
            if not self.hidden_key:
                # generate random key
                self.hidden_key = string.replace(unicode(random.random() * time.time()), ".", "")
            upload = files[name]
            upload.file.seek(0)
            self._storage.put_file(self.hidden_key, upload)
            upload.file.seek(0)
        elif self.hidden_key:
            restored = self._storage.get_file(self.hidden_key, name)
            if restored:
                upload = restored
                files[name] = upload
                upload.file.seek(0)
            else:
                self.hidden_key = u""

        return upload

    def render(self, name, value, attrs=None):
        default_attrs = {'class':'resubmit'}
        attrs = attrs or {}
        attrs.update(default_attrs)
        substitutions = {
            'input': Input().render(name, None, self.build_attrs(attrs, type=self.input_type)),
            'input_text': self.input_text,
            'initial_text': self.initial_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = u'%(input)s'

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = (u'<a target="_blank" href="%s">%s</a>' % (escape(value.url), escape(force_unicode(value))))
        elif self.hidden_key:
            template = self.template_with_initial
            substitutions['initial'] = escape(force_unicode(value.name))

        if not self.is_required and value and (hasattr(value, "url") or self.hidden_key):
            checkbox_name = self.clear_checkbox_name(name)
            checkbox_id = self.clear_checkbox_id(checkbox_name)
            substitutions['clear_checkbox_name'] = checkbox_name
            substitutions['clear_checkbox_id'] = checkbox_id
            substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
            substitutions['clear_template'] = self.template_with_clear % substitutions

        if value:
            substitutions['input'] += self._render_preview(value)
    
        html = template % substitutions

        if self.hidden_key:
            html += HiddenInput().render(self.hidden_keyname, self.hidden_key, {})

        return mark_safe(html)

    def set_storage(self, value):
        self._storage = value

    def _render_preview(self, value):
        output = u''
        try:
            thumb = ThumbFactory(value, self).thumb()
            if thumb:
                output = thumb.render()
        except NoReverseMatch:
            raise
        except Exception:
            output += u"Can't create preview"
        return output
