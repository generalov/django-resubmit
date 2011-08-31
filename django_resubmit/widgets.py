# coding: utf-8
from __future__ import absolute_import

from django import template
from django.forms.widgets import CheckboxInput, ClearableFileInput, HiddenInput, Input
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from django.utils.encoding import force_unicode

from .conf import settings
from .storage import get_default_storage
from .thumbnailer import ThumbnailManager


FILE_INPUT_CLEAR = False


class FileWidget(ClearableFileInput):

    class Media:
        css = {'all': (settings.STATIC_URL + 'django_resubmit/widget.css',)}
        js = (#'https://raw.github.com/malsup/form/master/jquery.form.js',
              settings.STATIC_URL + 'django_resubmit/jquery.form.js',
              settings.STATIC_URL + 'django_resubmit/widget.js',)

    def __init__(self, *args, **kwargs):
        self.template = 'django_resubmit/widget.html'
        self.thumb_size = settings.RESUBMIT_THUMBNAIL_SIZE
        self.set_storage(get_default_storage())
        self.resubmit_key = u""
        super(FileWidget, self).__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        self.resubmit_key = data.get(self._resubmit_keyname(name), u"")

        upload = super(FileWidget, self).value_from_datadict(data, files, name)

        # user checks 'clear' or checks 'clear' and uploads a file
        if upload is FILE_INPUT_CLEAR or upload is FILE_INPUT_CONTRADICTION:
            if self.resubmit_key:
                self._storage.clear_file(self.resubmit_key)
                self.resubmit_key = u""
            return upload

        if files and name in files:
            if self.resubmit_key:
                self._storage.clear_file(self.resubmit_key)
            upload = files[name]
            self.resubmit_key = self._storage.put_file(upload)
        elif self.resubmit_key:
            restored = self._storage.get_file(self.resubmit_key, name)
            if restored:
                upload = restored
                files[name] = upload
            else:
                self.resubmit_key = u""

        return upload

    def render(self, name, value, attrs=None):
        default_attrs = {'class':'resubmit-input'}
        attrs = attrs or {}
        attrs.update(default_attrs)
        checkbox_name = self.clear_checkbox_name(name)
        checkbox_id = self.clear_checkbox_id(checkbox_name)
        
        thumbnail = self._thumbnail(self.thumb_size, value)
        if thumbnail:
            width, height = thumbnail.size
            thumbnail_url = thumbnail.url
        else:
            width, height = self.thumb_size
            thumbnail_url = None

        data = {## Field
                'name': name,
                'value': value,
                'input': Input().render(name, None, self.build_attrs(attrs, type=self.input_type)),
                #'input_text': self.input_text,
                'is_required': self.is_required,
                ## Initial (current) value
                'input_has_initial': value and (hasattr(value, "url") or self.resubmit_key),
                'initial_text': self.initial_text,
                'initial_name': force_unicode(value.name) if value else None,
                'initial_url': value.url if hasattr(value, 'url') else None,
                ## Clear value
                'clear_checkbox': CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id}),
                'clear_checkbox_id': checkbox_id,
                'clear_checkbox_name': checkbox_name,
                'clear_checkbox_label': self.clear_checkbox_label,
                ## Resubmit
                'resubmit_key_input': HiddenInput().render(self._resubmit_keyname(name), self.resubmit_key or u'', {}),
                ## Preview
                'thumbnail_url': thumbnail_url,
                'preview_width': width,
                'preview_height': height,
        }

        return template.loader.render_to_string(self.template, data)

    def _resubmit_keyname(self, name):
        return "%s-cachekey" % name

    def _thumbnail(self, size, value):
        """ Make thumbnail and return url"""
        if self.resubmit_key:
            path = self.resubmit_key
        elif hasattr(value, 'url'):
            path = value.name
        else:
            return None
        try:
            thumbnail_manager = ThumbnailManager()
            return thumbnail_manager.thumbnail(size, path)
        except Exception:
            return None

    def set_storage(self, value):
        self._storage = value

