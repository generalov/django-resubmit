
class ThumbnailException(Exception): pass


class IThumbnailer(object):

    def create_thumbnail(self, size, source):
        """Requesting to create a thumbnail for a thumbnail-able source.

        size is a tuple of requested thumbnail dimensions (width, height)
        source is a IResource from create thumbnail."""
        raise NotImplemented()


class IThumbnail(object):

    @property
    def mime_type(self):
        """Return thumbnail MIME type."""
        raise NotImplemented()

    @property
    def size(self):
        """Return thumbnail size."""
        raise NotImplemented()

    @property
    def url(self):
        """Return thumbnail HTTP based URL."""
        raise NotImplemented()

    def as_file(self):
        """Return thumbnail as file-like object."""
        raise NotImplemented()


class IResource(object):

    @property
    def mime_type(self):
        """Return resource MIME type."""
        raise NotImplemented()

    @property
    def path(self):
        """Return the resource indentificator."""
        raise NotImplemented()

    def as_file(self):
        """Return the file-like object for resource data."""
        raise NotImplemented()

