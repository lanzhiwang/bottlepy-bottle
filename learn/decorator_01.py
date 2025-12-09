def my_decorator1(i):
    print "my_decorator1 i:", i
    def wrapper(handler):
        print "my_decorator1 handler:", handler
        print "my_decorator1 Something is happening before the function is called."
        handler()
        print "my_decorator1 Something is happening after the function is called."
        return handler
    return wrapper


@my_decorator1(11)
def say_hello():
    print "Hello!"

say_hello()

"""
$ python learn/decorator_01.py
my_decorator1 i: 11
my_decorator1 handler: <function say_hello at 0x7efd062e76d0>
my_decorator1 Something is happening before the function is called.
Hello!
my_decorator1 Something is happening after the function is called.
Hello!
$
"""
