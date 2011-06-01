This could help users to resubmit form after validation error was occured
without loosing selected files.


Status and License
==================

It is licensed under an Simplified BSD License.


Configuration
=============

Edit your ``settings.py`` and append ``django_resubmit`` to the
``INSTALLED_APPS``.  Also you must specify a ``resubmit`` cache backend, for
example::

    INSTALLED_APPS = (
        ...,
        "django_resubmit",
    )
    CACHES = {
        ...,
        "resubmit": {
            "BACKEND": "django.core.caches.backends.filebased.FileBasedCache",
            "LOCATION": "/tmp/resubmit-data",
        }
    }

For more information about cache see Django documentation. 


Usage
=====

Supply FileFiled with custom FileWidget widget::

   from django import forms
   from django_resubmit.forms.widgets import FileWidget
   
   class SampleForm(forms.Form):
       name = forms.CharField(max_length=25)
       file = forms.FileField(widget=FileWidget(thumb_size=[50,50]))


How It Works
============

It stores uploaded file into the temporary storage (cache) on the server with
some key and injects this key as hidden field into the form then the
``ValidationError`` is occured. When user resubmits the form It restores the
file from the cache and puts it into the ``request.FILES``.

It automatically generates and shows thumbnails for uploaded image files. You 
can easily extend it to show video, flash, etc.

It makes Javascript image preview for just selected (not uploaded) files. Works
in Chrome, Firefox and IE.
 

How To Run Tests
================

Use virtualenv::

    virtualenv python
    . ./python/bin/activate
    pip install -r example/requirements.txt
    pip install -e .
    python example/manage.py test django_resubmit testapp


Bugs and TODO
=============

* Extract preview-specific logic from the FileWidget.
* The ability to customize and expand the set of preview methods.
* Dynamically create a more accurate preview using ajax. This should fix the
  preview problem in the Opera browser too.
* Write documentation.
* Commit into the Django.

