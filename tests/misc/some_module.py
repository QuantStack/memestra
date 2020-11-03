from decoratortest import deprecated

@deprecated
def foo(): pass

def bar(): pass

@deprecated("because it's too old")
def foobar(): pass
