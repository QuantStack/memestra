from decorator import decorate

def _deprecated(func, *args, **kw):
    print('warning:', func.__name__, 'has been deprecated')
    return func(*args, **kw)

def deprecated(func):
    return decorate(func, _deprecated)
