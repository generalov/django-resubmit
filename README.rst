.. thumbnail: http://live.gnome.org/ThumbnailerSpec

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
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
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
       file = forms.FileField(widget=FileWidget)


Add this url to urls.py::

    url(r'^django_resubmit/', include('django_resubmit.urls', namespace="django_resubmit")),


Advanced settings
=================

There are several advanced settings.

RESUBMIT_THUMBNAIL_SIZE
   The size of thumbnails (width, height)

   Default: `(60, 60)`

RESUBMIT_THUMBNAILERS
   The thumbnailers to use.

   Default::

    RESUBMIT_THUMBNAILERS = [
        {
            "NAME": "django_resubmit.thumbnailer.pil_image.Thumbnailer",
            "MIME_TYPES": (
                'image/bmp', 'image/x-ms-bmp',
                'image/png', 'image/jpeg', 'image/gif',
                'image/x-icon', 'image/vnd.microsoft.icon',)
        }
    ]

The built-in thumbnailers are::

    "django_resubmit.thumbnailer.pil_image.Thumbnailer"
    "django_resubmit.thumbnailer.sorl_legacy.Thumbnailer"

The thumbnailer should implement the ``IThumbnailer`` interface::

    interface IThumbnailer:

        create_thumbnail(size, source): IThumbnail
            Create thumbnail for given Resource

there ``IThumbnail`` is::

    interface IThumbnail:

        property size : string
            Return thumbnail proposed size

        property mime_type : string
            Return thumbnail MIME type

        property url : string
            Return thumbnail url

        as_file(): file
            Return thumbnail data as file-like object.


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
    pip install -r requirements.txt
    pip install -e .
    python example/manage.py test django_resubmit testapp


Bugs and TODO
=============

* Handle thumbnail urls.
* The ability to customize and expand the set of preview methods.
* Write documentation.
* Commit into the Django.

