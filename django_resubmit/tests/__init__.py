"""Force import of all modules in this package in order to get the standard test runner to pick up the tests."""
import os

__test__ = dict()
modules = [name
        for name, ext in map(os.path.splitext, os.listdir(os.path.dirname(__file__)))
        if ext == '.py' and name.startswith('test_')]

for module in modules:
    exec("from %s.%s import __doc__ as module_doc" % (__name__, module))
    exec("from %s.%s import *" % (__name__, module))
    __test__[module] = module_doc or ""
