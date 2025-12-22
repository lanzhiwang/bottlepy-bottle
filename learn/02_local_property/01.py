"""
作为一名高级 Python 开发人员, 我可以用一句话总结 threading.local(): 它是一个"伪装"成全局变量的局部变量.

简单来说, threading.local() 创建一个特殊的对象, 当你把它放在全局作用域时, 所有线程都能访问它,
但每个线程在这个对象里读写数据时, 只能看到自己存进去的东西.
就像每个人都去同一个储物柜存放东西, 但每个人打开柜子门后, 看到的都是属于自己的独立空间.

下面我通过对比试验来为你演示它的核心作用.

1. 场景一: 不使用 threading.local(导致数据污染)
假设我们有一个全局变量 context, 两个线程都试图修改它.

"""

import threading
import time


# 一个普通的对象
class SimpleContext:
    user_id = None


context = SimpleContext()


def worker(user_id):
    context.user_id = user_id
    # 模拟处理业务逻辑, 期间可能会有其他线程修改 context.user_id
    time.sleep(0.5)
    print(
        f"线程 {threading.current_thread().name}: 期望值 {user_id}, 实际值 {context.user_id}"
    )


# 启动两个线程
t1 = threading.Thread(target=worker, args=("Alice",), name="Thread-A")
t2 = threading.Thread(target=worker, args=("Bob",), name="Thread-B")

t1.start()
t2.start()
t1.join()
t2.join()
print()

"""
$ python 01.py
线程 Thread-A: 期望值 Alice, 实际值 Bob
线程 Thread-B: 期望值 Bob, 实际值 Bob
$ python 01.py
线程 Thread-A: 期望值 Alice, 实际值 Bob
线程 Thread-B: 期望值 Bob, 实际值 Bob
$ python 01.py
线程 Thread-A: 期望值 Alice, 实际值 Bob
线程 Thread-B: 期望值 Bob, 实际值 Bob
$

原因: 因为 context.user_id 是全局共享的, Thread-B 把 Thread-A 的数据覆盖了.

"""
