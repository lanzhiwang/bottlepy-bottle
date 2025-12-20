"""
作为高级开发人员, 我来为你深入浅出地解释 property() 函数式写法.

在 Python 中, 你可能更熟悉 @property 这种装饰器写法, 但其实 property() 本质上是一个内置类型的构造函数.

使用 property(fget, fset, fdel, doc) 的写法, 其核心作用是: 通过手动组装"获取、设置、删除"三个函数, 动态地创建一个属性(Descriptor).
这种写法在需要批量生成属性或函数式编程场景下非常强大. 我们不用多线程, 用一个简单的"温度转换"和"动态加密属性"来举例.

1. 基础理解: 与装饰器等价
通常我们这么写
"""


class Student:
    def __init__(self):
        self._age = 0

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        self._age = value


s = Student()
s.age = 25  # 触发 set_age
print(s.age)  # 触发 get_age

"""
$ python 08.py
25
$
"""
