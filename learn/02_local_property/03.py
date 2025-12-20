"""
3. 进阶用法: 自定义初始化
有时候我们希望 local 对象在每个线程中都有一些默认值.
我们可以通过继承并重写 __init__ 来实现.
"""

import threading


class MyLocal(threading.local):
    def __init__(self):
        # 每个线程第一次访问此对象时, 都会执行一次 __init__
        self.history = []


my_data = MyLocal()


def track_work(item):
    my_data.history.append(item)
    print(f"{threading.current_thread().name} 的记录: {my_data.history}")


# 在两个线程中操作, 你会发现它们的 history 列表是互不影响的
threading.Thread(target=track_work, args=("Task 1",)).start()
threading.Thread(target=track_work, args=("Task 2",)).start()

"""
$ python 03.py
Thread-1 (track_work) 的记录: ['Task 1']
Thread-2 (track_work) 的记录: ['Task 2']
$ python 03.py
Thread-1 (track_work) 的记录: ['Task 1']
Thread-2 (track_work) 的记录: ['Task 2']
$

4. 为什么要用它? (核心价值)

作为高级开发人员, 你在以下场景必须想到它: 

1. Web 框架的 Request Context:
在 Flask 等框架中, 每个请求都在一个独立的线程里运行. 你需要一个全局可访问的 request 对象, 但这个对象必须只包含当前请求的信息.
threading.local 就是这种设计的核心支撑.

2. 数据库连接池:
通常我们会给每个线程分配一个独立的数据库连接, 以避免多线程共享一个连接导致的事务混乱或 Socket 冲突.

3. 消除参数传递(Refactoring): 
如果你有一个变量需要在几十个函数之间层层传递(例如: 当前登录的用户信息),
使用 threading.local 可以让你直接在深层函数中获取该信息, 而无需修改所有函数的签名.

总结
threading.local() 的作用是: 在多线程环境下, 提供一种看似全局共享、实则线程私有的变量存储机制,
从而避免锁(Lock)带来的性能损耗, 并简化多线程编程中的数据隔离问题.

"""
