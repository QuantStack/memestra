import os
import hashlib
import yaml

CacheVersion = 0


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
        self. homedir = os.path.expanduser(os.path.join(user_config_dir,
                                                        memestra_dir))
        os.makedirs(self.homedir, exist_ok=True)

    def _get_path(self, key):
        return os.path.join(self.homedir, key.module_hash)

    def __contains__(self, key):
        cache_path = self._get_path(key)
        return os.path.isfile(cache_path)

    def __getitem__(self, key):
        cache_path = self._get_path(key)
        with open(cache_path, 'r') as yaml_fd:
            return yaml.load(yaml_fd, Loader=yaml.SafeLoader)

    def __setitem__(self, key, data):
        cache_path = self._get_path(key)
        with open(cache_path, 'w') as yaml_fd:
            yaml.dump(data, yaml_fd)


def run():
    import argparse
    parser = argparse.ArgumentParser(description='Edit memestra cache.')
    parser.add_argument('--deprecated', dest='deprecated',
                        type=str, nargs='+',
                        default='decorator.deprecated',
                        help='function to flag as deprecated')
    parser.add_argument('input', type=str,
                        help='module.py to edit')

    data = {'version': CacheVersion,
            'generator': 'manual',
            'obsolete_functions': parser.deprecated}
    cache = Cache()
    key = CacheKey(parser.input)
    cache[key] = data
