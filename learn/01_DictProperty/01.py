"""
描述符协议 (__get__, __set__, __delete__)
"""

import functools


class DictProperty(object):
    """
    Property that maps to a key in a local dict-like attribute.
    """

    def __init__(self, attr, key=None, read_only=False):
        self.attr, self.key, self.read_only = attr, key, read_only
        print(f"DictProperty __init__ self.attr: {self.attr}")
        print(f"DictProperty __init__ self.key: {self.key}")
        print(f"DictProperty __init__ self.read_only: {self.read_only}")

    def __call__(self, func):
        print(f"DictProperty __call__ func: {func}")
        functools.update_wrapper(self, func, updated=[])
        self.getter, self.key = func, self.key or func.__name__
        print(f"DictProperty __call__ self.getter: {self.getter}")
        print(f"DictProperty __call__ self.key: {self.key}")
        return self

    def __get__(self, obj, cls):
        print(f"DictProperty __get__ self: {self}")
        print(f"DictProperty __get__ obj: {obj}")
        print(f"DictProperty __get__ cls: {cls}")

        if obj is None:
            return self

        print(f"DictProperty __get__ self.key: {self.key}")
        print(f"DictProperty __get__ self.attr: {self.attr}")
        key, storage = self.key, getattr(obj, self.attr)
        print(f"DictProperty __get__ key: {key}")
        print(f"DictProperty __get__ storage: {storage}")

        print(f"DictProperty __get__ key not in storage: {key not in storage}")
        if key not in storage:
            result = self.getter(obj)
            print(f"DictProperty __get__ result: {result}")
            storage[key] = result
        return storage[key]

    def __set__(self, obj, value):
        print(f"DictProperty __set__ self: {self}")
        print(f"DictProperty __set__ obj: {obj}")
        print(f"DictProperty __set__ value: {value}")

        if self.read_only:
            raise AttributeError("Read-Only property.")

        print(f"DictProperty __set__ self.attr: {self.attr}")
        print(f"DictProperty __set__ self.key: {self.key}")
        getattr(obj, self.attr)[self.key] = value

    def __delete__(self, obj):
        print(f"DictProperty __delete__ self: {self}")
        print(f"DictProperty __delete__ obj: {obj}")

        if self.read_only:
            raise AttributeError("Read-Only property.")

        print(f"DictProperty __delete__ self.attr: {self.attr}")
        print(f"DictProperty __delete__ self.key: {self.key}")
        del getattr(obj, self.attr)[self.key]


class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        # 这是 DictProperty 实际操作的"存储桶"
        self._info_cache = {"name": name}
        print(f"User __init__ self.user_id: {self.user_id}")
        print(f"User __init__ self._info_cache: {self._info_cache}")

    # 1. 基本用法: 映射到字典中的 "name" 键
    @DictProperty(attr="_info_cache")
    def name(self):
        return "Unknown"  # 如果字典里没这个 key, 会用这个默认值

    # 2. 延迟加载示例: 计算非常耗时的"等级"
    # 指定 key 为 "rank_level", 且设置为只读
    @DictProperty(attr="_info_cache", key="rank_level", read_only=True)
    def rank(self):
        print(f"正在为用户计算等级（耗时操作）...")
        import time

        time.sleep(1)
        return "Gold Member"

    # 3. 自定义映射: 把属性 'email' 映射到字典的 'contact_email' 键
    @DictProperty(attr="_info_cache", key="contact_email")
    def email(self):
        return "not_set@example.com"


# --- 测试代码 ---

u = User(1, "Alice")

print("--- 访问普通映射 ---")
print(f"User Name: {u.name}")  # 字典已有 "name", 直接返回 Alice

print("\n--- 访问延迟加载属性 ---")
# 第一次访问, 会执行 rank 函数里的打印, 并存入字典
print(f"Rank: {u.rank}")
# 第二次访问, 直接从 _info_cache 获取, 不再打印, 速度极快
print(f"Rank (Cached): {u.rank}")

