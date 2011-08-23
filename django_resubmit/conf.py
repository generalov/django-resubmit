from django.core.exceptions import ImproperlyConfigured
from django.conf import settings as default_settings


DEFAULT_RESUBMIT_THUMBNAILERS = [
    {
        "NAME": "django_resubmit.thumbnailer.pil_image.Thumbnailer",
        "MIME_TYPES": (
            'image/bmp', 'image/x-ms-bmp',
            'image/png', 'image/jpeg', 'image/gif',
            'image/x-icon', 'image/vnd.microsoft.icon',)
    }
]

DEFAULT_RESUBMIT_THUMBNAIL_SIZE = (60, 60)


class Config(object):

    def __init__(self, settings):

        if "resubmit" in settings.CACHES:
            backend = "resubmit"
        else:
            backend = getattr(settings, "RESUBMIT_BACKEND", None)

        if not backend:
            raise ImproperlyConfigured("Please specify a resubmit "
                                       "backend in your settings.")

        self.BACKEND = backend
        self.RESUBMIT_THUMBNAIL_SIZE = getattr(settings, "RESUBMIT_THUMBNAIL_SIZE", DEFAULT_RESUBMIT_THUMBNAIL_SIZE)
        self.RESUBMIT_THUMBNAILERS = getattr(settings, "RESUBMIT_THUMBNAILERS", DEFAULT_RESUBMIT_THUMBNAILERS)
        self.STATIC_URL = getattr(settings, "STATIC_URL")


settings = Config(default_settings)
