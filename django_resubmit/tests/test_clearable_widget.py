# coding: utf-8
from __future__ import absolute_import

import unittest
from .tools import CacheMock
from .tools import RequestFactory

from ..widgets import FileWidget
from ..widgets import FILE_INPUT_CONTRADICTION
from ..storage import CacheTemporaryStorage


class ClearableWidgetTest(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.widget = FileWidget()

    def test_should_not_display_clear_checkbox_then_is_required(self):
        widget = self.widget
        widget.is_required = True
        request = self.factory.post('/', {
            'file': self.factory.file('test.txt', 'test content')})
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        output = widget.render('file', upload)
        self.assertTrue('resubmit-clear' not in output, output)

    def test_should_display_clear_checkbox_then_does_not_required(self):
        widget = self.widget
        widget.is_required = False
        request = self.factory.post('/', {
            'file': self.factory.file('test.txt', 'test content')})
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        output = widget.render('file', upload)
        self.assertTrue('resubmit-clear' in output, output)

    def test_should_not_to_hold_a_file_on_cotradiction(self):
        cache = CacheMock()
        self.widget.storage = CacheTemporaryStorage(cache=cache)

        widget = self.widget
        widget.is_required = False
        request = self.factory.post('/', {
            'file-clear': 'on',
            'file': self.factory.file('test.txt', 'test content')})
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        self.assertEquals(upload, FILE_INPUT_CONTRADICTION)
        self.assertEquals(cache._data, {})

    def test_should_clear_when_clear_is_checked_and_no_any_file(self):
        cache = CacheMock()
        self.widget.storage = CacheTemporaryStorage(cache=cache)

        widget = self.widget
        widget.is_required = False
        request = self.factory.post('/', {
            'file': self.factory.file('test.txt', 'test content')})
        widget.value_from_datadict(request.POST, request.FILES, 'file')
        self.assertEquals(len(cache._data.keys()), 1, "File should be hodled")

        request = self.factory.post('/', {
            'file-cachekey': widget.resubmit_key,
            'file-clear': 'on', })
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        self.assertEquals(upload, False, "Upload should be False")
        self.assertEquals(cache._data, {}, "Cache should be empty")

    def test_should_handle_large_files(self):
        """
        Should handle large files.

        Django handles files larger than FILE_UPLOAD_MAX_MEMORY_SIZE in a
        special way. It places them in real temporary files on the disk.

        I suppose we should store such files on the disk too, and place in
        the cache just metadata.
        """
        cache = CacheMock()
        self.widget.storage = CacheTemporaryStorage(cache=cache)

        widget = self.widget
        request = self.factory.post('/', {
            'file': self.factory.file('test.txt', 'x' * 10000000)})
        upload = widget.value_from_datadict(request.POST, request.FILES, 'file')
        output = widget.render('file', upload)
        self.assertEquals(len(cache._data.keys()), 1, "Should to remember large file")

