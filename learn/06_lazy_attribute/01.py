import functools
import time


class lazy_attribute(object):
    """A property that caches itself to the class object."""

    def __init__(self, func):
        print(f"lazy_attribute __init__ func: {func}")
        functools.update_wrapper(self, func, updated=[])
        self.getter = func

    def __get__(self, obj, cls):
        print(f"lazy_attribute __get__ self: {self}")
        print(f"lazy_attribute __get__ obj: {obj}")
        print(f"lazy_attribute __get__ cls: {cls}")

        value = self.getter(cls)
        print(f"lazy_attribute __get__ value: {value}")

        print(f"lazy_attribute __get__ self.__name__: {self.__name__}")
        setattr(cls, self.__name__, value)
        return value


class DatabaseConfig:
    @lazy_attribute
    def connection_string(cls):
        """模拟一个复杂的配置解析过程, 比如读取本地加密文件"""
        print(f"--- 正在为类 {cls.__name__} 生成全局连接字符串... ---")
        time.sleep(2)  # 模拟高耗时 IO
        return "postgresql://admin:secret_password@localhost:5432/production_db"


# --- 测试过程 ---

print("1. 第一次访问(通过类访问):")
start = time.time()
# 此时触发 __get__, 计算并修改类属性
print(f"Result: {DatabaseConfig.connection_string}")
print(f"耗时: {time.time() - start:.2f}s")

print("\n2. 第二次访问(通过另一个实例访问):")
start = time.time()
db1 = DatabaseConfig()
# 此时不再计算, 直接从类字典获取
print(f"Result: {db1.connection_string}")
print(f"耗时: {time.time() - start:.2f}s")

print("\n3. 检查类字典内容:")
# 你会发现 connection_string 不再是描述符对象, 而是一个字符串
print(
    f"DatabaseConfig.__dict__['connection_string']: {DatabaseConfig.__dict__['connection_string']}"
)


"""
这段代码实现的是一种类级别的惰性加载(Class-level Lazy Loading).
虽然它看起来和之前讨论过的 cached_property 很像, 但它们之间有一个本质的区别:
cached_property: 缓存结果在 实例(Instance) 上. 每个实例都会计算一次, 各实例间不共享.
lazy_attribute: 缓存结果在类(Class)上. 所有实例共享同一个结果, 且全生命周期只计算一次.

1. 代码核心逻辑解析

(1) 装饰器初始化 (__init__)

使用 functools.update_wrapper(self, func, updated=[]) 将被装饰函数的元数据(如 __name__)拷贝到 lazy_attribute 实例上.
这确保了在 __get__ 中可以使用 self.__name__ 获取正确的属性名.

(2) 描述符触发 (__get__)

这是该模式最巧妙的地方:
参数接收: __get__(self, obj, cls) 中, cls 是所属的类对象.
调用函数: value = self.getter(cls). 注意, 这里传入的是 cls(类), 这意味着被装饰的方法在行为上类似于一个 classmethod.
覆盖类属性: setattr(cls, self.__name__, value). 这一步会直接在类的 __dict__ 中写入计算后的值.

由于类属性的查找优先级高于非数据描述符, 一旦这一行执行完毕, 原来的 lazy_attribute 实例就从类的查找路径中被"遮蔽"或替换了.

单次执行: 之后无论是通过类访问 cls.attr, 还是通过实例访问 obj.attr, 拿到的都是直接存储在类字典里的 value, 不会再触发 __get__.

2. 使用示例
这个模式非常适合用于处理昂贵的、全局共享的配置或元数据.

3. 与其他模式的对比

作为高级开发人员, 在选择使用 lazy_attribute 还是其他工具时, 通常考虑以下维度:
特性       property          cached_property           lazy_attribute
计算频率    每次访问都计算      每个实例计算一次.             每个类计算一次
存储位置    不存储(动态计算)    存储在 obj.__dict__          存储在 Cls.__dict__
适用场景    简单的逻辑切换      实例相关的重计算(如用户总分)    类相关的静态数据(如配置解析)
内存开销    最低              随实例增加而增加               极低(全局一份)

4. 潜在风险与注意事项

单向性: 一旦计算完成, 结果就固定在类上了. 如果你在程序运行中需要刷新这个值, 必须手动执行 del DatabaseConfig.connection_string, 这样下次访问才会重新触发描述符.

线程安全性: 如果多个线程在同一瞬间第一次访问该属性, self.getter(cls) 可能会被并发调用多次. 在对性能极度敏感且计算开销极大的环境下, 可能需要加一把类级别的锁.

行为混淆: 因为它在计算时传入的是 cls, 所以被装饰的方法内部无法访问实例变量(self). 如果不熟悉此模式的同事维护代码, 可能会感到困惑.

总结

lazy_attribute 是一种极其精简且高效的类级别缓存方案. 它利用 Python 描述符协议实现了"自毁并替换"的逻辑, 是编写高性能框架(如 Web 框架的路由解析、ORM 的模型元数据加载)时的常用利器.

$ python 01.py

lazy_attribute __init__ func: <function DatabaseConfig.connection_string at 0x7fdfc996dd00>

1. 第一次访问(通过类访问):
lazy_attribute __get__ self: <__main__.lazy_attribute object at 0x7fdfc9974aa0>
lazy_attribute __get__ obj: None
lazy_attribute __get__ cls: <class '__main__.DatabaseConfig'>
--- 正在为类 DatabaseConfig 生成全局连接字符串... ---
lazy_attribute __get__ value: postgresql://admin:secret_password@localhost:5432/production_db
lazy_attribute __get__ self.__name__: connection_string
Result: postgresql://admin:secret_password@localhost:5432/production_db
耗时: 2.00s

2. 第二次访问(通过另一个实例访问):
Result: postgresql://admin:secret_password@localhost:5432/production_db
耗时: 0.00s

3. 检查类字典内容:
DatabaseConfig.__dict__['connection_string']: postgresql://admin:secret_password@localhost:5432/production_db
$

"""
