"""
2. 场景二: 使用 threading.local(线程隔离)
现在我们将对象换成 threading.local().
"""

import threading
import time

# 创建一个线程局部存储对象
local_context = threading.local()


def worker(user_id):
    # 每个线程赋值时, 其实是存在了该线程私有的字典里
    local_context.user_id = user_id

    time.sleep(0.5)

    # 获取值时, 也只能获取到本线程之前存入的值
    print(
        f"线程 {threading.current_thread().name}: 期望值 {user_id}, 实际值 {local_context.user_id}"
    )


t1 = threading.Thread(target=worker, args=("Alice",), name="Thread-A")
t2 = threading.Thread(target=worker, args=("Bob",), name="Thread-B")

t1.start()
t2.start()
t1.join()
t2.join()
print()

"""
$ python 02.py
线程 Thread-A: 期望值 Alice, 实际值 Alice
线程 Thread-B: 期望值 Bob, 实际值 Bob
$
$ python 02.py
线程 Thread-A: 期望值 Alice, 实际值 Alice
线程 Thread-B: 期望值 Bob, 实际值 Bob
$ python 02.py
线程 Thread-A: 期望值 Alice, 实际值 Alice
线程 Thread-B: 期望值 Bob, 实际值 Bob
$

原因: threading.local() 内部通过线程 ID 为每个线程分配了独立的存储空间, 实现了物理上的隔离.

"""
