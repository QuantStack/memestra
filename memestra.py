import argparse
import beniget
import gast as ast

import argparse

parser = argparse.ArgumentParser(description='Check decorator usage.')
parser.add_argument('--decorator', dest='decorator',
                    default='decorator.deprecated',
                    help='Path to the decorator to check')
parser.add_argument('input', metavar='N', type=argparse.FileType('r'),
                    help='file to scan')

args = parser.parse_args()

decorator_module, decorator_func = args.decorator.split('.')

module = ast.parse(args.input.read())

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
        deprecate_uses.append((deprecated_function.name,
                               args.input.name,
                               user.node.lineno,
                               user.node.col_offset))

deprecate_uses.sort()
for fname, fd, lineno, colno in deprecate_uses:
    print("{} used at {}:{}:{}".format(fname, fd, lineno, colno + 1))

