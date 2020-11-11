import os
import hashlib
import yaml

# not using gast because we only rely on Import and ImportFrom, which are
# portable. Not using gast prevents an extra costly conversion step.
import ast

from memestra.docparse import docparse
from memestra.utils import resolve_module


class DependenciesResolver(ast.NodeVisitor):
    '''
    Traverse a module an collect statically imported modules
    '''


    def __init__(self):
        self.result = set()

    def add_module(self, module_name):
        module_path = resolve_module(module_name)
        if module_path is not None:
            self.result.add(module_path)

    def visit_Import(self, node):
        for alias in node.names:
            self.add_module(alias.name)

    def visit_ImportFrom(self, node):
        self.add_module(node.module)

    # All members below are specialized in order to improve performance:
    # It's useless to traverse leaf statements and expression when looking for
    # an import.

    def visit_stmt(self, node):
        pass

    visit_Assign = visit_AugAssign = visit_AnnAssign = visit_Expr = visit_stmt
    visit_Return = visit_Print = visit_Raise = visit_Assert = visit_stmt
    visit_Pass = visit_Break = visit_Continue = visit_Delete = visit_stmt
    visit_Global = visit_Nonlocal = visit_Exec = visit_stmt

    def visit_body(self, node):
        for stmt in node.body:
            self.visit(stmt)

    visit_FunctionDef = visit_ClassDef = visit_AsyncFunctionDef = visit_body
    visit_With = visit_AsyncWith = visit_body

    def visit_orelse(self, node):
        for stmt in node.body:
            self.visit(stmt)
        for stmt in node.orelse:
            self.visit(stmt)

    visit_For = visit_While = visit_If = visit_AsyncFor = visit_orelse

    def visit_Try(self, node):
        for stmt in node.body:
            self.visit(stmt)
        for stmt in node.orelse:
            self.visit(stmt)
        for stmt in node.finalbody:
            self.visit(stmt)


class Format(object):

    version = 1

    fields = (('version', lambda: Format.version),
              ('name', str),
              ('deprecated', list),
              ('generator', lambda: 'manual'))

    generators = {'memestra', 'manual'}

    @staticmethod
    def setdefaults(data, **defaults):
        for field, default in Format.fields:
            data.setdefault(field, defaults.get(field, default()))

    @staticmethod
    def check(data):
        Format.check_keys(data)
        for k, _ in Format.fields:
            getattr(Format, 'check_{}'.format(k))(data)

    @staticmethod
    def check_name(data):
        if not isinstance(data['name'], str):
            raise ValueError("name must be an str")

    @staticmethod
    def check_keys(data):
        data_keys = set(data.keys())
        format_keys = {k for k, _ in Format.fields}
        if not data_keys == format_keys:
            difference = data_keys.difference(format_keys)
            raise ValueError("Invalid field{}: {}".format(
                's' * (len(difference) > 1),
                ', '.join(sorted(difference))))

    @staticmethod
    def check_version(data):
        if data['version'] != Format.version:
            raise ValueError(
                "Invalid version, should be {}".format(Format.version))

    @staticmethod
    def check_generator(data):
        if data['generator'] not in Format.generators:
            raise ValueError(
                "Invalid generator, should be one of {}"
                .format(', '.join(sorted(Format.generators))))

    @staticmethod
    def check_deprecated(data):
        deprecated = data['deprecated']
        if not isinstance(deprecated, list):
            raise ValueError("deprecated must be a list")
        if not all(isinstance(of, str) for of in deprecated):
            raise ValueError("deprecated must be a list of string")


class CacheKeyFactoryBase(object):
    def __init__(self, keycls):
        self.keycls = keycls
        self.created = dict()

    def __call__(self, module_path):
        if module_path in self.created:
            return self.created[module_path]
        else:
            self.created[module_path] = None  # creation in process
            key = self.keycls(module_path, self)
            self.created[module_path] = key
            return key

    def get(self, *args):
        return self.created.get(*args)


class CacheKeyFactory(CacheKeyFactoryBase):
    '''
    Factory for non-recursive keys.
    Only the content of the module is taken into account
    '''

    class CacheKey(object):

        def __init__(self, module_path, _):
            self.name, _ = os.path.splitext(os.path.basename(module_path))
            with open(module_path, 'rb') as fd:
                module_content = fd.read()
                module_hash = hashlib.sha256(module_content).hexdigest()
                self.module_hash = module_hash

    def __init__(self):
        super(CacheKeyFactory, self).__init__(CacheKeyFactory.CacheKey)


class RecursiveCacheKeyFactory(CacheKeyFactoryBase):
    '''
    Factory for recursive keys.
    This take into account the module content, and the content of *all* imported
    module. That way, a change in the module hierarchy implies a change in the
    key.
    '''

    class CacheKey(object):

        def __init__(self, module_path, factory):
            assert module_path not in factory.created or factory.created[module_path] is None

            self.name, _ = os.path.splitext(os.path.basename(module_path))
            with open(module_path, 'rb') as fd:
                module_content = fd.read()

                code = ast.parse(module_content)
                dependencies_resolver = DependenciesResolver()
                dependencies_resolver.visit(code)

                new_deps = []
                for dep in dependencies_resolver.result:
                    if factory.get(dep, 1) is not None:
                        new_deps.append(dep)

                module_hash = hashlib.sha256(module_content).hexdigest()

                hashes = [module_hash]

                for new_dep in sorted(new_deps):
                    try:
                        new_dep_key = factory(new_dep)
                    # FIXME: this only happens on windows, maybe we could do
                    # better?
                    except UnicodeDecodeError:
                        continue
                    hashes.append(new_dep_key.module_hash)

                self.module_hash = hashlib.sha256("".join(hashes).encode("ascii")).hexdigest()

    def __init__(self):
        super(RecursiveCacheKeyFactory, self).__init__(RecursiveCacheKeyFactory.CacheKey)


