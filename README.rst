This could help users to resubmit file in FileField in after ValidationError in
Django.


Status and License
==================

It is written by Andrey Podoplelov and Evgeny V. Generalov. It is licensed under
an Simplified BSD License.


Usage
=====

Supply FileFiled with custom FileCacheWidget widget::

   from django import forms
   from django_resubmit.forms.widgets import FileCacheWidget
   
   class SampleForm(forms.Form):
       name = forms.CharField(max_length=25)
       file = forms.FileField(widget=FileCacheWidget)


What It Does
============

It helps users to resubmit form after ValidationError was occured without
loosing specified files.

It stores uploaded file into the temporary storage (cache) on the server with
random key and injects this key as hidden field into the form then
ValidationError is occured. When user resubmits the form It restores the file
from the cache and put it into the ``request.FILES``.


How To Run Tests
================

Use virtualenv::

    virtualenv python
    . ./python/bin/activate
    pip install -r example/requirements.txt
    pip install -e .
    python example/manage.py test django_resubmit


Bugs and TODO
=============

* Separate FileCacheWidget from django.contrib.admin
* Handle large files (larger than FILE_UPLOAD_MAX_MEMORY_SIZE)
* Add support for ImageField
* Write documentation
* Commit into the Django

