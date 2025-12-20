"""
如果我的自定义对象不是继承 threading.local, 而是将 threading.local 作为对象的一个属性, 如一下代码所示

class UnsafeContext:
    def __init__(self):
        self.ls = threading.local()

这时每个线程第一次访问此对象时, 都会执行一次 __init__ 吗? 这种使用方法能达到数据隔离的作用吗?
请使用实际的代码进行说明


这是一个非常经典的问题, 触及了 Python 对象模型和 threading.local 底层机制的核心.
作为高级开发人员, 我直接给出结论, 随后用代码为你深度剖析:

1. 关于 __init__: 不会.
   UnsafeContext.__init__ 只会在你实例化这个类时(执行 ctx = UnsafeContext())运行一次.
   后续无论多少个线程访问这个 ctx 实例, 都不会再次触发 UnsafeContext 的 __init__.

2. 关于数据隔离: 能.
   虽然 UnsafeContext 的初始化只运行一次, 但它内部的属性 self.ls 是一个 threading.local 实例.
   这个 ls 对象内部自带一套特殊的查找机制, 能够根据当前线程 ID 隔离数据.
"""

import threading
import time


class UnsafeContext:
    def __init__(self):
        # 这里的代码只会执行一次
        print(
            f"[{threading.current_thread().name}] --- UnsafeContext.__init__ 被调用了 ---"
        )
        self.ls = threading.local()


def worker(ctx, value):
    thread_name = threading.current_thread().name

    # 每个线程访问的是同一个 ctx.ls 对象
    # 但 threading.local 会在内部为每个线程维护独立的字典
    ctx.ls.data = value

    time.sleep(1)
    print(f"[{thread_name}] 读取到的数据是: {ctx.ls.data}")


# 1. 在主线程创建实例
print("主线程: 准备创建 ctx 实例")
ctx = UnsafeContext()
print("主线程: 实例创建完毕\n")

# 2. 启动两个线程, 共用这一个 ctx 实例
t1 = threading.Thread(target=worker, args=(ctx, "线程 A 的私有数据"), name="Thread-A")
t2 = threading.Thread(target=worker, args=(ctx, "线程 B 的私有数据"), name="Thread-B")

t1.start()
t2.start()

t1.join()
t2.join()

"""
$ python 04.py
主线程: 准备创建 ctx 实例
[MainThread] --- UnsafeContext.__init__ 被调用了 ---
主线程: 实例创建完毕

[Thread-A] 读取到的数据是: 线程 A 的私有数据
[Thread-B] 读取到的数据是: 线程 B 的私有数据
$
"""
