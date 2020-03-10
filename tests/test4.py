from decorator import deprecated as dp

@dp
def foo(): pass

@dp
def bar():
    foo()

foo()
