import sys


def load(target, **namespace):
    """Import a module or fetch an object from a module.

    * ``package.module`` returns `module` as a module object.
    * ``pack.mod:name`` returns the module variable `name` from `pack.mod`.
    * ``pack.mod:func()`` calls `pack.mod.func()` and returns the result.

    The last form accepts not only function calls, but any type of
    expression. Keyword arguments passed to this function are available as
    local variables. Example: ``import_string('re:compile(x)', x='[a-z]')``

    load 函数是 Python 动态编程的一个典型缩影, 常见于 Bottle 框架的内部工具集. 它的核心任务是将字符串转换为活生生的 Python 对象. 这在插件系统、动态路由或配置驱动的开发中极其有用.

    """
    print(f"load target: {target}")
    print(f"load namespace: {namespace}")

    module, target = target.split(":", 1) if ":" in target else (target, None)
    print(f"load module: {module}")
    print(f"load target: {target}")

    print(f"load sys.modules before: {sys.modules}")
    if module not in sys.modules:
        __import__(module)
    print(f"load sys.modules after: {sys.modules}")

    print(f"load not target: {not target}")
    if not target:
        return sys.modules[module]

    """
    isalnum()
    The method returns True if all characters in the string are letters (a-z, A-Z) or digits (0-9).
    Otherwise, it returns False.
    Examples
    "Python3": True
    "ab123": True
    "12345": True
    "hello": True
    "": False
    "Pyth on": False
    "Python!": False
    "user_name": False
    """
    print(f"load not target.isalnum: {target.isalnum()}")
    if target.isalnum():
        return getattr(sys.modules[module], target)

    package_name = module.split(".")[0]
    print(f"load module.split: {module.split(".")}")
    print(f"load package_name: {package_name}")

    namespace[package_name] = sys.modules[package_name]
    print(f"load namespace: {namespace}")
    print("%s.%s" % (module, target), namespace)
    return eval("%s.%s" % (module, target), namespace)


if __name__ == "__main__":
    # 假设根据配置选择 json 模块
    m = load("json")
    print(m.dumps({"status": "ok"}))  # 输出: {"status": "ok"}

    print("-------" * 10)

    # 加载 os 模块下的 path 属性
    path_tool = load("os:path")
    print(path_tool.join("home", "user"))  # 输出: home/user (Linux环境下)

    print("-------" * 10)

    # 加载 datetime 模块下的 datetime 类
    dt_class = load("datetime:datetime")
    print(dt_class.now())

    print("-------" * 10)

    # 动态编译正则表达式, x 是通过关键字参数传入 eval 命名空间的
    regex = load("re:compile(x)", x="^[0-9]+$")
    print(regex.match("12345"))  # <re.Match object; ...>

    print("-------" * 10)

    # 进行数学运算
    val = load("math:pow(a, b)", a=2, b=10)
    print(val)  # 1024.0

    print("-------" * 10)

    # 假设你正在写一个支持动态控制器加载的框架
    # 配置信息
    config = {"handler": "myapp.controllers.user:UserController()"}

    # 动态实例化控制器
    controller = load(config["handler"])
    # 现在 controller 是 UserController 的一个实例
