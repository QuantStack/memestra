import decorator

@decorator.deprecated
def foo(): pass

def bar():
    foo()

foo()
