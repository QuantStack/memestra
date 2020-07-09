import deprecated

# @deprecated.deprecated(reason="use another function")
# def some_old_function(x, y):
#     return x + y

@deprecated.deprecated("use another function")
def some_old_function_with_no_arg(x, y):
    print("some_old_function(x, y): is called 🦇 ")
    return x + y

@deprecated.deprecated(mariana="use another function", carrapato="magico", reason="another reason")
def some_old_function(x, y):
    print("some_old_function(x, y): is called 🦇 ")
    return x + y

# @deprecated.deprecated("use another function")
# def some_old_function(x, y):
#     print("some_old_function(x, y): is called 🦇 ")
#     return x + y

@deprecated.deprecated
class A:
    pass

@deprecated.deprecated(reason="BBB ^%&*(DIUAOSHK")
class B:
    pass

@deprecated.deprecated("deprecated class with no arg")
class deprecated_class_no_arg:
    pass

some_old_function(4, 7)
B()
A()
deprecated_class_no_arg()
some_old_function_with_no_arg()