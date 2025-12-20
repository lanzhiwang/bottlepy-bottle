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

    print("./bottle.py load target1:", target)
    print("./bottle.py load namespace:", namespace)
    # ./bottle.py load target1: example_settings
    # ./bottle.py load namespace: {}

    module, target = target.split(":", 1) if ":" in target else (target, None)
    print("./bottle.py load module:", module)
    print("./bottle.py load target2:", target)
    # ./bottle.py load module: example_settings
    # ./bottle.py load target2: None

    # print("./bottle.py load sys.modules:", sys.modules)
    """
    ./bottle.py load sys.modules:
    {
        'sys': <module 'sys' (built-in)>,
        'builtins': <module 'builtins' (built-in)>,
        '_frozen_importlib': <module '_frozen_importlib' (frozen)>,
        '_imp': <module '_imp' (built-in)>,
        '_thread': <module '_thread' (built-in)>,
        '_warnings': <module '_warnings' (built-in)>,
        '_weakref': <module '_weakref' (built-in)>,
        '_io': <module '_io' (built-in)>,
        'marshal': <module 'marshal' (built-in)>,
        'posix': <module 'posix' (built-in)>,
        '_frozen_importlib_external': <module '_frozen_importlib_external' (frozen)>,
        'time': <module 'time' (built-in)>,
        'zipimport': <module 'zipimport' (frozen)>,
        '_codecs': <module '_codecs' (built-in)>,
        'codecs': <module 'codecs' (frozen)>,
        'encodings.aliases': <module 'encodings.aliases' from '/usr/local/lib/python3.12/encodings/aliases.py'>,
        'encodings': <module 'encodings' from '/usr/local/lib/python3.12/encodings/__init__.py'>,
        'encodings.utf_8': <module 'encodings.utf_8' from '/usr/local/lib/python3.12/encodings/utf_8.py'>,
        '_signal': <module '_signal' (built-in)>,
        '_abc': <module '_abc' (built-in)>,
        'abc': <module 'abc' (frozen)>,
        'io': <module 'io' (frozen)>,
        '__main__': <module 'unittest.__main__' from '/usr/local/lib/python3.12/unittest/__main__.py'>,
        '_stat': <module '_stat' (built-in)>,
        'stat': <module 'stat' (frozen)>,
        '_collections_abc': <module '_collections_abc' (frozen)>,
        'genericpath': <module 'genericpath' (frozen)>,
        'posixpath': <module 'posixpath' (frozen)>,
        'os.path': <module 'posixpath' (frozen)>,
        'os': <module 'os' (frozen)>,
        '_sitebuiltins': <module '_sitebuiltins' (frozen)>,
        '_distutils_hack': <module '_distutils_hack' from '/usr/local/lib/python3.12/site-packages/_distutils_hack/__init__.py'>,
        'site': <module 'site' (frozen)>,
        'importlib._bootstrap': <module '_frozen_importlib' (frozen)>,
        'importlib._bootstrap_external': <module '_frozen_importlib_external' (frozen)>,
        'warnings': <module 'warnings' from '/usr/local/lib/python3.12/warnings.py'>,
        'importlib': <module 'importlib' from '/usr/local/lib/python3.12/importlib/__init__.py'>,
        'importlib.machinery': <module 'importlib.machinery' (frozen)>,
        'importlib._abc': <module 'importlib._abc' from '/usr/local/lib/python3.12/importlib/_abc.py'>,
        'types': <module 'types' from '/usr/local/lib/python3.12/types.py'>,
        'importlib.util': <module 'importlib.util' (frozen)>,
        'runpy': <module 'runpy' (frozen)>,
        'itertools': <module 'itertools' (built-in)>,
        'keyword': <module 'keyword' from '/usr/local/lib/python3.12/keyword.py'>,
        '_operator': <module '_operator' (built-in)>,
        'operator': <module 'operator' from '/usr/local/lib/python3.12/operator.py'>,
        'reprlib': <module 'reprlib' from '/usr/local/lib/python3.12/reprlib.py'>,
        '_collections': <module '_collections' (built-in)>,
        'collections': <module 'collections' from '/usr/local/lib/python3.12/collections/__init__.py'>,
        'collections.abc': <module 'collections.abc' from '/usr/local/lib/python3.12/collections/abc.py'>,
        '_functools': <module '_functools' (built-in)>,
        'functools': <module 'functools' from '/usr/local/lib/python3.12/functools.py'>,
        'enum': <module 'enum' from '/usr/local/lib/python3.12/enum.py'>,
        '_sre': <module '_sre' (built-in)>,
        're._constants': <module 're._constants' from '/usr/local/lib/python3.12/re/_constants.py'>,
        're._parser': <module 're._parser' from '/usr/local/lib/python3.12/re/_parser.py'>,
        're._casefix': <module 're._casefix' from '/usr/local/lib/python3.12/re/_casefix.py'>,
        're._compiler': <module 're._compiler' from '/usr/local/lib/python3.12/re/_compiler.py'>,
        'copyreg': <module 'copyreg' from '/usr/local/lib/python3.12/copyreg.py'>,
        're': <module 're' from '/usr/local/lib/python3.12/re/__init__.py'>,
        'token': <module 'token' from '/usr/local/lib/python3.12/token.py'>,
        '_tokenize': <module '_tokenize' (built-in)>,
        'tokenize': <module 'tokenize' from '/usr/local/lib/python3.12/tokenize.py'>,
        'linecache': <module 'linecache' from '/usr/local/lib/python3.12/linecache.py'>,
        'textwrap': <module 'textwrap' from '/usr/local/lib/python3.12/textwrap.py'>,
        'contextlib': <module 'contextlib' from '/usr/local/lib/python3.12/contextlib.py'>,
        'traceback': <module 'traceback' from '/usr/local/lib/python3.12/traceback.py'>,
        'unittest.util': <module 'unittest.util' from '/usr/local/lib/python3.12/unittest/util.py'>,
        'unittest.result': <module 'unittest.result' from '/usr/local/lib/python3.12/unittest/result.py'>,
        '_heapq': <module '_heapq' from '/usr/local/lib/python3.12/lib-dynload/_heapq.cpython-312-x86_64-linux-gnu.so'>,
        'heapq': <module 'heapq' from '/usr/local/lib/python3.12/heapq.py'>,
        'difflib': <module 'difflib' from '/usr/local/lib/python3.12/difflib.py'>,
        '_weakrefset': <module '_weakrefset' from '/usr/local/lib/python3.12/_weakrefset.py'>,
        'weakref': <module 'weakref' from '/usr/local/lib/python3.12/weakref.py'>,
        'copy': <module 'copy' from '/usr/local/lib/python3.12/copy.py'>,
        '_ast': <module '_ast' (built-in)>,
        'ast': <module 'ast' from '/usr/local/lib/python3.12/ast.py'>,
        '_opcode': <module '_opcode' from '/usr/local/lib/python3.12/lib-dynload/_opcode.cpython-312-x86_64-linux-gnu.so'>,
        'opcode': <module 'opcode' from '/usr/local/lib/python3.12/opcode.py'>,
        'dis': <module 'dis' from '/usr/local/lib/python3.12/dis.py'>,
        'inspect': <module 'inspect' from '/usr/local/lib/python3.12/inspect.py'>,
        'dataclasses': <module 'dataclasses' from '/usr/local/lib/python3.12/dataclasses.py'>,
        'pprint': <module 'pprint' from '/usr/local/lib/python3.12/pprint.py'>,
        'unittest.case': <module 'unittest.case' from '/usr/local/lib/python3.12/unittest/case.py'>,
        'unittest.suite': <module 'unittest.suite' from '/usr/local/lib/python3.12/unittest/suite.py'>,
        'fnmatch': <module 'fnmatch' from '/usr/local/lib/python3.12/fnmatch.py'>,
        'unittest.loader': <module 'unittest.loader' from '/usr/local/lib/python3.12/unittest/loader.py'>,
        'gettext': <module 'gettext' from '/usr/local/lib/python3.12/gettext.py'>,
        'argparse': <module 'argparse' from '/usr/local/lib/python3.12/argparse.py'>,
        'signal': <module 'signal' from '/usr/local/lib/python3.12/signal.py'>,
        'unittest.signals': <module 'unittest.signals' from '/usr/local/lib/python3.12/unittest/signals.py'>,
        'unittest.runner': <module 'unittest.runner' from '/usr/local/lib/python3.12/unittest/runner.py'>,
        'unittest.main': <module 'unittest.main' from '/usr/local/lib/python3.12/unittest/main.py'>,
        'unittest': <module 'unittest' from '/usr/local/lib/python3.12/unittest/__init__.py'>,
        '_locale': <module '_locale' (built-in)>,
        'locale': <module 'locale' from '/usr/local/lib/python3.12/locale.py'>,
        'errno': <module 'errno' (built-in)>,
        'zlib': <module 'zlib' from '/usr/local/lib/python3.12/lib-dynload/zlib.cpython-312-x86_64-linux-gnu.so'>,
        '_compression': <module '_compression' from '/usr/local/lib/python3.12/_compression.py'>,
        '_bz2': <module '_bz2' from '/usr/local/lib/python3.12/lib-dynload/_bz2.cpython-312-x86_64-linux-gnu.so'>,
        'bz2': <module 'bz2' from '/usr/local/lib/python3.12/bz2.py'>,
        '_lzma': <module '_lzma' from '/usr/local/lib/python3.12/lib-dynload/_lzma.cpython-312-x86_64-linux-gnu.so'>,
        'lzma': <module 'lzma' from '/usr/local/lib/python3.12/lzma.py'>,
        'shutil': <module 'shutil' from '/usr/local/lib/python3.12/shutil.py'>,
        'math': <module 'math' from '/usr/local/lib/python3.12/lib-dynload/math.cpython-312-x86_64-linux-gnu.so'>,
        '_bisect': <module '_bisect' from '/usr/local/lib/python3.12/lib-dynload/_bisect.cpython-312-x86_64-linux-gnu.so'>,
        'bisect': <module 'bisect' from '/usr/local/lib/python3.12/bisect.py'>,
        '_random': <module '_random' from '/usr/local/lib/python3.12/lib-dynload/_random.cpython-312-x86_64-linux-gnu.so'>,
        '_sha2': <module '_sha2' from '/usr/local/lib/python3.12/lib-dynload/_sha2.cpython-312-x86_64-linux-gnu.so'>,
        'random': <module 'random' from '/usr/local/lib/python3.12/random.py'>,
        'tempfile': <module 'tempfile' from '/usr/local/lib/python3.12/tempfile.py'>,
        'configparser': <module 'configparser' from '/usr/local/lib/python3.12/configparser.py'>,
        'configdict': <module 'configdict' from '/bottle/learn/configdict/configdict.py'>,
        'test_config': <module 'test_config' from '/bottle/learn/configdict/test_config.py'>
    }
    """

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
    """

    __slots__ = (
        "_meta",
        "_change_listener",
        "_overlays",
        "_virtual_keys",
        "_source",
        "__weakref__",
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

        :param name: Module name to import and load.
        :param squash: If true (default), nested dicts are assumed to
           represent namespaces and flattened (see :meth:`load_dict`).
        """

        print("./bottle.py ConfigDict load_module name:", name)
        print("./bottle.py ConfigDict load_module squash:", squash)
        # ./bottle.py ConfigDict load_module name: example_settings
        # ./bottle.py ConfigDict load_module squash: True

        config_obj = load(name)
        print("./bottle.py ConfigDict load_module config_obj:", config_obj)
        # ./bottle.py ConfigDict load_module config_obj: <module 'example_settings' from '/bottle/learn/configdict/example_settings.py'>

        obj = {
            key: getattr(config_obj, key) for key in dir(config_obj) if key.isupper()
        }
        print("./bottle.py ConfigDict load_module obj:", obj)
        # ./bottle.py ConfigDict load_module obj: {'A': {'B': {'C': 3}}}

        if squash:
            self.load_dict(obj)
        else:
            self.update(obj)
        return self

    def load_config(self, filename, **options):
        """Load values from ``*.ini`` style config files using configparser.

        INI style sections (e.g. ``[section]``) are used as namespace for
        all keys within that section. Both section and key names may contain
        dots as namespace separators and are converted to lower-case.

        The special sections ``[bottle]`` and ``[ROOT]`` refer to the root
        namespace and the ``[DEFAULT]`` section defines default values for all
        other sections.

        :param filename: The path of a config file, or a list of paths.
        :param options: All keyword parameters are passed to the underlying
            :class:`python:configparser.ConfigParser` constructor call.

        """

        print("./bottle.py ConfigDict load_config filename:", filename)
        print("./bottle.py ConfigDict load_config options:", options)
        # ./bottle.py ConfigDict load_config filename: /tmp/tmpjzqym6s0.example.ini
        # ./bottle.py ConfigDict load_config options: {}

        options.setdefault("allow_no_value", True)
        if py3k:
            options.setdefault("interpolation", configparser.ExtendedInterpolation())
        print("./bottle.py ConfigDict load_config options:", options)
        # ./bottle.py ConfigDict load_config options: {'allow_no_value': True, 'interpolation': <configparser.ExtendedInterpolation object at 0x7f765ddefb60>}

        conf = configparser.ConfigParser(**options)
        print("./bottle.py ConfigDict load_config conf:", conf)
        # ./bottle.py ConfigDict load_config conf: <configparser.ConfigParser object at 0x7f765ddef680>
        conf.read(filename)
        print("./bottle.py ConfigDict load_config conf:", conf)
        # ./bottle.py ConfigDict load_config conf: <configparser.ConfigParser object at 0x7f765ddef680>

        for section in conf.sections():
            print("./bottle.py ConfigDict load_config section:", section)
            # ./bottle.py ConfigDict load_config section: bottle
            # ./bottle.py ConfigDict load_config section: ROOT
            # ./bottle.py ConfigDict load_config section: NameSpace.Section
            # ./bottle.py ConfigDict load_config section: compression

            for key in conf.options(section):
                print("./bottle.py ConfigDict load_config key:", key)
                # ./bottle.py ConfigDict load_config key: port
                # ./bottle.py ConfigDict load_config key: default
                # ./bottle.py ConfigDict load_config key: namespace.key
                # ./bottle.py ConfigDict load_config key: default
                # ./bottle.py ConfigDict load_config key: sub.namespace.key
                # ./bottle.py ConfigDict load_config key: default
                # ./bottle.py ConfigDict load_config key: status
                # ./bottle.py ConfigDict load_config key: default

                value = conf.get(section, key)
                print("./bottle.py ConfigDict load_config value:", value)
                # ./bottle.py ConfigDict load_config value: 8080
                # ./bottle.py ConfigDict load_config value: 45
                # ./bottle.py ConfigDict load_config value: test
                # ./bottle.py ConfigDict load_config value: 45
                # ./bottle.py ConfigDict load_config value: test2
                # ./bottle.py ConfigDict load_config value: otherDefault
                # ./bottle.py ConfigDict load_config value: single
                # ./bottle.py ConfigDict load_config value: 45

                if section not in ("bottle", "ROOT"):
                    key = section + "." + key
                print("./bottle.py ConfigDict load_config key:", key)
                # ./bottle.py ConfigDict load_config key: port
                # ./bottle.py ConfigDict load_config key: default
                # ./bottle.py ConfigDict load_config key: namespace.key
                # ./bottle.py ConfigDict load_config key: default
                # ./bottle.py ConfigDict load_config key: NameSpace.Section.sub.namespace.key
                # ./bottle.py ConfigDict load_config key: NameSpace.Section.default
                # ./bottle.py ConfigDict load_config key: compression.status
                # ./bottle.py ConfigDict load_config key: compression.default

                self[key.lower()] = value
        return self

    def load_dict(self, source, namespace=""):
        """Load values from a dictionary structure. Nesting can be used to
        represent namespaces.

        >>> c = ConfigDict()
        >>> c.load_dict({'some': {'namespace': {'key': 'value'} } })
        {'some.namespace.key': 'value'}
        """

        print("./bottle.py ConfigDict load_dict source:", source)
        print("./bottle.py ConfigDict load_dict namespace:", namespace)
        # ./bottle.py ConfigDict load_dict source: {'A': {'B': {'C': 3}}}
        # ./bottle.py ConfigDict load_dict namespace:
        # ./bottle.py ConfigDict load_dict source: {'B': {'C': 3}}
        # ./bottle.py ConfigDict load_dict namespace: A
        # ./bottle.py ConfigDict load_dict source: {'C': 3}
        # ./bottle.py ConfigDict load_dict namespace: A.B

        for key, value in source.items():
            if isinstance(key, basestring):
                nskey = (namespace + "." + key).strip(".")
                if isinstance(value, dict):
                    self.load_dict(value, namespace=nskey)
                else:
                    self[nskey] = value
            else:
                raise TypeError("Key has type %r (not a string)" % type(key))
        return self

    def update(self, *a, **ka):
        """If the first parameter is a string, all keys are prefixed with this
        namespace. Apart from that it works just as the usual dict.update().

        >>> c = ConfigDict()
        >>> c.update('some.namespace', key='value')
        """

        print("./bottle.py ConfigDict update a:", a)
        print("./bottle.py ConfigDict update ka:", ka)
        # ./bottle.py ConfigDict update a: ({'A': {'B': {'C': 3}}},)
        # ./bottle.py ConfigDict update ka: {}

        prefix = ""
        if a and isinstance(a[0], basestring):
            prefix = a[0].strip(".") + "."
            a = a[1:]

        print("./bottle.py ConfigDict update a:", a)
        print("./bottle.py ConfigDict update prefix:", prefix)
        # ./bottle.py ConfigDict update a: ({'A': {'B': {'C': 3}}},)
        # ./bottle.py ConfigDict update prefix:

        print("./bottle.py ConfigDict update dict(*a, **ka):", dict(*a, **ka))
        # ./bottle.py ConfigDict update dict(*a, **ka): {'A': {'B': {'C': 3}}}

        for key, value in dict(*a, **ka).items():
            self[prefix + key] = value

    def setdefault(self, key, value=None):
        print("./bottle.py ConfigDict setdefault key:", key)
        print("./bottle.py ConfigDict setdefault value:", value)
        # ./bottle.py ConfigDict setdefault key: key
        # ./bottle.py ConfigDict setdefault value: Val2

        if key not in self:
            self[key] = value
        return self[key]

    def __setitem__(self, key, value):
        print("./bottle.py ConfigDict __setitem__ key:", key)
        print("./bottle.py ConfigDict __setitem__ value:", value)
        # ./bottle.py ConfigDict __setitem__ key: port
        # ./bottle.py ConfigDict __setitem__ value: 8080

        if not isinstance(key, basestring):
            raise TypeError("Key has type %r (not a string)" % type(key))

        self._virtual_keys.discard(key)
        print(
            "./bottle.py ConfigDict __setitem__ self._virtual_keys:", self._virtual_keys
        )
        # ./bottle.py ConfigDict __setitem__ self._virtual_keys: set()

        value = self.meta_get(key, "filter", lambda x: x)(value)
        if key in self and self[key] is value:
            return

        self._on_change(key, value)
        dict.__setitem__(self, key, value)

        for overlay in self._iter_overlays():
            overlay._set_virtual(key, value)

    def __delitem__(self, key):
        print("./bottle.py ConfigDict __delitem__ key:", key)
        # ./bottle.py ConfigDict __delitem__ key: No key

        if key not in self:
            raise KeyError(key)
        if key in self._virtual_keys:
            raise KeyError("Virtual keys cannot be deleted: %s" % key)

        if self._source and key in self._source:
            # Not virtual, but present in source -> Restore virtual value
            dict.__delitem__(self, key)
            self._set_virtual(key, self._source[key])
        else:  # not virtual, not present in source. This is OUR value
            self._on_change(key, None)
            dict.__delitem__(self, key)
            for overlay in self._iter_overlays():
                overlay._delete_virtual(key)

    def _set_virtual(self, key, value):
        """Recursively set or update virtual keys."""

        print("./bottle.py ConfigDict _set_virtual key:", key)
        print("./bottle.py ConfigDict _set_virtual value:", value)
        # ./bottle.py ConfigDict _set_virtual key: key
        # ./bottle.py ConfigDict _set_virtual value: source

        print("./bottle.py ConfigDict _set_virtual self:", self)

        if key in self and key not in self._virtual_keys:
            return  # Do nothing for non-virtual keys.

        self._virtual_keys.add(key)
        if key in self and self[key] is not value:
            self._on_change(key, value)
        dict.__setitem__(self, key, value)
        for overlay in self._iter_overlays():
            overlay._set_virtual(key, value)

    def _delete_virtual(self, key):
        """Recursively delete virtual entry."""

        print("./bottle.py ConfigDict _delete_virtual key:", key)

        if key not in self._virtual_keys:
            return  # Do nothing for non-virtual keys.

        if key in self:
            self._on_change(key, None)
        dict.__delitem__(self, key)
        self._virtual_keys.discard(key)
        for overlay in self._iter_overlays():
            overlay._delete_virtual(key)

    def _on_change(self, key, value):
        print("./bottle.py ConfigDict _on_change key:", key)
        print("./bottle.py ConfigDict _on_change value:", value)
        # ./bottle.py ConfigDict _on_change key: port
        # ./bottle.py ConfigDict _on_change value: 8080

        print(
            "./bottle.py ConfigDict _on_change self._change_listener:",
            self._change_listener,
        )
        # ./bottle.py ConfigDict _on_change self._change_listener: []

        for cb in self._change_listener:
            if cb(self, key, value):
                return True

    def _add_change_listener(self, func):
        print("./bottle.py ConfigDict _add_change_listener func:", func)

        self._change_listener.append(func)
        return func

    def meta_get(self, key, metafield, default=None):
        """Return the value of a meta field for a key."""

        print("./bottle.py ConfigDict meta_get key:", key)
        print("./bottle.py ConfigDict meta_get metafield:", metafield)
        print("./bottle.py ConfigDict meta_get default:", default)
        # ./bottle.py ConfigDict meta_get key: port
        # ./bottle.py ConfigDict meta_get metafield: filter
        # ./bottle.py ConfigDict meta_get default: <function ConfigDict.__setitem__.<locals>.<lambda> at 0x7f3e75cf0540>

        return self._meta.get(key, {}).get(metafield, default)

    def meta_set(self, key, metafield, value):
        """Set the meta field for a key to a new value.

        Meta-fields are shared between all members of an overlay tree.
        """

        print("./bottle.py ConfigDict meta_set key:", key)
        print("./bottle.py ConfigDict meta_set metafield:", metafield)
        print("./bottle.py ConfigDict meta_set value:", value)
        # ./bottle.py ConfigDict meta_set key: bool
        # ./bottle.py ConfigDict meta_set metafield: filter
        # ./bottle.py ConfigDict meta_set value: <class 'bool'>
        # ./bottle.py ConfigDict meta_set key: int
        # ./bottle.py ConfigDict meta_set metafield: filter
        # ./bottle.py ConfigDict meta_set value: <class 'int'>

        self._meta.setdefault(key, {})[metafield] = value
        print("./bottle.py ConfigDict meta_set self._meta:", self._meta)
        # ./bottle.py ConfigDict meta_set self._meta:
        # {
        #     'bool': {'filter': <class 'bool'>}
        # }
        # ./bottle.py ConfigDict meta_set self._meta:
        # {
        #     'bool': {'filter': <class 'bool'>},
        #     'int': {'filter': <class 'int'>}
        # }

    def meta_list(self, key):
        """Return an iterable of meta field names defined for a key."""

        print("./bottle.py ConfigDict meta_list key:", key)

        return self._meta.get(key, {}).keys()

    def _define(self, key, default=_UNSET, help=_UNSET, validate=_UNSET):
        """(Unstable) Shortcut for plugins to define own config parameters."""

        print("./bottle.py ConfigDict _define key:", key)
        print("./bottle.py ConfigDict _define default:", default)
        print("./bottle.py ConfigDict _define help:", help)
        print("./bottle.py ConfigDict _define validate:", validate)

        if default is not _UNSET:
            self.setdefault(key, default)
        if help is not _UNSET:
            self.meta_set(key, "help", help)
        if validate is not _UNSET:
            self.meta_set(key, "validate", validate)

    def _iter_overlays(self):
        print("./bottle.py ConfigDict _iter_overlays self._overlays:", self._overlays)
        # ./bottle.py ConfigDict _iter_overlays self._overlays: []

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
        """
        # Cleanup dead references
        print("./bottle.py ConfigDict _make_overlay self._overlays1:", self._overlays)
        # ./bottle.py ConfigDict _make_overlay self._overlays1: []

        self._overlays[:] = [ref for ref in self._overlays if ref() is not None]
        print("./bottle.py ConfigDict _make_overlay self._overlays2:", self._overlays)
        # ./bottle.py ConfigDict _make_overlay self._overlays2: []

        """
        overlay               source(self)
            _meta                 _meta
            _source               _overlays
        """
        overlay = ConfigDict()
        overlay._meta = self._meta
        overlay._source = self
        self._overlays.append(weakref.ref(overlay))
        print("./bottle.py ConfigDict _make_overlay self._overlays3:", self._overlays)
        for key in self:
            overlay._set_virtual(key, self[key])
        return overlay
