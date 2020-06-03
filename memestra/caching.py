import os
import hashlib
import yaml

from memestra.docparse import docparse


class Format(object):

    version = 0

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


class CacheKey(object):

    def __init__(self, module_path):
        self.name, _ = os.path.splitext(os.path.basename(module_path))
        with open(module_path, 'rb') as fd:
            self.module_hash = hashlib.sha256(fd.read()).hexdigest()


class Cache(object):

    def __init__(self):
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
    cache = Cache()
    key = CacheKey(args.input)
    cache[key] = data


def run_list(args):
    cache = Cache()
    for k, v in cache.items():
        print('{}: {} ({})'.format(k, v['name'], len(v['deprecated'])))


def run_clear(args):
    cache = Cache()
    nb_cleared = cache.clear()
    print('Cache cleared, {} element{} removed.'.format(nb_cleared, 's' *
                                                        (nb_cleared > 1)))


def run_docparse(args):
    deprecated = docparse(args.input, args.pattern)

    cache = Cache()
    key = CacheKey(args.input)
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

    parser_set = subparsers.add_parser('set', help='Set a cache entry')
    parser_set.add_argument('--deprecated', dest='deprecated',
                            type=str, nargs='+',
                            default='decorator.deprecated',
                            help='function to flag as deprecated')
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
    parser_docparse.add_argument('-v,--verbose', dest='verbose',
                                 action='store_true')
    parser_docparse.add_argument(
        '--pattern', dest='pattern', type=str, default=r'.*deprecated.*',
        help='pattern found in deprecated function docstring')
    parser_docparse.add_argument('input', type=str,
                                 help='module.py to scan')
    parser_docparse.set_defaults(runner=run_docparse)

    args = parser.parse_args()
    if hasattr(args, 'runner'):
        args.runner(args)
    else:
        parser.print_help()
