"""
为什么要用闭包?
如果你直接在类里写 self.ls = threading.local(), 那么 ls 变成了实例的一个属性.
而使用代码中的闭包方式, ls 被隐藏在 property 的 getter/setter 作用域内, 外部无法通过 shared_ctx.dict 轻易篡改 ls 对象本身, 这符合最小权限原则.
请写一些代码说明不使用闭包带来的风险

这是一个非常深刻的问题. 作为高级开发人员, 我们不仅关注代码"能运行", 更关注代码的健壮性(Robustness)、安全性以及 API 的纯粹性.
如果不使用闭包, 而是将 threading.local() 放在类实例中(例如 self.ls), 会带来以下三个核心风险: 破坏单一职责、命名空间污染、以及极易发生的意外篡改.

以下是代码示例, 说明不使用闭包可能导致的灾难性后果.

1. 风险一: 意外篡改(Fatal Overwriting)
如果 ls 是实例的一个公开属性, 任何程序员(或者第三方库)都可能在不经意间重置它. 一旦重置, 所有线程存储在该实例上的局部数据都会立刻失效或丢失索引.
"""

import threading


class UnsafeContext:
    def __init__(self):
        # 风险点: ls 暴露在实例中
        self.ls = threading.local()

    @property
    def user_id(self):
        return getattr(self.ls, "user_id", None)

    @user_id.setter
    def user_id(self, value):
        self.ls.user_id = value


# --- 模拟灾难 ---
ctx = UnsafeContext()
ctx.user_id = "ADMIN"
print(ctx.user_id)

# 某个粗心的开发人员或某个错误的中间件做了这件事:
ctx.ls = {}  # 彻底破坏了底层存储结构!

try:
    print(ctx.user_id)
except AttributeError as e:
    print(f"崩溃了! 因为 ls 不再是一个 threading.local 对象: {e}")

"""
$ python 05.py
ADMIN
None
$
"""
