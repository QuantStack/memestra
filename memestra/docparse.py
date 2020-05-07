import gast as ast
import re


def docparse(module_path, pattern):

    with open(module_path) as fd:
        content = fd.read()
    tree = ast.parse(content)
    def_types = (ast.AsyncFunctionDef,
                 ast.FunctionDef,
                 ast.ClassDef)
    flags = re.DOTALL | re.MULTILINE

    deprecated = []
    for stmt in tree.body:
        if not isinstance(stmt, def_types):
            continue
        fst_stmt = stmt.body[0]
        if not isinstance(fst_stmt, ast.Expr):
            continue
        if not isinstance(fst_stmt.value, ast.Constant):
            continue
        cst = fst_stmt.value
        if not isinstance(cst.value, str):
            continue
        if re.match(pattern, cst.value, flags):
            deprecated.append(stmt.name)
    return deprecated
