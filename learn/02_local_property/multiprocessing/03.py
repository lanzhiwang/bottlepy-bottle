"""
在 Python 中, CPU 密集型任务一般采用多进程进行处理, 这是因为 GIL (全局解释器锁) 的影响, 能使用代码示例具体说明这个影响吗?

你好! 作为一名高级 Python 开发人员, 这是一个非常经典且必须深入理解的话题.

GIL(Global Interpreter Lock) 是 CPython (Python 官方解释器)的一种机制, 它确保在任何时刻, 只有一个线程在执行 Python 字节码.
这意味着即使你的电脑有 32 个核心, 对于 CPU 密集型任务, Python 的多线程也只能利用其中的 1 个核心.

为了让你直观感受到这个影响, 我编写了一段对比代码. 我们将执行一个简单的 CPU 密集型任务: 大数求和计算.

实验设计

我们将对比三种方案:

1. 单线程(串行)执行: 作为一个基准.

2. 多线程(Threading)执行: 展示 GIL 如何让多核心"失效".

3. 多进程(Multiprocessing)执行: 展示如何绕过 GIL 实现真正的并行.

代码示例
"""

import time
import threading
import multiprocessing

# 模拟一个 CPU 密集型任务: 巨大的循环和加法计算
COUNT = 50_000_000


def cpu_bound_task(n):
    result = 0
    while result < n:
        result += 1
    return result


if __name__ == "__main__":
    # --- 1. 单线程 (Serial) ---
    print(f"开始单线程任务...")
    start = time.perf_counter()
    cpu_bound_task(COUNT)
    cpu_bound_task(COUNT)
    end = time.perf_counter()
    print(f"单线程耗时: {end - start:.2f} 秒")

    # --- 2. 多线程 (Multithreading) ---
    print(f"\n开始多线程任务 (2个线程)...")
    t1 = threading.Thread(target=cpu_bound_task, args=(COUNT,))
    t2 = threading.Thread(target=cpu_bound_task, args=(COUNT,))

    start = time.perf_counter()
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    end = time.perf_counter()
    print(f"多线程耗时: {end - start:.2f} 秒")

    # --- 3. 多进程 (Multiprocessing) ---
    print(f"\n开始多进程任务 (2个进程)...")
    p1 = multiprocessing.Process(target=cpu_bound_task, args=(COUNT,))
    p2 = multiprocessing.Process(target=cpu_bound_task, args=(COUNT,))

    start = time.perf_counter()
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    end = time.perf_counter()
    print(f"多进程耗时: {end - start:.2f} 秒")

"""
# 总核数 = 物理 CPU 个数 X 每颗物理 CPU 的核数
# 总逻辑 CPU 数 = 物理 CPU 个数 X 每颗物理 CPU 的核数 X 超线程数

# 查看物理 CPU 个数
$ cat /proc/cpuinfo | grep "physical id" | sort | uniq | wc -l
2

# 查看每个物理 CPU 中 core 的个数(即核数)
$ cat /proc/cpuinfo | grep "cpu cores" | uniq
cpu cores	: 56

# 查看逻辑 CPU 的个数
$ cat /proc/cpuinfo| grep "processor"| wc -l
224

$ python 03.py
开始单线程任务...
单线程耗时: 1.89 秒

开始多线程任务 (2个线程)...
多线程耗时: 1.92 秒

开始多进程任务 (2个进程)...
多进程耗时: 0.95 秒
$

典型结果与数据分析

在我的 56 核处理器上, 运行结果通常如下:

单线程: 约 1.89 秒
多线程: 约 1.92 秒(甚至更久一点点)
多进程: 约 0.95 秒(理论减半)

为什么多线程反而慢了?

观察结果你会发现, 多线程跑完总任务的时间, 和单线程一个接一个跑完的时间几乎一样.

* 原因: 当线程 1 获取了 GIL 正在计算时, 线程 2 只能在旁边看着, 无法进入 CPU 运行.
* 副作用: 由于两个线程在不断地尝试获取和释放 GIL, 以及操作系统进行线程上下文切换(Context Switch), 这些开销反而导致总时间略长于单线程.

为什么多进程快了?

* 原因: multiprocessing 模块会启动两个独立的 Python 解释器实例. 每个进程都有自己独立的内存空间和自己独立的 GIL.
* 结果: 这两个进程可以分别运行在 CPU 的两个不同物理核心上, 实现真正的并行计算(Parallelism), 时间减半.

高级开发者的建议总结

判定任务类型:

* CPU 密集型(如: 加密、图像处理、大规模数学运算): 必须用 multiprocessing.
* IO 密集型(如: 网络请求、文件读写、数据库操作): 推荐用 threading 或 asyncio. 因为在等待 IO 时, Python 会主动释放 GIL, 从而让其他线程运行.

GIL 的未来

Python 3.13 已经引入了实验性的禁用 GIL (nogil) 模式. 但在 2025 年及以前的绝大部分生产环境中, GIL 依然是默认开启的, 上述规则依然适用.

计算重负载的终极方案

如果你有极致的性能需求, 高级开发人员通常会使用 C/C++ 编写扩展模块, 或者使用 NumPy/Pandas. 这些库底层是用 C 写的, 它们在进行大规模数值运算时会显式地释放 GIL, 从而让 Python 的多线程也能在计算上获得加速.
通过这个实验, 你应该能深刻理解为什么"Python 多线程"在计算领域经常被诟病, 以及为什么"多进程"才是处理重负载的正确姿势.
"""
