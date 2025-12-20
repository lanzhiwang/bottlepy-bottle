"""
3. 风险三: 破坏封装与"最小知识原则"
如果使用闭包(如你最初的代码), threading.local() 实例存在于函数作用域中, 而不是对象字典 __dict__ 中.

我们可以对比一下两者的内部结构:

方案 A: 使用闭包(安全)
"""

import threading


def _local_property():
    ls = threading.local()

    def fget(_):
        try:
            return ls.var
        except AttributeError:
            raise RuntimeError("Request context not initialized.")

    def fset(_, value):
        ls.var = value
        print()

    def fdel(_):
        del ls.var

    return property(fget, fset, fdel, "Thread-local property")


# 使用你最初的 local_property 函数
class SafeContext:
    user_id = _local_property()


safe_ctx = SafeContext()
print(safe_ctx.__dict__)

"""
优点: 外部代码无法通过 safe_ctx.xxx 触碰到那个 ls 对象. 它就像一个"幽灵"变量, 只存在于 getter/setter 的闭包环境中.

方案 B: 直接放在实例里(危险)
"""


class RiskyContext:
    def __init__(self):
        self._ls = threading.local()


risky_ctx = RiskyContext()
print(risky_ctx.__dict__)

"""
$ python 07.py
{}
{'_ls': <_thread._local object at 0x7f9cee0f7060>}
$
"""
