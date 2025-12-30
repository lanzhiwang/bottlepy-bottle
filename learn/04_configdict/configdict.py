import sys
import configparser
import weakref

basestring = str

_UNSET = object()

py = sys.version_info
py3k = py.major > 2


def load(target, **namespace):
    """Import a module or fetch an object from a module.

    * ``package.module`` returns `module` as a module object.
    * ``pack.mod:name`` returns the module variable `name` from `pack.mod`.
    * ``pack.mod:func()`` calls `pack.mod.func()` and returns the result.

    The last form accepts not only function calls, but any type of
    expression. Keyword arguments passed to this function are available as
    local variables. Example: ``import_string('re:compile(x)', x='[a-z]')``
    """
    module, target = target.split(":", 1) if ":" in target else (target, None)
    if module not in sys.modules:
        __import__(module)
    if not target:
        return sys.modules[module]
    if target.isalnum():
        return getattr(sys.modules[module], target)
    package_name = module.split(".")[0]
    namespace[package_name] = sys.modules[package_name]
    return eval("%s.%s" % (module, target), namespace)


class ConfigDict(dict):
    """A dict-like configuration storage with additional support for
    namespaces, validators, meta-data and overlays.

    This dict-like class is heavily optimized for read access.
    Read-only methods and item access should be as fast as a native dict.

    一个类字典的配置存储类, 额外支持命名空间、验证器、元数据和叠加层(Overlay).
    该类针对读取访问进行了深度优化. 只读方法和项访问的速度与原生字典一致.

    ConfigDict 不仅仅是一个字典, 而是一个具有层级命名空间、元数据支持、变更监听、以及"叠加层(Overlay)"功能的配置中心.
    核心设计点:
    1. 高性能读取: 通过 __slots__ 减少内存占用. 不同于传统的 ChainMap(每次查找都要遍历多个字典),
       它采用主动推送的方式: 当父级配置变化时, 自动同步到所有子级(Overlay), 确保读取操作和原生 dict 一样快.
    2. 命名空间扁平化(Squashing): 它支持将嵌套字典 {'a': {'b': 1}} 转化为扁平化的键 'a.b': 1.
    3. 叠加层(Overlay)机制: 类似于 Git 的分支. 你可以创建一个 Overlay, 它继承父配置的所有值(称为 Virtual Keys).
       如果你修改了 Overlay 的值, 它会变成该层私有的(Non-virtual), 而不会影响父层.
    4. 元数据与过滤器: 每个键可以绑定元数据(如帮助文本). 最重要的是 filter 元数据, 它能在赋值时自动转换数据(例如将字符串转为整数).
    """

    # 使用 __slots__ 限制属性, 减少内存占用并提升属性访问速度
    __slots__ = (
        "_meta",  # 存储键的元数据(如过滤器、帮助信息)
        "_change_listener",  # 存储变更监听回调函数
        "_overlays",  # 存储对该配置层进行的弱引用叠加层列表
        "_virtual_keys",  # 存储从父级继承而来的"虚拟键"集合
        "_source",  # 如果当前是叠加层, 指向其源(父级)配置对象
        "__weakref__",  # 支持弱引用
    )

    def __init__(self):
        self._meta = {}
        self._change_listener = []
        #: Weak references of overlays that need to be kept in sync.
        self._overlays = []
        #: Config that is the source for this overlay.
        self._source = None
        #: Keys of values copied from the source (values we do not own)
        self._virtual_keys = set()

    def load_module(self, name, squash=True):
        """Load values from a Python module.

        Import a python module by name and add all upper-case module-level
        variables to this config dict.

        从 Python 模块中加载配置.
        导入模块并将所有大写的模块级变量添加到配置字典中.

        :param name: Module name to import and load.
        :param squash: If true (default), nested dicts are assumed to
           represent namespaces and flattened (see :meth:`load_dict`).
           命名空间扁平化(Squashing): 它支持将嵌套字典 {'a': {'b': 1}} 转化为扁平化的键 'a.b': 1.
        """

        print(f"ConfigDict load_module name: {name}")
        print(f"ConfigDict load_module squash: {squash}")

        config_obj = load(name)
        print(f"ConfigDict load_module config_obj: {config_obj}")
        print(f"ConfigDict load_module config_obj: {dir(config_obj)}")

        # 过滤出所有大写的属性(约定: 配置变量通常大写)
        obj = {
            key: getattr(config_obj, key) for key in dir(config_obj) if key.isupper()
        }
        print(f"ConfigDict load_module obj: {obj}")

        if squash:
            self.load_dict(obj)  # 扁平化处理
        else:
            self.update(obj)  # 普通更新
        return self

    def load_config(self, filename, **options):
        """Load values from ``*.ini`` style config files using configparser.

        INI style sections (e.g. ``[section]``) are used as namespace for
        all keys within that section. Both section and key names may contain
        dots as namespace separators and are converted to lower-case.

        The special sections ``[bottle]`` and ``[ROOT]`` refer to the root
        namespace and the ``[DEFAULT]`` section defines default values for all
        other sections.

        加载 *.ini 格式的配置文件.
        INI 的 [section] 会作为键的命名空间前缀.

        :param filename: The path of a config file, or a list of paths.
        :param options: All keyword parameters are passed to the underlying
            :class:`python:configparser.ConfigParser` constructor call.

        """
        print(f"ConfigDict load_config filename: {filename}")
        print(f"ConfigDict load_config options: {options}")

        options.setdefault("allow_no_value", True)
        if py3k:
            options.setdefault("interpolation", configparser.ExtendedInterpolation())
        print(f"ConfigDict load_config options: {options}")

        conf = configparser.ConfigParser(**options)
        print(f"ConfigDict load_config conf: {conf}")
        conf.read(filename)
        print(f"ConfigDict load_config conf: {conf}")

        for section in conf.sections():
            print(f"ConfigDict load_config section: {section}")
            for key in conf.options(section):
                print(f"ConfigDict load_config key: {key}")
                value = conf.get(section, key)
                print(f"ConfigDict load_config value: {value}")
                # 排除特殊的根命名空间
                if section not in ("bottle", "ROOT"):
                    key = section + "." + key
                print(f"ConfigDict load_config key: {key}")
                self[key.lower()] = value
        return self

    def load_dict(self, source, namespace=""):
        """Load values from a dictionary structure. Nesting can be used to
        represent namespaces.

        从字典结构加载. 支持嵌套字典递归展开为点分隔的命名空间.
        例如: {'a': {'b': 1}} -> {'a.b': 1}

        >>> c = ConfigDict()
        >>> c.load_dict({'some': {'namespace': {'key': 'value'} } })
        {'some.namespace.key': 'value'}
        """
        print(f"ConfigDict load_dict source: {source}")
        print(f"ConfigDict load_dict namespace: {namespace}")

        for key, value in source.items():
            if isinstance(key, basestring):
                nskey = (namespace + "." + key).strip(".")
                if isinstance(value, dict):
                    self.load_dict(value, namespace=nskey)  # 递归展开
                else:
                    self[nskey] = value
            else:
                raise TypeError("Key has type %r (not a string)" % type(key))
        return self

    def update(self, *a, **ka):
        """If the first parameter is a string, all keys are prefixed with this
        namespace. Apart from that it works just as the usual dict.update().

        支持命名空间前缀的更新方法.
        c.update('some.ns', key='value') -> c['some.ns.key'] = 'value'

        >>> c = ConfigDict()
        >>> c.update('some.namespace', key='value')
        """
        print(f"ConfigDict update self: {self}")
        print(f"ConfigDict update a: {a}")
        print(f"ConfigDict update ka: {ka}")

        prefix = ""
        if a and isinstance(a[0], basestring):
            prefix = a[0].strip(".") + "."
            a = a[1:]
        print(f"ConfigDict update prefix: {prefix}")
        print(f"ConfigDict update a: {a}")
        print(f"ConfigDict update dict(*a, **ka): {dict(*a, **ka)}")
        for key, value in dict(*a, **ka).items():
            self[prefix + key] = value

    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value
        return self[key]

    def __setitem__(self, key, value):
        """
        写入操作: 包含过滤器触发、监听器通知及叠加层同步
        """

        print(f"ConfigDict __setitem__ key: {key}")
        print(f"ConfigDict __setitem__ value: {value}")

        if not isinstance(key, basestring):
            raise TypeError("Key has type %r (not a string)" % type(key))

        # 一旦手动设置, 该键就不再是"虚拟键"(即不再随父级同步)
        """
        The Python set.discard() method removes a specified element from a set if it is present.
        A key feature is that it does not raise an error if the element is not found,
        unlike the set.remove() method.
        """
        print(f"ConfigDict __setitem__ 删除虚拟键")
        print(f"ConfigDict __setitem__ self._virtual_keys: {self._virtual_keys}")
        self._virtual_keys.discard(key)
        print(f"ConfigDict __setitem__ self._virtual_keys: {self._virtual_keys}")

        # 核心功能: 如果定义了 filter 元数据, 则在存储前转换数据(如转 int)
        print(f"ConfigDict __setitem__ meta 过滤")
        print(f"ConfigDict __setitem__ value: {value}")
        value = self.meta_get(key, "filter", lambda x: x)(value)
        print(f"ConfigDict __setitem__ value: {value}")

        # 如果值没变, 则跳过后续逻辑以优化性能
        print(f"ConfigDict __setitem__ 如果值没变, 则跳过后续逻辑以优化性能")
        print(f"ConfigDict __setitem__ self: {self}")
        if key in self and self[key] is value:
            return
        print(f"ConfigDict __setitem__ self: {self}")

        # 触发变更监听器
        print(f"ConfigDict __setitem__ 触发变更监听器")
        self._on_change(key, value)

        # 调用父类 dict 的设置方法
        print(f"ConfigDict __setitem__ 调用父类 dict 的设置方法")
        print(f"ConfigDict __setitem__ self: {self}")
        dict.__setitem__(self, key, value)
        print(f"ConfigDict __setitem__ self: {self}")

        # 递归更新所有子级叠加层
        print(f"ConfigDict __setitem__ 递归更新所有子级叠加层")
        for overlay in self._iter_overlays():
            print(f"ConfigDict __setitem__ overlay: {overlay}")
            overlay._set_virtual(key, value)

    def __delitem__(self, key):
        """
        删除操作: 如果存在父级, 删除后会恢复为父级的虚拟值
        """
        if key not in self:
            raise KeyError(key)
        if key in self._virtual_keys:
            # 无法删除虚拟键(继承自父级)
            raise KeyError("Virtual keys cannot be deleted: %s" % key)

        if self._source and key in self._source:
            # Not virtual, but present in source -> Restore virtual value
            # 如果父级有这个值, 删除本级修改后, 恢复为父级的值
            dict.__delitem__(self, key)
            self._set_virtual(key, self._source[key])
        else:
            # not virtual, not present in source. This is OUR value
            # 彻底删除(父级也没有)
            self._on_change(key, None)
            dict.__delitem__(self, key)
            for overlay in self._iter_overlays():
                overlay._delete_virtual(key)

    def _set_virtual(self, key, value):
        """
        Recursively set or update virtual keys.

        内部方法: 递归设置或更新虚拟键.
        当父级配置变化时, 该方法确保子级同步.
        """

        # 如果子级已经有了自己独立设置的值(非虚拟), 则不覆盖它
        if key in self and key not in self._virtual_keys:
            return  # Do nothing for non-virtual keys.

        self._virtual_keys.add(key)
        if key in self and self[key] is not value:
            self._on_change(key, value)
        dict.__setitem__(self, key, value)
        # 继续向下传递给孙级叠加层
        for overlay in self._iter_overlays():
            overlay._set_virtual(key, value)

    def _delete_virtual(self, key):
        """Recursively delete virtual entry."""
        if key not in self._virtual_keys:
            return  # Do nothing for non-virtual keys.

        if key in self:
            self._on_change(key, None)
        dict.__delitem__(self, key)
        self._virtual_keys.discard(key)
        for overlay in self._iter_overlays():
            overlay._delete_virtual(key)

    def _on_change(self, key, value):
        """
        执行所有的变更监听回调
        """
        for cb in self._change_listener:
            if cb(self, key, value):
                # 如果回调返回 True, 则停止后续回调
                return True

    def _add_change_listener(self, func):
        """
        @conf._add_change_listener
        def on_config_change(config, key, value):
            print(f"  [监听器] 配置项 '{key}' 已变更为: {value} (类型: {type(value)})")
        """
        self._change_listener.append(func)
        print(
            f"ConfigDict _add_change_listener self._change_listener: {self._change_listener}"
        )
        return func

    def meta_get(self, key, metafield, default=None):
        """
        Return the value of a meta field for a key.
        获取某个键绑定的元数据(例如: self.meta_get('port', 'filter'))
        """
        return self._meta.get(key, {}).get(metafield, default)

    def meta_set(self, key, metafield, value):
        """Set the meta field for a key to a new value.

        Meta-fields are shared between all members of an overlay tree.

        设置元数据. 元数据在整个 Overlay 树中是共享的

        conf.meta_set("server.port", "filter", int)  # 强制转整数
        conf.meta_set("server.debug", "filter", lambda x: x.lower() == "true")  # 转布尔
        """
        self._meta.setdefault(key, {})[metafield] = value
        print(f"ConfigDict meta_set self._meta: {self._meta}")

    def meta_list(self, key):
        """Return an iterable of meta field names defined for a key."""
        return self._meta.get(key, {}).keys()

    def _define(self, key, default=_UNSET, help=_UNSET, validate=_UNSET):
        """(Unstable) Shortcut for plugins to define own config parameters."""

        print(f"ConfigDict _define key: {key}")
        print(f"ConfigDict _define default: {default}")
        print(f"ConfigDict _define help: {help}")
        print(f"ConfigDict _define validate: {validate}")

        if default is not _UNSET:
            self.setdefault(key, default)

        if help is not _UNSET:
            self.meta_set(key, "help", help)

        if validate is not _UNSET:
            self.meta_set(key, "validate", validate)

    def _iter_overlays(self):
        for ref in self._overlays:
            overlay = ref()
            if overlay is not None:
                yield overlay

    def _make_overlay(self):
        """(Unstable) Create a new overlay that acts like a chained map: Values
        missing in the overlay are copied from the source map. Both maps
        share the same meta entries.

        Entries that were copied from the source are called 'virtual'. You
        can not delete virtual keys, but overwrite them, which turns them
        into non-virtual entries. Setting keys on an overlay never affects
        its source, but may affect any number of child overlays.

        Other than collections.ChainMap or most other implementations, this
        approach does not resolve missing keys on demand, but instead
        actively copies all values from the source to the overlay and keeps
        track of virtual and non-virtual keys internally. This removes any
        lookup-overhead. Read-access is as fast as a build-in dict for both
        virtual and non-virtual keys.

        Changes are propagated recursively and depth-first. A failing
        on-change handler in an overlay stops the propagation of virtual
        values and may result in an partly updated tree. Take extra care
        here and make sure that on-change handlers never fail.

        Used by Route.config

        创建一个叠加层(Overlay).
        叠加层像 ChainMap, 但读取速度更快.
        修改叠加层不会影响父级, 但父级的修改会实时同步给叠加层.
        """
        # Cleanup dead references
        # 清理已失效的弱引用
        print(f"ConfigDict _make_overlay 清理已失效的弱引用")
        print(f"ConfigDict _make_overlay self._overlays: {self._overlays}")
        self._overlays[:] = [ref for ref in self._overlays if ref() is not None]
        print(f"ConfigDict _make_overlay self._overlays: {self._overlays}")

        overlay = ConfigDict()
        overlay._meta = self._meta  # 所有叠加层共享同一份元数据
        overlay._source = self
        self._overlays.append(weakref.ref(overlay))
        # 将父级当前的所有值作为虚拟键拷贝到子级
        print(f"ConfigDict _make_overlay 将父级当前的所有值作为虚拟键拷贝到子级")
        for key in self:
            overlay._set_virtual(key, self[key])
        return overlay


