class BaseController(object):
    _singleton = None
    def __new__(cls, *a, **k):
        print "BaseController __new__ cls:", cls
        print "BaseController __new__ a:", a
        print "BaseController __new__ k:", k

        print "BaseController __new__ cls._singleton:", cls._singleton

        if not cls._singleton:
            cls._singleton = object.__new__(cls, *a, **k)
        return cls._singleton

class CTest(BaseController):
    def _no(self):
        return 'no'
    def yes(self):
        return 'yes'
    def yes2(self, test):
        return test


c1 = CTest()
c2 = CTest()

if isinstance(CTest, type):
    print "isinstance(c1, type)"

if issubclass(CTest, BaseController):
    print "issubclass(c1, BaseController)"

if isinstance(c1, BaseController):
    print "isinstance(c1, BaseController)"
