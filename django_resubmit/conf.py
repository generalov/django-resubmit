from django.core.exceptions import ImproperlyConfigured
from django.conf import settings as default_settings


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
        self.RESUBMIT_THUMBNAIL_SIZE = getattr(settings, "RESUBMIT_THUMBNAIL_SIZE", (60, 60))
        self.STATIC_URL = getattr(settings, "STATIC_URL")


settings = Config(default_settings)
