This could help users to resubmit file in FileField in after ValidationError in
Django.


Status and License
==================

It is licensed under an Simplified BSD License.


Configuration
=============
Add 'django_resubmit' to the INSTALLED_APPS section in your django settings file.

Also you can setup cache backend for you project in settings.py, for example::

    DJANGO_RESUBMIT_BACKEND = "file:///tmp/?timeout=600"

For more information about cache see Django documentation. 


Usage
=====

Supply FileFiled with custom FileWidget widget::

   from django import forms
   from django_resubmit.forms.widgets import FileWidget
   
   class SampleForm(forms.Form):
       name = forms.CharField(max_length=25)
       file = forms.FileField(widget=FileWidget(thumb_size=[50,50]))


What It Does
============

It helps users to resubmit form after ValidationError was occured without
loosing specified files.

It stores uploaded file into the temporary storage (cache) on the server with
random key and injects this key as hidden field into the form then
ValidationError is occured. When user resubmits the form It restores the file
from the cache and put it into the ``request.FILES``.

It automatically generates and shows thumbnails for uploaded image files. You 
can easily extend it to show video, flash, etc.

It makes Javascript image preview for just selected(not uploaded) files. Works 
in Chrome, Firefox and IE.
 

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

* Write documentation
* Commit into the Django

