import os
import hashlib
import yaml


class Format(object):

    version = 0

    fields = (('version', lambda: Format.version),
              ('obsolete_functions', lambda: []),
              ('generator', lambda: 'manual'))

    generators = {'memestra', 'manual'}

    @staticmethod
    def setdefaults(data):
        for field, default in Format.fields:
            data.setdefault(field, default())

    @staticmethod
    def check(data):
        Format.check_keys(data)
        for k, _ in Format.fields:
            getattr(Format, 'check_{}'.format(k))(data)

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
    def check_obsolete_functions(data):
        obsolete_functions = data['obsolete_functions']
        if not isinstance(obsolete_functions, list):
            raise ValueError("obsolete_functions must be a list")
        if not all(isinstance(of, str) for of in obsolete_functions):
            raise ValueError("obsolete_functions must be a list of string")


class CacheKey(object):

    def __init__(self, module_path):
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
        Format.setdefaults(data)
        Format.check(data)
        cache_path = self._get_path(key)
        with open(cache_path, 'w') as yaml_fd:
            yaml.dump(data, yaml_fd)

    def keys(self):
        return os.listdir(self.cachedir)


def run_set(args):
    data = {'generator': 'manual',
            'obsolete_functions': args.deprecated}
    cache = Cache()
    key = CacheKey(args.input)
    cache[key] = data

def run_list(args):
    cache = Cache()
    for k in cache.keys():
        print(k)

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

    args = parser.parse_args()
    args.runner(args)


