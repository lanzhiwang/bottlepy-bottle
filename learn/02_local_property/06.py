"""
2. 风险二: 子类命名冲突(Attribute Shadowing)
在大型项目中, 类经常被继承. 如果基类使用了 self._ls 或 self.ls, 而子类不小心也定义了同名属性, 基类的线程隔离逻辑会直接瘫痪.
"""

import threading


class BaseService:
    def __init__(self):
        self.ls = threading.local()


class MyBusinessService(BaseService):
    def __init__(self):
        super().__init__()
        # 开发者并不知道父类用了 'ls' 这个名字
        # 这里可能只是想存储一个 'log_system' 的缩写
        self.ls = "LogSystem_Initialized"


service = MyBusinessService()
# 此时, BaseService 依赖的线程隔离机制已经完全失效, 因为 self.ls 被覆盖为了字符串
