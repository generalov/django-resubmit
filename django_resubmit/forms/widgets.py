# -*- coding: utf-8 -*-

import cStringIO
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
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings


class FileCacheWidget(AdminFileWidget):

    def __init__(self, *args, **kwargs):
        cache = kwargs.pop("cache", None)
        self.cachemng = CacheUploadFiles(cache=cache)
        self.hidden_keyname = u""
        self.hidden_key = u""
        self.isSaved = False
        super(FileCacheWidget, self).__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        self.hidden_keyname = "%s-cachekey" % name
        self.hidden_key = data.get(self.hidden_keyname, "")

        upload = super(FileCacheWidget, self).value_from_datadict(data, files, name)

        # user checks 'clear' or checks 'clear' and uploads a file
        if self.hidden_key:
            if (upload is False or upload is FILE_INPUT_CONTRADICTION or
                    data and data.get(self.clear_checkbox_name(name), False)):
                self.cachemng.clear_files_in_cache("cachefile-%s" % self.hidden_key)
                self.hidden_key = u""

        if upload is False or upload is FILE_INPUT_CONTRADICTION:
            return upload

        if files and name in files:
            if not self.hidden_key:
                # generate random key
                self.hidden_key = string.replace(unicode(random.random() * time.time()), ".", "")
            self.cachemng.put_file_to_cache("cachefile-%s" % self.hidden_key, files[name])
        elif self.hidden_key:
            restored = self.cachemng.get_file_from_cache("cachefile-%s" % self.hidden_key)
            if restored:
                assert restored.field_name == name
                upload = restored
                files[name] = restored
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


class CacheUploadFiles(object):
    def __init__(self, cache=None, max_in_memory_size=None):
        if cache is None:
            from django.core.cache import cache
        if max_in_memory_size is None:
            max_in_memory_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
        self.max_in_memory_size = max_in_memory_size
        self.cache = cache

    def put_file_to_cache(self, cache_key, inmfile, cache=None):
        # FIXME: implement caching for lagre files (not in-memory)
        if inmfile.size >= self.max_in_memory_size:
            return
        cachestruct = {}
        cachestruct["content"] = inmfile.file.getvalue()
        cachestruct["field_name"] = inmfile.field_name
        cachestruct["filename"] = inmfile.name
        cachestruct["content-type"] = inmfile.content_type
        cachestruct["filesize"] = inmfile.size
        cachestruct["charset"] = inmfile.charset

        self.cache.set(cache_key, cachestruct)

    def get_file_from_cache(self, cache_key):
        upfile = None
        cache_content = self.cache.get(cache_key)
        if cache_content:
            file = cStringIO.StringIO()
            file.write(cache_content["content"])
            upfile = InMemoryUploadedFile(
                file,
                cache_content["field_name"],
                cache_content["filename"],
                cache_content["content-type"],
                cache_content["filesize"],
                cache_content["charset"]
            )
        return upfile

    def clear_files_in_cache(self, cache_key):
        self.cache.delete(cache_key)

