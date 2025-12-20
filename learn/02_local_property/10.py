"""
2. 高级进阶: 为什么需要这种写法? (动态属性工厂)

装饰器 @property 只能写死在类里. 但如果你想写一个"属性工厂", 根据不同的配置生成不同的属性, 就必须用 property() 函数.

例子: 创建一个带有"前缀"验证的属性工厂
假设我们有很多字段需要存入字典, 但每个字段都有不同的验证逻辑:
"""


def validated_property(storage_key, prefix):
    """
    这是一个工厂函数, 返回一个配置好的 property 对象
    """

    def fget(obj):
        # 假设数据存在实例的 _data 字典里
        return obj._data.get(storage_key, "")

    def fset(obj, value):
        if not str(value).startswith(prefix):
            raise ValueError(f"错误: 值必须以 '{prefix}' 开头")
        obj._data[storage_key] = value

    def fdel(obj):
        del obj._data[storage_key]

    # 返回一个组装好的属性
    return property(fget, fset, fdel, f"以 {prefix} 开头的存储属性")


class User:
    def __init__(self):
        self._data = {}

    # 动态生成两个属性
    # 只要调用这个工厂, 就能得到一套独立的 getter/setter 逻辑
    job_code = validated_property("job", "JOB_")
    dept_code = validated_property("dept", "DEPT_")


# --- 使用 ---
u = User()
u.job_code = "JOB_DEVELOPER"  # 正常
# u.dept_code = "HR_MANAGER"   # 抛出 ValueError: 值必须以 'DEPT_' 开头

print(u.job_code)  # 输出: JOB_DEVELOPER

"""
$ python 10.py
JOB_DEVELOPER
$

3. 这种写法相比装饰器的优势

1. 逻辑复用: 如上面的例子, validated_property 函数只需要写一次, 就可以在任何类中创建无数个相似逻辑的属性.

2. 闭包支持: 它利用了闭包(Closure). fget 和 fset 可以访问工厂函数传入的参数(如 prefix 和 storage_key), 而不需要在实例对象中增加额外的属性.

3. 动态绑定: 你可以根据运行时的条件, 决定是否给某个类增加某个属性.

总结

property(fget, fset, fdel, doc) 的本质是: 解耦. 

它把"属性"这个概念拆解成了四个独立的组件(读、写、删、文案), 让你像搭积木一样, 通过代码动态地去拼接这些功能, 而不是在类定义里写死.
这正是你最初看到的 _local_property 能够实现"每个属性都有自己独立的 threading.local() 对象"的核心原因.
"""
