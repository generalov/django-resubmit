# -*- coding: utf-8 -*-
import string
import time
import random

from django.contrib.admin.widgets import AdminFileWidget
from django.forms.fields import FileField
from django.forms.widgets import HiddenInput, CheckboxInput
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.encoding import StrAndUnicode, force_unicode

from django_resubmit.storage import TemporaryFileStorage

FILE_INPUT_CLEAR = False


class FileCacheWidget(AdminFileWidget):

    def __init__(self, *args, **kwargs):
        backend = kwargs.pop("backend", None)
        self.storage = TemporaryFileStorage(backend=backend)
        self.hidden_keyname = u""
        self.hidden_key = u""
        self.isSaved = False
        super(FileCacheWidget, self).__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        self.hidden_keyname = "%s-cachekey" % name
        self.hidden_key = data.get(self.hidden_keyname, "")

        upload = super(FileCacheWidget, self).value_from_datadict(data, files, name)

        # user checks 'clear' or checks 'clear' and uploads a file
        if upload is FILE_INPUT_CLEAR or upload is FILE_INPUT_CONTRADICTION:
            if self.hidden_key:
                self.storage.clear_file(self.hidden_key)
                self.hidden_key = u""
            return upload

        if files and name in files:
            if not self.hidden_key:
                # generate random key
                self.hidden_key = string.replace(unicode(random.random() * time.time()), ".", "")
            upload = files[name]
            upload.file.seek(0)
            self.storage.put_file(self.hidden_key, upload)
        elif self.hidden_key:
            restored = self.storage.get_file(self.hidden_key, name)
            if restored:
                upload = restored
                files[name] = upload
            else:
                self.hidden_key = u""

        return upload

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = u'%(input)s'

        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        #if value != '' and self.hidden_key:
        #    # Only add the 'value' attribute if a value is non-empty.
        #    final_attrs['value'] = force_unicode(self._format_value(value))
        substitutions['input'] = mark_safe(u'<input%s />' % flatatt(final_attrs))

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

        html = template % substitutions

        if self.hidden_key:
            hi = HiddenInput()
            html += hi.render(self.hidden_keyname, self.hidden_key, {})
        return mark_safe(html)


