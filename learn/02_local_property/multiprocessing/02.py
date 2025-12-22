"""
我运行了一个 Python 脚本, 相当于在操作系统开启了一个进程(主进程), 我在脚本中分别创建了两个子进程(Proc-A 和 Proc-A)

我又在主进程、Proc-A 和 Proc-A 中分别创建了两个线程

请使用代码示例说明以上结构, 并说明在 linux 终端如何查看这种结构

你好! 作为一名高级开发人员, 我非常乐意为你构建这个"多进程 + 多线程"的混合架构示例.
这种结构在高性能网络服务器(如 Gunicorn 配合多个 Worker 和 Threads)中非常常见.

1. Python 代码实现

我们将编写一个脚本, 主进程会创建两个线程和两个子进程, 而每个子进程内部又会创建自己的两个线程. 为了方便你在终端观察, 我们会让所有线程进入长睡眠状态.

"""

import multiprocessing
import threading
import os
import time


def thread_task(name):
    """线程执行的任务"""
    pid = os.getpid()
    thread_id = threading.get_ident()
    print(f"  [线程启动] 进程PID: {pid} | 线程ID: {thread_id} | 名称: {name}")
    # 保持存活以便查看
    time.sleep(1000)


def create_threads(prefix):
    """在当前进程中创建两个线程"""
    t1 = threading.Thread(
        target=thread_task, args=(f"{prefix}-Thread-1",), name=f"{prefix}-T1"
    )
    t2 = threading.Thread(
        target=thread_task, args=(f"{prefix}-Thread-2",), name=f"{prefix}-T2"
    )
    t1.start()
    t2.start()


def process_worker(name):
    """子进程执行的任务"""
    pid = os.getpid()
    ppid = os.getppid()
    print(f"\n[子进程启动] 名称: {name} | PID: {pid} | 父进程PPID: {ppid}")

    # 在子进程中创建两个线程
    create_threads(name)

    # 保持进程存活
    time.sleep(100)


if __name__ == "__main__":
    main_pid = os.getpid()
    print(f"[主进程启动] PID: {main_pid}")

    # 1. 在主进程中创建两个线程
    print("主进程正在创建自己的线程...")
    create_threads("MainProc")

    # 2. 创建两个子进程
    processes = []
    for name in ["Proc-A", "Proc-B"]:
        p = multiprocessing.Process(target=process_worker, args=(name,), name=name)
        p.start()
        processes.append(p)

    print("\n系统结构已就绪. 请打开另一个终端查看进程树...")

    for p in processes:
        p.join()


"""
$ python 02.py
[主进程启动] PID: 927136
主进程正在创建自己的线程...
  [线程启动] 进程PID: 927136 | 线程ID: 140030523512384 | 名称: MainProc-Thread-1
  [线程启动] 进程PID: 927136 | 线程ID: 140030515119680 | 名称: MainProc-Thread-2

系统结构已就绪. 请打开另一个终端查看进程树...

[子进程启动] 名称: Proc-A | PID: 927139 | 父进程PPID: 927136
  [线程启动] 进程PID: 927139 | 线程ID: 140030515119680 | 名称: Proc-A-Thread-1
  [线程启动] 进程PID: 927139 | 线程ID: 140030523512384 | 名称: Proc-A-Thread-2

[子进程启动] 名称: Proc-B | PID: 927140 | 父进程PPID: 927136
  [线程启动] 进程PID: 927140 | 线程ID: 140030515119680 | 名称: Proc-B-Thread-1
  [线程启动] 进程PID: 927140 | 线程ID: 140030523512384 | 名称: Proc-B-Thread-2

$ pstree -p -t -a 927136
python,927136 02.py
  ├─python,927139 02.py
  │   ├─{python},927141
  │   └─{python},927142
  ├─python,927140 02.py
  │   ├─{python},927143
  │   └─{python},927144
  ├─{python},927137
  └─{python},927138
$
$ pstree -p -t 927136
python(927136)─┬─python(927139)─┬─{python}(927141)
               │                └─{python}(927142)
               ├─python(927140)─┬─{python}(927143)
               │                └─{python}(927144)
               ├─{python}(927137)
               └─{python}(927138)
$

2. 在 Linux 终端如何查看这种结构

在 Linux 中, 有几种非常强大的工具可以观察这种嵌套层级关系.

假设你的主进程 PID 是 1234(运行脚本时控制台会打印出来).

方法 A: 使用 pstree (最直观)

这是查看进程/线程树最清晰的方法.

-p: 显示 PID.
-t: 显示线程名(如果可用).
-a: 显示命令行参数.

# 请将 <PID> 替换为你程序打印的主进程 PID
pstree -p -t <PID>

预期输出效果图:
python(1234)─┬─{python}(1235)  <-- 主进程的线程1
             ├─{python}(1236)  <-- 主进程的线程2
             ├─Proc-A(1237)─┬─{Proc-A}(1239) <-- 子进程A的线程1
             │              └─{Proc-A}(1240) <-- 子进程A的线程2
             └─Proc-B(1238)─┬─{Proc-B}(1241) <-- 子进程B的线程1
                            └─{Proc-B}(1242) <-- 子进程B的线程2


方法 B: 使用 ps 命令
如果你想看详细的列表, 可以使用 ps 命令查看特定进程及其下的所有线程.
-H: 显示层级(树状).
-m: 在进程后列出线程.
-L: 显示 LWP (轻量级进程, 即线程 ID).

ps -fL -u <你的用户名> | grep python

# 或者针对特定 PID
ps -mp <PID> -o LWP,PNP,CPU,COMMAND

方法 C: 使用 htop (交互式)
如果你安装了 htop, 这是最强大的实时观察工具:
在终端输入 htop

方法 D: 查看 /proc 文件系统
在 Linux 中, 一切皆文件. 你可以直接查看内核导出的信息:

# 查看主进程下的线程
ls /proc/<PID>/task

# 查看主进程及其子进程的层级
cat /proc/<PID>/status | grep Threads


3. 高级开发人员的笔记
PID vs TID (LWP): 在 Linux 核心中, 线程被视为"轻量级进程". 当你看到 pstree 或 ps 打印出不同的编号时, 主进程及其子进程拥有独立的 PID, 而每个进程内部的线程拥有独立的 TID(或称 LWP ID).

资源共享:
Proc-A 和 Proc-B 之间不共享内存.
Proc-A 内部的两个线程共享 Proc-A 的内存地址空间.

GIL (全局解释器锁):
虽然主进程、Proc-A、Proc-B 共有 6 个用户自定义线程, 但由于 Python GIL 的存在, 每一个进程内部的两个线程无法在多核 CPU 上实现真正的并行计算, 但三个进程之间是可以并行运行在不同核心上的.
这就是为什么在 Python 中处理 CPU 密集型任务时, 我们通常用"多进程"而不是纯"多线程".

"""
