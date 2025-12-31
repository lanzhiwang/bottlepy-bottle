import os
import sys
import time
import subprocess
import tempfile

# 检查间隔(秒)
INTERVAL = 2


def run_child(lockfile):
    """
    子进程逻辑: 模拟业务运行, 同时检查父进程是否活着
    """
    print(f"  [子进程 {os.getpid()}] 启动成功.")

    count = 0
    while True:
        count += 1

        """
        子进程如何检查父进程?
        方法: os.path.exists(lockfile) 和 os.path.getmtime(lockfile).
        原理:
        文件消失: 父进程正常关闭时会 os.unlink(lockfile). 子进程一旦发现文件没了, 就知道该撤了.
        心跳超时: 如果父进程崩溃(Crash)或死锁, 它可能来不及删文件. 但因为它不再运行循环, 所以没法执行 os.utime(lockfile, None) 来更新文件的时间戳. 子进程检查文件时间, 发现"这时间戳是 6 秒前的, 太老了", 从而判定父进程已死.
        """

        # 1. 检查锁文件是否存在
        if not os.path.exists(lockfile):
            print(f"  [子进程] 锁文件丢失, 判定父进程已退出, 子进程自我终止.")
            sys.exit(0)

        # 2. 检查锁文件的修改时间(心跳检查)
        # 如果父进程由于意外崩溃, 它就没法更新时间戳
        last_heartbeat = os.path.getmtime(lockfile)
        if time.time() - last_heartbeat > INTERVAL * 3:
            print(f"  [子进程] 心跳超时(父进程太久没理我), 判定父进程已挂, 自我终止.")
            sys.exit(0)

        print(f"  [子进程] 业务运行中... (心跳正常) 第 {count} 秒")

        # 模拟: 运行到第 10 秒时, 模拟代码改动, 要求重启
        if count == 10:
            print(f"  [子进程] 检测到'代码改动'! 通知父进程重启我.")
            sys.exit(3)  # 返回状态码 3

        time.sleep(1)


def run_parent():
    """
    父进程逻辑: 监控子进程, 并发送心跳
    """
    print(f"[父进程 {os.getpid()}] 启动监控.")

    # 创建一个临时锁文件作为"心跳站"
    fd, lockfile = tempfile.mkstemp(prefix="heartbeat.", suffix=".lock")
    os.close(fd)

    # 准备环境变量, 让子进程知道自己是子进程, 并知道锁文件在哪
    env = os.environ.copy()
    env["IS_CHILD"] = "true"
    env["LOCKFILE_PATH"] = lockfile

    try:
        while os.path.exists(lockfile):
            print(f"[父进程] 正在启动/重启子进程... {[sys.executable, __file__]}")
            # 启动自己(同一个脚本), 但带上 IS_CHILD 环境变量
            p = subprocess.Popen([sys.executable, __file__], env=env)

            """
            1. 父进程如何检查子进程?
            方法: p.poll().
            原理: subprocess.Popen 返回的对象 p 有一个 poll() 方法.
            如果子进程还在运行, 它返回 None; 如果子进程结束了, 它会返回子进程的退出码(Exit Code).
            父进程在 while p.poll() is None 循环里一直守着它.
            """
            # 内部循环: 只要子进程还在跑, 父进程就不断更新锁文件时间
            while p.poll() is None:
                # 给锁文件刷一下时间戳(更新 mtime)
                # 就像是在对子进程喊: "我还活着!"
                os.utime(lockfile, None)
                time.sleep(INTERVAL)

            # 子进程退出了, 检查退出码
            print(f"[父进程] 子进程已退出, 退出码: {p.returncode}")

            if p.returncode == 3:
                print(f"[父进程] 收到重启信号(3), 准备下一轮循环启动子进程.")
                continue
            else:
                print(f"[父进程] 子进程正常退出或出错退出, 父进程也准备退出.")
                break

    except KeyboardInterrupt:
        print(f"\n[父进程] 接收到 Ctrl+C, 清理并退出.")
    finally:
        if os.path.exists(lockfile):
            os.unlink(lockfile)


if __name__ == "__main__":
    # 根据环境变量判断当前身份
    print(f'os.environ.get("IS_CHILD"): {os.environ.get("IS_CHILD")}')
    if os.environ.get("IS_CHILD") == "true":
        lockfile = os.environ.get("LOCKFILE_PATH")
        run_child(lockfile)
    else:
        run_parent()

