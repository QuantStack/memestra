from decorator import deprecated as dp

@dp
def foo(): pass

def bar():
    foo()

foo()
