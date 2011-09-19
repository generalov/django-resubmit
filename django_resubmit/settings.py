
RESUBMIT_TEMPORARY_STORAGE = 'django_resubmit.storage.CacheTemporaryStorage'

RESUBMIT_THUMBNAILERS = [
    {
        'NAME': 'django_resubmit.thumbnailer.pil_image.Thumbnailer',
        'MIME_TYPES': (
            'image/bmp', 'image/x-ms-bmp',
            'image/png', 'image/jpeg', 'image/gif',
            'image/x-icon', 'image/vnd.microsoft.icon',)
    }
]

RESUBMIT_THUMBNAIL_SIZE = (60, 60)
