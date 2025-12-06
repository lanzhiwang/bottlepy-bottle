def my_decorator1(i):
    print "my_decorator1 i:", i
    def wrapper(handler):
        print "my_decorator1 handler:", handler
        print "my_decorator1 Something is happening before the function is called."
        handler()
        print "my_decorator1 Something is happening after the function is called."
        return handler
    return wrapper


def my_decorator2(j):
    print "my_decorator2 j:", j
    def wrapper(handler):
        print "my_decorator2 handler:", handler
        print "my_decorator2 Something is happening before the function is called."
        handler()
        print "my_decorator2 Something is happening after the function is called."
        return handler
    return wrapper


def say_hello():
    print "Hello!"


f1 = my_decorator1(11)
f2 = my_decorator2(22)

say_hello = f2(say_hello)
say_hello = f1(say_hello)

say_hello()

"""
$ python learn/decorator_04.py
my_decorator1 i: 11
my_decorator2 j: 22
my_decorator2 handler: <function say_hello at 0x7fc8f97af850>
my_decorator2 Something is happening before the function is called.
Hello!
my_decorator2 Something is happening after the function is called.
my_decorator1 handler: <function say_hello at 0x7fc8f97af850>
my_decorator1 Something is happening before the function is called.
Hello!
my_decorator1 Something is happening after the function is called.
Hello!
$
"""
