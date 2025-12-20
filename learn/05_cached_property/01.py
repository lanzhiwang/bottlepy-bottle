"""
这段代码实现的是一个非常经典且高效的设计模式: 惰性初始化(Lazy Initialization).
它的核心作用是: 一个属性只在第一次访问时计算, 随后将结果"固化"在实例中, 后续访问不再重复计算.

这与 Python 3.8+ 标准库中的 functools.cached_property 逻辑几乎一致, 但这段实现展示了其底层的巧妙机制.
"""

import functools
import time


def update_wrapper(wrapper, wrapped, *a, **ka):
    """
    作用: 将原函数(wrapped)的元数据(如 __name__, __doc__, __module__ 等)拷贝到 cached_property 实例上.
    为何加 try-except: 某些特殊对象可能缺少部分元数据属性. 高级开发人员通常会加这个保护, 以增强代码在各种复杂(如 C 扩展模块、动态生成的类)环境下的鲁棒性.
    """
    print(f"update_wrapper wrapper: {wrapper}")
    print(f"update_wrapper wrapped: {wrapped}")
    print(f"update_wrapper a: {a}")
    print(f"update_wrapper ka: {ka}")

    try:
        functools.update_wrapper(wrapper, wrapped, *a, **ka)
    except AttributeError:
        pass


"""
cached_property 的运作机制

这是一个非数据描述符(Non-data Descriptor). 它的奥秘在于 Python 属性查找的优先级:

1. 数据描述符(定义了 __set__ 或 __delete__).
2. 实例属性(存在于 obj.__dict__ 中).
3. 非数据描述符(仅定义了 __get__).

运行流程:

首次访问: obj.__dict__ 中没有该属性名. Python 顺着查找路径找到了类中的 cached_property (非数据描述符), 触发 __get__.
计算与替换: __get__ 调用原始函数计算结果, 并通过 obj.__dict__[self.func.__name__] = value 直接将结果写入实例字典.
后续访问: 由于 obj.__dict__ 现在已经有了该属性(实例属性优先级更高), Python 会直接从字典中取值, 永远不会再次触发 __get__, 从而实现了缓存.
"""


class cached_property(object):
    """A property that is only computed once per instance and then replaces
    itself with an ordinary attribute. Deleting the attribute resets the
    property."""

    def __init__(self, func):
        print(f"cached_property __init__ func: {func}")
        update_wrapper(self, func)
        self.func = func

    def __get__(self, obj, cls):
        print(f"cached_property __get__ self: {self}")
        print(f"cached_property __get__ obj: {obj}")
        print(f"cached_property __get__ cls: {cls}")

        if obj is None:
            return self
        print(f"cached_property __get__ self.func.__name__: {self.func.__name__}")
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        print(f"cached_property __get__ value: {value}")
        return value


class DataAnalyzer:
    def __init__(self, data_list):
        self.data_list = data_list
        print("Analyzer 实例已创建")

    @cached_property
    def expensive_sum(self):
        """模拟一个非常耗时的计算过程"""
        print("正在进行复杂的数学计算... (耗时 2 秒)")
        time.sleep(2)
        return sum(self.data_list)


# --- 测试过程 ---

analyzer = DataAnalyzer([10, 20, 30, 40, 50])

print("\n--- 第一次访问属性 ---")
start = time.time()
print(f"结果: {analyzer.expensive_sum}")
print(f"耗时: {time.time() - start:.2f} 秒")

print("\n--- 第二次访问属性 ---")
start = time.time()
print(f"结果: {analyzer.expensive_sum}")  # 直接从缓存取, 不再打印"正在进行计算"
print(f"耗时: {time.time() - start:.2f} 秒")

print("\n--- 查看内部存储 ---")
# 你会发现 'expensive_sum' 已经出现在了实例字典里
print(f"实例的 __dict__: {analyzer.__dict__}")

print("\n--- 重置缓存 ---")
# 只要删除实例字典里的这个 key, 下次访问就会重新计算
del analyzer.expensive_sum
print("缓存已手动清除")
print(f"再次访问结果: {analyzer.expensive_sum}")

"""
$ python 01.py
cached_property __init__ func: <function DataAnalyzer.expensive_sum at 0x7f550dddde40>
update_wrapper wrapper: <__main__.cached_property object at 0x7f550dde56d0>
update_wrapper wrapped: <function DataAnalyzer.expensive_sum at 0x7f550dddde40>
update_wrapper a: ()
update_wrapper ka: {}
Analyzer 实例已创建

--- 第一次访问属性 ---
cached_property __get__ self: <__main__.cached_property object at 0x7f550dde56d0>
cached_property __get__ obj: <__main__.DataAnalyzer object at 0x7f550dde5700>
cached_property __get__ cls: <class '__main__.DataAnalyzer'>
cached_property __get__ self.func.__name__: expensive_sum
正在进行复杂的数学计算... (耗时 2 秒)
cached_property __get__ value: 150
结果: 150
耗时: 2.00 秒

--- 第二次访问属性 ---
结果: 150
耗时: 0.00 秒

--- 查看内部存储 ---
实例的 __dict__: {'data_list': [10, 20, 30, 40, 50], 'expensive_sum': 150}

--- 重置缓存 ---
缓存已手动清除
cached_property __get__ self: <__main__.cached_property object at 0x7f550dde56d0>
cached_property __get__ obj: <__main__.DataAnalyzer object at 0x7f550dde5700>
cached_property __get__ cls: <class '__main__.DataAnalyzer'>
cached_property __get__ self.func.__name__: expensive_sum
正在进行复杂的数学计算... (耗时 2 秒)
cached_property __get__ value: 150
再次访问结果: 150
$

3. 为什么高级开发人员喜欢这种写法?

1. 性能优化: 对于需要从数据库读取配置、进行图像处理或复杂正则匹配的属性, 这种做法能极大减少 CPU 负担.
2. 代码优雅: 它让你可以像访问普通属性一样(obj.attr)去调用一个方法, 同时不需要在 __init__ 中预先计算所有内容(避免了不必要的初始化开销).
3. 支持重置: 通过 del obj.attr 就能清空缓存, 这在数据更新后需要重新计算的场景下非常灵活.

注意事项
1. 线程安全: 上述实现在多线程环境下, 如果有两个线程同时第一次访问, 可能会导致计算被触发两次(虽然最终结果会被覆盖为同一个). 在极高性能要求的工业级代码中, 有时会在这里加锁(Lock).
2. 不可变性: 通常建议只对那些在实例生命周期内不经常变动的数据使用 cached_property.

这段代码是 Python 描述符协议(Descriptor Protocol)最优雅的应用之一. 你理解了这个, 就理解了 Python 对象系统的核心.

"""
