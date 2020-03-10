import beniget
import gast as ast


def memestra(file_descriptor, decorator):
    '''
    Parse `file_descriptor` and returns a list of
    (function, filename, line, colno) tuples. Each elements
    represents a code location where a deprecated function is used.
    A deprecated function is a function flagged by `decorator`, where
    `decorator` is a string of the form 'module.attribute'
    '''

    decorator_module, decorator_func = decorator.split('.')
    module = ast.parse(file_descriptor.read())

    ancestors = beniget.Ancestors()
    ancestors.visit(module)

    duc = beniget.DefUseChains()
    duc.visit(module)

    # Collect deprecated functions
    deprecated_functions = []
    for dlocal in duc.locals[module]:
        dnode = dlocal.node
        if isinstance(dnode, ast.alias):
            original_name = dnode.name
        if original_name == decorator_module:
            for user in dlocal.users():
                grand_parent, parent = ancestors.parents(user.node)[-2:]
                if not isinstance(parent, ast.Attribute):
                    continue
                if parent.attr != decorator_func:
                    continue
                if not isinstance(grand_parent, ast.FunctionDef):
                    continue
                deprecated_functions.append(grand_parent)
        elif original_name == decorator_func:
            parent = ancestors.parents(dlocal.node)[-1]
            if not isinstance(parent, ast.ImportFrom):
                continue
            if parent.module != decorator_module:
                continue
            for user in dlocal.users():
                parent = ancestors.parents(user.node)[-1]
                if not isinstance(parent, ast.FunctionDef):
                    continue
                deprecated_functions.append(parent)

    # Find their users
    deprecate_uses = []
    for deprecated_function in deprecated_functions:
        for user in duc.chains[deprecated_function].users():
            user_ancestors = (n
                              for n in ancestors.parents(user.node)
                              if isinstance(n, ast.FunctionDef))
            if any(f in deprecated_functions for f in user_ancestors):
                continue

            deprecate_uses.append((deprecated_function.name,
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