class Cache(object):

    def __init__(self, cache_dir=None):
        if cache_dir is not None:
            self.cachedir = cache_dir
        else:
            xdg_config_home = os.environ.get('XDG_CONFIG_HOME', None)
            if xdg_config_home is None:
                user_config_dir = '~'
                memestra_dir = '.memestra'
            else:
                user_config_dir = xdg_config_home
                memestra_dir = 'memestra'
            self.cachedir = os.path.expanduser(os.path.join(user_config_dir,
                                                            memestra_dir))

        os.makedirs(self.cachedir, exist_ok=True)

    def _get_path(self, key):
        return os.path.join(self.cachedir, key.module_hash)

    def __contains__(self, key):
        cache_path = self._get_path(key)
        return os.path.isfile(cache_path)

    def __getitem__(self, key):
        cache_path = self._get_path(key)
        with open(cache_path, 'r') as yaml_fd:
            return yaml.load(yaml_fd, Loader=yaml.SafeLoader)

    def __setitem__(self, key, data):
        data = data.copy()
        Format.setdefaults(data, name=key.name)
        Format.check(data)
        cache_path = self._get_path(key)
        with open(cache_path, 'w') as yaml_fd:
            yaml.dump(data, yaml_fd)

    def keys(self):
        return os.listdir(self.cachedir)

    def items(self):
        for key in self.keys():
            cache_path = os.path.join(self.cachedir, key)
            with open(cache_path, 'r') as yaml_fd:
                yield key, yaml.load(yaml_fd, Loader=yaml.SafeLoader)

    def clear(self):
        count = 0
        for key in self.keys():
            cache_path = os.path.join(self.cachedir, key)
            os.remove(cache_path)
            count += 1
        return count


def run_set(args):
    data = {'generator': 'manual',
            'deprecated': args.deprecated}
    cache = Cache(cache_dir=args.cache_dir)
    if args.recursive:
        key_factory = RecursiveCacheKeyFactory()
    else:
        key_factory = CacheKeyFactory()
    key = key_factory(args.input)
    cache[key] = data


def run_list(args):
    cache = Cache(cache_dir=args.cache_dir)
    for k, v in cache.items():
        print('{}: {} ({})'.format(k, v['name'], len(v['deprecated'])))


def run_clear(args):
    cache = Cache(cache_dir=args.cache_dir)
    nb_cleared = cache.clear()
    print('Cache cleared, {} element{} removed.'.format(nb_cleared, 's' *
                                                        (nb_cleared > 1)))


def run_docparse(args):
    deprecated = docparse(args.input, args.pattern)

    cache = Cache(cache_dir=args.cache_dir)
    if args.recursive:
        key_factory = RecursiveCacheKeyFactory()
    else:
        key_factory = CacheKeyFactory()
    key = key_factory(args.input)
    data = {'deprecated': deprecated,
            'generator': 'manual'}
    cache[key] = data
    if args.verbose:
        print("Found {} deprecated identifier{}".format(
            len(deprecated),
            's' * bool(deprecated)))
        for name in deprecated:
            print(name)


def run():
    import argparse
    parser = argparse.ArgumentParser(
        description='Interact with memestra cache')
    subparsers = parser.add_subparsers()

    parser.add_argument('--cache-dir', dest='cache_dir',
                        default=None,
                        action='store',
                        help='The directory where the cache is located')

    parser_set = subparsers.add_parser('set', help='Set a cache entry')
    parser_set.add_argument('--deprecated', dest='deprecated',
                            action='append',
                            help='function to flag as deprecated')
    parser_set.add_argument('--recursive', action='store_true',
                            help='set a dependency-aware cache key')
    parser_set.add_argument('input', type=str,
                            help='module.py to edit')
    parser_set.set_defaults(runner=run_set)

    parser_list = subparsers.add_parser('list', help='List cache entries')
    parser_list.set_defaults(runner=run_list)

    parser_clear = subparsers.add_parser('clear',
                                         help='Remove all cache entries')
    parser_clear.set_defaults(runner=run_clear)

    parser_docparse = subparsers.add_parser(
        'docparse',
        help='Set cache entry from docstring')
    parser_docparse.add_argument('-v', '--verbose', dest='verbose',
                                 action='store_true')
    parser_docparse.add_argument(
        '--pattern', dest='pattern', type=str, default=r'.*deprecated.*',
        help='pattern found in deprecated function docstring')
    parser_docparse.add_argument('--recursive', action='store_true',
                                 help='set a dependency-aware cache key')
    parser_docparse.add_argument('input', type=str,
                                 help='module.py to scan')
    parser_docparse.set_defaults(runner=run_docparse)

    args = parser.parse_args()
    if hasattr(args, 'runner'):
        args.runner(args)
    else:
        parser.print_help()
