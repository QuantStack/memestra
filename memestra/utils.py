import os
import sys
from importlib import util
from importlib.abc import SourceLoader

def _resolve_module(module_name, additional_search_paths=None):
    if additional_search_paths is None:
        additional_search_paths = []

    if module_name is None or module_name == "__main__":
        return None, None

    parent, _, module_name = module_name.rpartition(".")
    search_path = sys.path + additional_search_paths

    if parent != "":
        parent_spec, search_path = _resolve_module(parent)
        if parent_spec is None:
            return None, None

    try:
        spec = None
        for finder in sys.meta_path:
            try:
                spec = finder.find_spec(module_name, search_path)
            except AttributeError:
                pass

            if spec is not None:
                break

        origin = spec.origin if spec else None
        if spec is None or spec.origin is None:
            return None, None
        if isinstance(spec.loader, SourceLoader):
            return spec.origin, spec.submodule_search_locations
        else:
            return None, None

    except ModuleNotFoundError:
        return None, []

def resolve_module(module_name, additional_search_paths=None):
    return _resolve_module(module_name, additional_search_paths)[0]
