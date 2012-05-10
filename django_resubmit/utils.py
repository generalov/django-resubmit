from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured


def import_object(name):
    module, attr = name.rsplit('.', 1)
    mod = import_module(module)
    try:
        return getattr(mod, attr)
    except AttributeError:
        raise ImportError("'%s' module has no attribute '%s'" % (module, attr))

def import_configurable_object(name, verbose_name='object'):
    try:
        result = import_object(name)
    except ImportError: 
        raise ImproperlyConfigured('Error importing %(object)s %(name)s' % {
            'object': verbose_name, 'name': name})
    return result
