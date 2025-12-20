import threading
import time
import random


def _local_property():
    ls = threading.local()

    def fget(_):
        print("_local_property fget _:", _)
        try:
            print("_local_property fget ls.var:", ls.var)
            return ls.var
        except AttributeError:
            raise RuntimeError("Request context not initialized.")

    def fset(_, value):
        print("_local_property fset _:", _)
        print("_local_property fset value:", value)
        ls.var = value

    def fdel(_):
        print("_local_property fdel _:", _)
        del ls.var

    return property(fget, fset, fdel, "Thread-local property")


# --- 使用示例 ---


class LocalRequest(object):
    environ = _local_property()


# 全局共享同一个 context 实例, 但其内部属性是线程隔离的
request = LocalRequest()
print("request:", request)
print("request:", dir(request))


def thread_worker(thread_data: str):
    """
    线程任务函数
    """
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] 启动...")

    # 1. 验证初始状态: 尝试获取未设置的属性应抛出异常
    try:
        _ = request.environ
    except RuntimeError as e:
        print(f"[{thread_name}] 预期内的错误: {e}")

    # 2. 设置线程局部变量
    print(f"[{thread_name}] 设置 user_id 为: {thread_data}")
    request.environ = thread_data

    # 3. 模拟耗时操作, 期间可能有其他线程在修改该属性
    # 如果不是线程局部的, 这里的值会被另一个线程覆盖
    sleep_time = random.uniform(0.5, 1.5)
    time.sleep(sleep_time)

    # 4. 验证值是否保持不变
    current_val = request.environ
    if current_val == thread_data:
        print(f"[{thread_name}] 验证通过! user_id 依然是: {current_val}")
    else:
        print(f"[{thread_name}] 警告! 数据发生污染! 当前值: {current_val}")

    # 5. 清理(可选)
    del request.environ
    print(f"[{thread_name}] 已删除 user_id")


if __name__ == "__main__":
    print("--- 开始线程隔离测试 ---")

    # 创建两个线程, 分别赋予不同的数据
    t1 = threading.Thread(target=thread_worker, args=("USER_ALPHA",), name="Thread-A")
    # t2 = threading.Thread(target=thread_worker, args=("USER_BETA",), name="Thread-B")

    t1.start()
    # t2.start()

    t1.join()
    # t2.join()

    print("--- 测试结束 ---")

"""
$ python 11.py
request: <__main__.LocalRequest object at 0x7ffaa3cd9280>
request: ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'environ']
--- 开始线程隔离测试 ---
[Thread-A] 启动...
_local_property fget _: <__main__.LocalRequest object at 0x7ffaa3cd9280>
[Thread-A] 预期内的错误: Request context not initialized.
[Thread-A] 设置 user_id 为: USER_ALPHA
_local_property fset _: <__main__.LocalRequest object at 0x7ffaa3cd9280>
_local_property fset value: USER_ALPHA
_local_property fget _: <__main__.LocalRequest object at 0x7ffaa3cd9280>
_local_property fget ls.var: USER_ALPHA
[Thread-A] 验证通过! user_id 依然是: USER_ALPHA
_local_property fdel _: <__main__.LocalRequest object at 0x7ffaa3cd9280>
[Thread-A] 已删除 user_id
--- 测试结束 ---
$

"""
