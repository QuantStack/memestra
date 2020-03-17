import beniget
import sys
import gast as ast
import os


# FIXME: this only handles module name not subpackages
def resolve_module(module_name):
    module_path = module_name + ".py"
    for base in sys.path:
        fullpath = os.path.join(base, module_path)
        if os.path.exists(fullpath):
            return fullpath
    return


# FIXME: this is not recursive, but should be
class ImportResolver(ast.NodeVisitor):

    def __init__(self, decorator):
        self.deprecated = None
        self.decorator_module, self.decorator_func = decorator.split('.')

    def visit_Import(self, node):
        for alias in node.names:
            module_path = resolve_module(alias.name)

            if module_path is None:
                continue

            with open(module_path) as fd:
                module = ast.parse(fd.read())
                duc = beniget.DefUseChains()
                duc.visit(module)
                anc = beniget.Ancestors()
                anc.visit(module)

                deprecated = self.collect_deprecated(module, duc, anc)
                dl = {d.name: d for d in deprecated}
                for user in self.def_use_chains.chains[alias].users():
                    parent = self.ancestors.parents(user.node)[-1]
                    if isinstance(parent, ast.Attribute):
                        if parent.attr in dl:
                            self.deprecated.add(parent)

    # FIXME: handle relative imports
    def visit_ImportFrom(self, node):
        if node.module is None:
            return
        module_path = resolve_module(node.module)

        if module_path is None:
            return

        aliases = [alias.name for alias in node.names]

        with open(module_path) as fd:
            module = ast.parse(fd.read())
            duc = beniget.DefUseChains()
            duc.visit(module)
            anc = beniget.Ancestors()
            anc.visit(module)
            for deprecated in self.collect_deprecated(module, duc, anc):
                try:
                    index = aliases.index(deprecated.name)
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
            if isinstance(dnode, ast.alias):
                original_name = dnode.name
            if original_name == self.decorator_module:
                for user in dlocal.users():
                    grand_parent, parent = ancestors.parents(user.node)[-2:]
                    # We could handle more situations, incl. renaming
                    if not isinstance(parent, ast.Attribute):
                        continue
                    if parent.attr != self.decorator_func:
                        continue
                    if not isinstance(grand_parent, ast.FunctionDef):
                        continue
                    deprecated.add(grand_parent)
            elif original_name == self.decorator_func:
                parent = ancestors.parents(dlocal.node)[-1]
                if not isinstance(parent, ast.ImportFrom):
                    continue
                if parent.module != self.decorator_module:
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
    `decorator` is a string of the form 'module.attribute'
    '''

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

    parser = argparse.ArgumentParser(description='Check decorator usage.')
    parser.add_argument('--decorator', dest='decorator',
                        default='decorator.deprecated',
                        help='Path to the decorator to check')
    parser.add_argument('input', type=argparse.FileType('r'),
                        help='file to scan')

    args = parser.parse_args()

    deprecate_uses = memestra(args.input, args.decorator)

    for fname, fd, lineno, colno in deprecate_uses:
        print("{} used at {}:{}:{}".format(fname, fd, lineno, colno + 1))


if __name__ == '__main__':
    run()
