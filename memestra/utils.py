import os
import sys
from itertools import chain

# FIXME: this only handles module name not subpackages
def resolve_module(module_name, importer_path=()):
    module_path = module_name + ".py"
    bases = sys.path
    if importer_path:
        bases = chain([os.path.abspath(
            os.path.dirname(importer_path))], sys.path)
    for base in bases:
        fullpath = os.path.join(base, module_path)
        if os.path.exists(fullpath):
            return fullpath
    return