"""
$ python learn/09_run/heartbeat_demo.py
os.environ.get("IS_CHILD"): None
[父进程 4136612] 启动监控.
[父进程] 正在启动/重启子进程... ['/root/miniconda3/envs/bottle_python_3_12/bin/python', '/root/bottle/learn/09_run/heartbeat_demo.py']
os.environ.get("IS_CHILD"): true
  [子进程 4136613] 启动成功.
  [子进程] 业务运行中... (心跳正常) 第 1 秒
  [子进程] 业务运行中... (心跳正常) 第 2 秒
  [子进程] 业务运行中... (心跳正常) 第 3 秒
  [子进程] 业务运行中... (心跳正常) 第 4 秒
  [子进程] 业务运行中... (心跳正常) 第 5 秒
  [子进程] 业务运行中... (心跳正常) 第 6 秒
  [子进程] 业务运行中... (心跳正常) 第 7 秒
  [子进程] 业务运行中... (心跳正常) 第 8 秒
  [子进程] 业务运行中... (心跳正常) 第 9 秒
  [子进程] 业务运行中... (心跳正常) 第 10 秒
  [子进程] 检测到'代码改动'! 通知父进程重启我.
[父进程] 子进程已退出, 退出码: 3
[父进程] 收到重启信号(3), 准备下一轮循环启动子进程.
[父进程] 正在启动/重启子进程... ['/root/miniconda3/envs/bottle_python_3_12/bin/python', '/root/bottle/learn/09_run/heartbeat_demo.py']
os.environ.get("IS_CHILD"): true
  [子进程 4136750] 启动成功.
  [子进程] 业务运行中... (心跳正常) 第 1 秒
  [子进程] 业务运行中... (心跳正常) 第 2 秒
  [子进程] 业务运行中... (心跳正常) 第 3 秒
  [子进程] 业务运行中... (心跳正常) 第 4 秒
  [子进程] 业务运行中... (心跳正常) 第 5 秒
  [子进程] 业务运行中... (心跳正常) 第 6 秒
  [子进程] 业务运行中... (心跳正常) 第 7 秒
  [子进程] 业务运行中... (心跳正常) 第 8 秒
  [子进程] 业务运行中... (心跳正常) 第 9 秒
  [子进程] 业务运行中... (心跳正常) 第 10 秒
  [子进程] 检测到'代码改动'! 通知父进程重启我.
[父进程] 子进程已退出, 退出码: 3
[父进程] 收到重启信号(3), 准备下一轮循环启动子进程.
[父进程] 正在启动/重启子进程... ['/root/miniconda3/envs/bottle_python_3_12/bin/python', '/root/bottle/learn/09_run/heartbeat_demo.py']
os.environ.get("IS_CHILD"): true
  [子进程 4136983] 启动成功.
  [子进程] 业务运行中... (心跳正常) 第 1 秒
  [子进程] 业务运行中... (心跳正常) 第 2 秒
  [子进程] 业务运行中... (心跳正常) 第 3 秒
  [子进程] 业务运行中... (心跳正常) 第 4 秒
  [子进程] 业务运行中... (心跳正常) 第 5 秒
  [子进程] 业务运行中... (心跳正常) 第 6 秒
  [子进程] 业务运行中... (心跳正常) 第 7 秒
  [子进程] 业务运行中... (心跳正常) 第 8 秒
  [子进程] 业务运行中... (心跳正常) 第 9 秒
  [子进程] 业务运行中... (心跳正常) 第 10 秒
  [子进程] 检测到'代码改动'! 通知父进程重启我.
[父进程] 子进程已退出, 退出码: 3
[父进程] 收到重启信号(3), 准备下一轮循环启动子进程.
[父进程] 正在启动/重启子进程... ['/root/miniconda3/envs/bottle_python_3_12/bin/python', '/root/bottle/learn/09_run/heartbeat_demo.py']
os.environ.get("IS_CHILD"): true
  [子进程 4137082] 启动成功.
  [子进程] 业务运行中... (心跳正常) 第 1 秒
  [子进程] 业务运行中... (心跳正常) 第 2 秒
  [子进程] 业务运行中... (心跳正常) 第 3 秒
  [子进程] 业务运行中... (心跳正常) 第 4 秒
  [子进程] 业务运行中... (心跳正常) 第 5 秒
  [子进程] 业务运行中... (心跳正常) 第 6 秒
  [子进程] 业务运行中... (心跳正常) 第 7 秒
  [子进程] 业务运行中... (心跳正常) 第 8 秒
  [子进程] 业务运行中... (心跳正常) 第 9 秒
  [子进程] 业务运行中... (心跳正常) 第 10 秒
  [子进程] 检测到'代码改动'! 通知父进程重启我.
[父进程] 子进程已退出, 退出码: 3
[父进程] 收到重启信号(3), 准备下一轮循环启动子进程.
[父进程] 正在启动/重启子进程... ['/root/miniconda3/envs/bottle_python_3_12/bin/python', '/root/bottle/learn/09_run/heartbeat_demo.py']
os.environ.get("IS_CHILD"): true
  [子进程 4137251] 启动成功.
  [子进程] 业务运行中... (心跳正常) 第 1 秒
  [子进程] 业务运行中... (心跳正常) 第 2 秒
  [子进程] 业务运行中... (心跳正常) 第 3 秒
  [子进程] 业务运行中... (心跳正常) 第 4 秒
  [子进程] 业务运行中... (心跳正常) 第 5 秒
  [子进程] 业务运行中... (心跳正常) 第 6 秒
  [子进程] 业务运行中... (心跳正常) 第 7 秒
^C
[父进程] 接收到 Ctrl+C, 清理并退出.
Traceback (most recent call last):
  File "/root/bottle/learn/09_run/heartbeat_demo.py", line 108, in <module>
    run_child(lockfile)
  File "/root/bottle/learn/09_run/heartbeat_demo.py", line 48, in run_child
    time.sleep(1)
KeyboardInterrupt
$
"""