print("\n--- 写入与查看内部字典 ---")
u.email = "alice@dev.com"  # 触发 __set__, 写入字典的 contact_email 键
print(f"Internal Cache: {u._info_cache}")

print("\n--- 测试只读属性 ---")
try:
    u.rank = "Platinum"
except AttributeError as e:
    print(f"错误拦截成功: {e}")

"""
$ python 01.py
DictProperty __init__ self.attr: _info_cache
DictProperty __init__ self.key: None
DictProperty __init__ self.read_only: False
DictProperty __call__ func: <function User.name at 0x7f1b71751f80>
DictProperty __call__ self.getter: <function User.name at 0x7f1b71751f80>
DictProperty __call__ self.key: name
DictProperty __init__ self.attr: _info_cache
DictProperty __init__ self.key: rank_level
DictProperty __init__ self.read_only: True
DictProperty __call__ func: <function User.rank at 0x7f1b71752020>
DictProperty __call__ self.getter: <function User.rank at 0x7f1b71752020>
DictProperty __call__ self.key: rank_level
DictProperty __init__ self.attr: _info_cache
DictProperty __init__ self.key: contact_email
DictProperty __init__ self.read_only: False
DictProperty __call__ func: <function User.email at 0x7f1b717520c0>
DictProperty __call__ self.getter: <function User.email at 0x7f1b717520c0>
DictProperty __call__ self.key: contact_email
User __init__ self.user_id: 1
User __init__ self._info_cache: {'name': 'Alice'}
--- 访问普通映射 ---
DictProperty __get__ self: <__main__.DictProperty object at 0x7f1b7175af90>
DictProperty __get__ obj: <__main__.User object at 0x7f1b7175aea0>
DictProperty __get__ cls: <class '__main__.User'>
DictProperty __get__ self.key: name
DictProperty __get__ self.attr: _info_cache
DictProperty __get__ key: name
DictProperty __get__ storage: {'name': 'Alice'}
DictProperty __get__ key not in storage: False
User Name: Alice

--- 访问延迟加载属性 ---
DictProperty __get__ self: <__main__.DictProperty object at 0x7f1b7175ad50>
DictProperty __get__ obj: <__main__.User object at 0x7f1b7175aea0>
DictProperty __get__ cls: <class '__main__.User'>
DictProperty __get__ self.key: rank_level
DictProperty __get__ self.attr: _info_cache
DictProperty __get__ key: rank_level
DictProperty __get__ storage: {'name': 'Alice'}
DictProperty __get__ key not in storage: True
正在为用户计算等级（耗时操作）...
DictProperty __get__ result: Gold Member
Rank: Gold Member
DictProperty __get__ self: <__main__.DictProperty object at 0x7f1b7175ad50>
DictProperty __get__ obj: <__main__.User object at 0x7f1b7175aea0>
DictProperty __get__ cls: <class '__main__.User'>
DictProperty __get__ self.key: rank_level
DictProperty __get__ self.attr: _info_cache
DictProperty __get__ key: rank_level
DictProperty __get__ storage: {'name': 'Alice', 'rank_level': 'Gold Member'}
DictProperty __get__ key not in storage: False
Rank (Cached): Gold Member

--- 写入与查看内部字典 ---
DictProperty __set__ self: <__main__.DictProperty object at 0x7f1b7175adb0>
DictProperty __set__ obj: <__main__.User object at 0x7f1b7175aea0>
DictProperty __set__ value: alice@dev.com
DictProperty __set__ self.attr: _info_cache
DictProperty __set__ self.key: contact_email
Internal Cache: {'name': 'Alice', 'rank_level': 'Gold Member', 'contact_email': 'alice@dev.com'}

--- 测试只读属性 ---
DictProperty __set__ self: <__main__.DictProperty object at 0x7f1b7175ad50>
DictProperty __set__ obj: <__main__.User object at 0x7f1b7175aea0>
DictProperty __set__ value: Platinum
错误拦截成功: Read-Only property.
$
"""
