"""
假设我们有一个全局变量 global_context, 两个进程都试图修改它.
那么两个进程会相互影响吗? 请使用代码进行举例说明.

你好! 作为一个精通 Python 的高级开发人员, 我可以直接给出结论:
在多进程(Multiprocessing)环境下, 两个进程修改同一个全局变量, 彼此之间完全没有影响.
这是因为进程和线程有着本质的区别. 在操作系统层面, 每个进程都拥有独立的内存地址空间. 当一个子进程被创建时, 它会获得父进程当前内存的一份"副本"
(在 Linux 下通过 fork 实现, 采用写时复制 Copy-on-Write 技术). 一旦进程开始运行, 它们就像住在两个平行的宇宙中, 互不干涉.

"""

import multiprocessing
import os
import time

# 定义一个全局变量
global_context = "Initial Value"


def worker(new_value):
    global global_context

    # 获取当前进程的 ID
    pid = os.getpid()
    print(f"[进程 {pid}] 收到任务, 当前 global_context: '{global_context}'")

    # 修改全局变量
    global_context = new_value

    # 模拟耗时操作
    time.sleep(1)
    print(f"[进程 {pid}] 修改后的 global_context: '{global_context}'")


if __name__ == "__main__":
    print(f"[主进程 {os.getpid()}] 初始 global_context: '{global_context}'\n")

    # 创建两个进程
    # 进程 P1 尝试将其改为 'PROCESS_A'
    p1 = multiprocessing.Process(target=worker, args=("PROCESS_A",), name="Proc-A")
    # 进程 P2 尝试将其改为 'PROCESS_B'
    p2 = multiprocessing.Process(target=worker, args=("PROCESS_B",), name="Proc-B")

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print(
        f"\n[主进程 {os.getpid()}] 所有子进程结束后的 global_context: '{global_context}'"
    )


"""
$ python 01.py
[主进程 849467] 初始 global_context: 'Initial Value'

[进程 849468] 收到任务, 当前 global_context: 'Initial Value'
[进程 849469] 收到任务, 当前 global_context: 'Initial Value'
[进程 849468] 修改后的 global_context: 'PROCESS_A'
[进程 849469] 修改后的 global_context: 'PROCESS_B'

[主进程 849467] 所有子进程结束后的 global_context: 'Initial Value'
$

结论说明:

1. 子进程 A 将其修改为 PROCESS_A, 这只影响它自己的内存空间.
2. 子进程 B 将其修改为 PROCESS_B, 它完全不知道进程 A 做了什么.
3. 主进程 的 global_context 依然保持初始值.

高级开发者的深度解析
为什么在多进程中全局变量不生效, 而多线程(Threading)中却会产生冲突?

A. 内存隔离 (Memory Isolation)
进程: 操作系统为每个进程分配独立的虚拟内存. 虽然在创建的那一刻数据是一样的, 但随后它们就像两个独立的文件副本, 修改 A 不会改变 B.
线程: 同一进程内的所有线程共享同一个内存地址空间. 如果两个线程同时修改一个全局变量, 就会发生竞争(Race Condition), 导致数据污染.

B. 既然互不影响, 为什么还要注意?

虽然不会相互干扰, 但这也意味着你无法通过全局变量在多进程间传递数据.

如果你确实需要在进程间共享数据, 作为高级开发人员, 我会建议你使用以下方案:

1. multiprocessing.Value 或 Array: 用于共享简单的基本类型数据.

2. multiprocessing.Manager: 提供共享的 dict 或 list(这是最接近"共享全局变量"体验的方案, 但有跨进程通信开销).

3. 消息队列 (Queue) / 管道 (Pipe): 通过显式发送消息来传递状态(这是并行编程中更推荐的"不要通过共享内存来通信, 而要通过通信来共享内存"原则).

总结

在多进程中, 全局变量是物理隔离的. 如果你之前的代码依赖全局变量在不同进程间同步状态, 那么代码逻辑是无效的; 你需要引入 IPC(进程间通信) 机制.

"""
