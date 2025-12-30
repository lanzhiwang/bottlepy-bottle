from inspect import getfullargspec

"""
>>> l1 = [1, 2, 3, 4]
>>> l2 = [5, 6, 7]
>>> l1 or l2
[1, 2, 3, 4]
>>> len(l1 or l2)
4
>>> len(l2 or l1)
3
>>> for i in l1 or l2:
...     print(i)
... 
1
2
3
4
>>> for i in l2 or l1:
...     print(i)
... 
5
6
7
>>> 
"""


def makelist(data):  # This is just too handy
    if isinstance(data, (tuple, list, set, dict)):
        return list(data)
    elif data:
        return [data]
    else:
        return []


def getargspec(func):
    spec = getfullargspec(func)
    print(f"getargspec spec: {spec}")
    kwargs = makelist(spec[0]) + makelist(spec.kwonlyargs)
    return kwargs, spec[1], spec[2], spec[3]


def yieldroutes(func):
    """Return a generator for routes that match the signature (name, args)
    of the func parameter. This may yield more than one route if the function
    takes optional keyword arguments. The output is best described by example::

        a()         -> '/a'
        b(x, y)     -> '/b/<x>/<y>'
        c(x, y=5)   -> '/c/<x>' and '/c/<x>/<y>'
        d(x=5, y=6) -> '/d' and '/d/<x>' and '/d/<x>/<y>'
    """

    print(f"yieldroutes func: {func}")

    print(f"yieldroutes func.__name__: {func.__name__}")
    path = "/" + func.__name__.replace("__", "/").lstrip("/")
    print(f"yieldroutes path: {path}")

    spec = getargspec(func)
    print(f"yieldroutes spec: {spec}")

    argc = len(spec[0]) - len(spec[3] or [])
    print(f"yieldroutes argc: {argc}")

    path += ("/<%s>" * argc) % tuple(spec[0][:argc])
    print(f"yieldroutes path: {path}")

    yield path
    for arg in spec[0][argc:]:
        path += "/<%s>" % arg
        print(f"yieldroutes path: {path}")
        yield path


def a():
    pass


def b(x, y):
    pass


def c(x, y=5):
    pass


def d(x=5, y=6):
    pass


if __name__ == "__main__":
    for rule in yieldroutes(a):
        print(f"rule: {rule}")
    print()

    for rule in yieldroutes(b):
        print(f"rule: {rule}")
    print()

    for rule in yieldroutes(c):
        print(f"rule: {rule}")
    print()

    for rule in yieldroutes(d):
        print(f"rule: {rule}")
    print()

"""
$ python yieldroutes.py 
yieldroutes func: <function a at 0x7fe6bd3474c0>
yieldroutes func.__name__: a
yieldroutes path: /a
getargspec spec: FullArgSpec(args=[], varargs=None, varkw=None, defaults=None, kwonlyargs=[], kwonlydefaults=None, annotations={})
yieldroutes spec: ([], None, None, None)
yieldroutes argc: 0
yieldroutes path: /a
rule: /a

yieldroutes func: <function b at 0x7fe6bd347600>
yieldroutes func.__name__: b
yieldroutes path: /b
getargspec spec: FullArgSpec(args=['x', 'y'], varargs=None, varkw=None, defaults=None, kwonlyargs=[], kwonlydefaults=None, annotations={})
yieldroutes spec: (['x', 'y'], None, None, None)
yieldroutes argc: 2
yieldroutes path: /b/<x>/<y>
rule: /b/<x>/<y>

yieldroutes func: <function c at 0x7fe6bd3476a0>
yieldroutes func.__name__: c
yieldroutes path: /c
getargspec spec: FullArgSpec(args=['x', 'y'], varargs=None, varkw=None, defaults=(5,), kwonlyargs=[], kwonlydefaults=None, annotations={})
yieldroutes spec: (['x', 'y'], None, None, (5,))
yieldroutes argc: 1
yieldroutes path: /c/<x>
rule: /c/<x>
yieldroutes path: /c/<x>/<y>
rule: /c/<x>/<y>

yieldroutes func: <function d at 0x7fe6bd347740>
yieldroutes func.__name__: d
yieldroutes path: /d
getargspec spec: FullArgSpec(args=['x', 'y'], varargs=None, varkw=None, defaults=(5, 6), kwonlyargs=[], kwonlydefaults=None, annotations={})
yieldroutes spec: (['x', 'y'], None, None, (5, 6))
yieldroutes argc: 0
yieldroutes path: /d
rule: /d
yieldroutes path: /d/<x>
rule: /d/<x>
yieldroutes path: /d/<x>/<y>
rule: /d/<x>/<y>

$
"""
