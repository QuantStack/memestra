from decorator import deprecated

@deprecated
def foo(): pass

def bar():
    foo()

foo()
