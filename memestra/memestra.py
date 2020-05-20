import beniget
import sys
import gast as ast
import os
import warnings
from collections import defaultdict
from memestra.caching import Cache, CacheKey, Format


# FIXME: this only handles module name not subpackages
def resolve_module(module_name):
    module_path = module_name + ".py"
    for base in sys.path:
        fullpath = os.path.join(base, module_path)
        if os.path.exists(fullpath):
            return fullpath
    return


class ImportResolver(ast.NodeVisitor):

    def __init__(self, decorator):
        self.deprecated = None
        self.decorator = tuple(decorator)
        self.cache = Cache()

    def load_deprecated_from_module(self, module_name):
        module_path = resolve_module(module_name)

        if module_path is None:
            return None

        module_key = CacheKey(module_path)

        if module_key in self.cache:
            data = self.cache[module_key]
            if data['version'] == Format.version:
                return set(data['deprecated'])
            elif data['generator'] == 'manual':
                warnings.warn(
                    ("skipping module {} because it has an obsolete, "
                     "manually generated, cache file: {}")
                    .format(module_name,
                            module_key.module_hash))
                return []

        with open(module_path) as fd:
            module = ast.parse(fd.read())
            duc = beniget.DefUseChains()
            duc.visit(module)
            anc = beniget.Ancestors()
            anc.visit(module)

            deprecated = self.collect_deprecated(module, duc, anc)
            dl = {d.name for d in deprecated}
            data = {'generator': 'memestra',
                    'deprecated': sorted(dl)}
            self.cache[module_key] = data
            # visit modules recursively
            self.generic_visit(module)
            return dl

    def visit_Import(self, node):
        for alias in node.names:
            deprecated = self.load_deprecated_from_module(alias.name)
            if deprecated is None:
                continue

            # the functools python module doesn't have a
            # self.def_use_chains.chains[alias] and will cause memestra to crash
            try:
                for user in self.def_use_chains.chains[alias].users():
                    parent = self.ancestors.parents(user.node)[-1]
                    if isinstance(parent, ast.Attribute):
                        if parent.attr in deprecated:
                            self.deprecated.add(parent)
            except:
                continue

    # FIXME: handle relative imports
    def visit_ImportFrom(self, node):
        deprecated = self.load_deprecated_from_module(node.module)
        if deprecated is None:
            return

        aliases = [alias.name for alias in node.names]

        for deprec in deprecated:
            try:
                index = aliases.index(deprec)
                alias = node.names[index]
                for user in self.def_use_chains.chains[alias].users():
                    self.deprecated.add(user.node)
            except ValueError:
                continue

    def visit_Module(self, node):
        duc = beniget.DefUseChains()
        duc.visit(node)
        self.def_use_chains = duc

        ancestors = beniget.Ancestors()
        ancestors.visit(node)
        self.ancestors = ancestors

        self.deprecated = self.collect_deprecated(node, duc, ancestors)
        self.generic_visit(node)

    def collect_deprecated(self, node, duc, ancestors):

        deprecated = set()

        for dlocal in duc.locals[node]:
            dnode = dlocal.node
            if not isinstance(dnode, ast.alias):
                continue

            original_path = tuple(dnode.name.split('.'))
            nbterms = len(original_path)

            if original_path == self.decorator[:nbterms]:
                for user in dlocal.users():
                    parents = list(ancestors.parents(user.node))
                    attrs = list(reversed(self.decorator[nbterms:]))
                    while attrs and parents:
                        attr = attrs[-1]
                        parent = parents.pop()
                        if not isinstance(parent, (ast.Attribute)):
                            break
                        if parent.attr != attr:
                            break
                        attrs.pop()

                    # path parsing fails if some attr left
                    if attrs:
                        continue

                    # Only handle decorators attached to a fdef
                    if not isinstance(parents[-1], ast.FunctionDef):
                        continue
                    deprecated.add(parents[-1])

            elif original_path == self.decorator[-1:]:
                parent = ancestors.parents(dlocal.node)[-1]
                if not isinstance(parent, ast.ImportFrom):
                    continue
                if parent.module != '.'.join(self.decorator[:-1]):
                    continue
                for user in dlocal.users():
                    parent = ancestors.parents(user.node)[-1]
                    if not isinstance(parent, ast.FunctionDef):
                        continue
                    deprecated.add(parent)

        return deprecated


def prettyname(node):
    if isinstance(node, ast.FunctionDef):
        return node.name
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return prettyname(node.value) + '.' + node.attr
    return repr(node)


def memestra(file_descriptor, decorator):
    '''
    Parse `file_descriptor` and returns a list of
    (function, filename, line, colno) tuples. Each elements
    represents a code location where a deprecated function is used.
    A deprecated function is a function flagged by `decorator`, where
    `decorator` is a tuple representing an import path,
    e.g. (module, attribute)
    '''

    assert len(decorator) > 1, "decorator is at least (module, attribute)"

    module = ast.parse(file_descriptor.read())

    # Collect deprecated functions
    resolver = ImportResolver(decorator)
    resolver.visit(module)

    ancestors = resolver.ancestors
    duc = resolver.def_use_chains

    # Find their users
    deprecate_uses = []
    for deprecated_node in resolver.deprecated:
        for user in duc.chains[deprecated_node].users():
            user_ancestors = (n
                              for n in ancestors.parents(user.node)
                              if isinstance(n, ast.FunctionDef))
            if any(f in resolver.deprecated for f in user_ancestors):
                continue

            deprecate_uses.append((prettyname(deprecated_node),
                                   getattr(file_descriptor, 'name', '<>'),
                                   user.node.lineno,
                                   user.node.col_offset))

    deprecate_uses.sort()
    return deprecate_uses


def run():

    import argparse
    from pkg_resources import iter_entry_points

    parser = argparse.ArgumentParser(description='Check decorator usage.')
    parser.add_argument('--decorator', dest='decorator',
                        default='decorator.deprecated',
                        help='Path to the decorator to check')
    parser.add_argument('input', type=argparse.FileType('r'),
                        help='file to scan')

    dispatcher = defaultdict(lambda: memestra)
    for entry_point in iter_entry_points(group='memestra.plugins', name=None):
        entry_point.load()(dispatcher)

    args = parser.parse_args()

    _, extension = os.path.splitext(args.input.name)

    deprecate_uses = dispatcher[extension](args.input,
                                           args.decorator.split('.'))

    for fname, fd, lineno, colno in deprecate_uses:
        print("{} used at {}:{}:{}".format(fname, fd, lineno, colno + 1))


if __name__ == '__main__':
    run()
