import some_module

def foo():
    return some_module.foo()

def bar():
    return some_module.bar()

def foobar():
    return foo(), bar()
