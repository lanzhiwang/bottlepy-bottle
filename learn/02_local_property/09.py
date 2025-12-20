"""
而 property() 函数写法是这样的(两者效果完全一致):
"""


class Student:
    def __init__(self):
        self._age = 0

    def get_age(self):
        return self._age

    def set_age(self, value):
        if value < 0:
            raise ValueError("年龄不能为负")
        self._age = value

    # 核心: 手动组装
    age = property(get_age, set_age, None, "这是年龄属性的文档")


s = Student()
s.age = 25  # 触发 set_age
print(s.age)  # 触发 get_age

"""
$ python 09.py
25
$
"""