def run_config_demo():
    # 1. 初始化
    print("--- 步骤 1. 初始化 ---")
    conf = ConfigDict()
    print(f"run_config_demo conf: {conf}")
    print()

    # 2. 演示 meta_set 和 filter (过滤器)
    # 过滤器是 ConfigDict 的灵魂, 它能确保输入数据的类型安全
    print("--- 步骤 2. 演示 meta_set 和 filter (过滤器) ---")
    conf.meta_set("server.port", "filter", int)  # 强制转整数
    conf.meta_set("server.debug", "filter", lambda x: x.lower() == "true")  # 转布尔
    print()

    # 3. 演示 _add_change_listener (变更监听)
    print("--- 步骤 3. 演示 _add_change_listener (变更监听) ---")

    @conf._add_change_listener
    def on_config_change(config, key, value):
        print(f"run_config_demo on_config_change config: {config}")
        print(f"run_config_demo on_config_change key: {key}")
        print(f"run_config_demo on_config_change value: {value}")
        return False

    print()

    # 4. 演示 load_config (加载 INI 文件)
    print("--- 步骤 4: 演示 load_config (加载 INI 文件) ---")
    conf.load_config("config.ini")
    # 此时会触发监听器, 且 port 会被 filter 转为 int, debug 转为 bool
    print(f"run_config_demo conf: {conf}")
    print()

    # 5. 演示 load_module (加载 Python 模块)
    print("--- 步骤 5: 演示 load_module (加载 Python 模块) ---")
    conf.load_module("app_config")  # 假设 app_config 在 sys.path 中, 或者当前目录
    print(f"run_config_demo conf: {conf}")
    print()

    # 6. 演示 load_dict (加载字典并扁平化)
    print("--- 步骤 6: 演示 load_dict (加载字典并扁平化) ---")
    conf.load_dict({"auth": {"methods": ["jwt", "session"], "secret": "top-secret"}})
    print(f"run_config_demo conf: {conf}")
    print()

    # 7. 演示 update (带命名空间的更新)
    print("--- 步骤 7: 演示 update (带命名空间的更新) ---")
    print(f"run_config_demo conf: {conf}")
    conf.update("storage", bucket="my-bucket", region="us-east-1")
    print(f"run_config_demo conf: {conf}")
    print()

    # 8. 演示读取 (高性能读取)
    print("--- 步骤 8: 演示读取 (高性能读取) ---")
    print(f"run_config_demo conf: {conf}")
    print(f"Port: {conf['server.port']}, Type: {type(conf['server.port'])}")
    print(f"Timeout: {conf['TIMEOUT']}")
    print()

    # 9. 演示 _make_overlay (叠加层/继承机制)
    # 这是最核心的功能: 创建一个"子配置", 用于特定的路由或请求
    print("--- 步骤 9: 演示 _make_overlay (叠加层/继承机制) ---")
    print(f"run_config_demo conf: {conf}")
    overlay_conf = conf._make_overlay()
    print(f"run_config_demo overlay_conf: {overlay_conf}")
    print(f"子配置读取父级 Port: {overlay_conf['server.port']}")
    # 修改子配置（变成非虚拟键）
    print("修改子配置的 Port...")
    overlay_conf["server.port"] = 9090
    print(f"父配置 Port (保持不变): {conf['server.port']}")
    print(f"子配置 Port (独立修改): {overlay_conf['server.port']}")
    print()

    # 10. 演示同步机制 (父变子变)
    print("--- 步骤 10: 演示同步机制 (父变子变) ---")
    print(f"run_config_demo conf: {conf}")
    print(f"run_config_demo overlay_conf: {overlay_conf}")
    conf["database.host"] = "192.168.1.1"
    conf["server.port"] = "7070"
    print(f"run_config_demo conf: {conf}")
    print(f"run_config_demo overlay_conf: {overlay_conf}")
    print()

    # 11. 演示 __delitem__ 和恢复虚拟键
    print(
        "--- 步骤 11: 演示 __delitem__ 和恢复虚拟键, 删除叠加层的修改, 恢复父级虚拟值 ---"
    )
    print(f"run_config_demo conf: {conf}")
    print(f"run_config_demo overlay_conf: {overlay_conf}")
    del overlay_conf["server.port"]
    print(f"删除子级修改后, 恢复为父级的值: {overlay_conf['server.port']}")
    print()

    # 12. 演示 meta_get 和 meta_list
    print("--- 步骤 12: 元数据操作, 演示 meta_get 和 meta_list ---")
    conf.meta_set("server.port", "help", "监听端口号")
    print(f"run_config_demo conf._meta: {conf._meta}")
    print(f"元数据获取 (help): {conf.meta_get('server.port', 'help')}")
    print(f"元数据列表: {list(conf.meta_list('server.port'))}")
    print()

    # 13. 演示 setdefault
    print("--- 步骤 13: 演示 setdefault ---")
    print(f"run_config_demo conf: {conf}")
    print(f"run_config_demo overlay_conf: {overlay_conf}")
    val = conf.setdefault("new_key", "default_val")
    print(f"run_config_demo conf: {conf}")
    print(f"run_config_demo overlay_conf: {overlay_conf}")
    print()

    # 14. 演示 _define (快速定义)
    print("--- 步骤 14: _define 快速定义 ---")
    print(f"run_config_demo conf: {conf}")
    print(f"run_config_demo overlay_conf: {overlay_conf}")
    conf._define("api.limit", default=1000, help="API 调用限制", validate=int)
    overlay_conf._define(
        "overlay.api.limit", default=2000, help="overlay API 调用限制", validate=float
    )
    print(f"run_config_demo conf: {conf}")
    print(f"run_config_demo overlay_conf: {overlay_conf}")
    print(f"run_config_demo conf._meta: {conf._meta}")
    print(f"run_config_demo overlay_conf._meta: {overlay_conf._meta}")


if __name__ == "__main__":
    run_config_demo()
