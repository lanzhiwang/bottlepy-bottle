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
        config_obj = load(name)
        obj = {
            key: getattr(config_obj, key) for key in dir(config_obj) if key.isupper()
        }

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
        options.setdefault("allow_no_value", True)
        if py3k:
            options.setdefault("interpolation", configparser.ExtendedInterpolation())
        conf = configparser.ConfigParser(**options)
        conf.read(filename)
        for section in conf.sections():
            for key in conf.options(section):
                value = conf.get(section, key)
                if section not in ("bottle", "ROOT"):
                    key = section + "." + key
                self[key.lower()] = value
        return self

    def load_dict(self, source, namespace=""):
        """Load values from a dictionary structure. Nesting can be used to
        represent namespaces.

        >>> c = ConfigDict()
        >>> c.load_dict({'some': {'namespace': {'key': 'value'} } })
        {'some.namespace.key': 'value'}
        """
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
        prefix = ""
        if a and isinstance(a[0], basestring):
            prefix = a[0].strip(".") + "."
            a = a[1:]
        for key, value in dict(*a, **ka).items():
            self[prefix + key] = value

    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value
        return self[key]

    def __setitem__(self, key, value):
        if not isinstance(key, basestring):
            raise TypeError("Key has type %r (not a string)" % type(key))

        self._virtual_keys.discard(key)

        value = self.meta_get(key, "filter", lambda x: x)(value)
        if key in self and self[key] is value:
            return

        self._on_change(key, value)
        dict.__setitem__(self, key, value)

        for overlay in self._iter_overlays():
            overlay._set_virtual(key, value)

    def __delitem__(self, key):
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
        if key not in self._virtual_keys:
            return  # Do nothing for non-virtual keys.

        if key in self:
            self._on_change(key, None)
        dict.__delitem__(self, key)
        self._virtual_keys.discard(key)
        for overlay in self._iter_overlays():
            overlay._delete_virtual(key)

    def _on_change(self, key, value):
        for cb in self._change_listener:
            if cb(self, key, value):
                return True

    def _add_change_listener(self, func):
        self._change_listener.append(func)
        return func

    def meta_get(self, key, metafield, default=None):
        """Return the value of a meta field for a key."""
        return self._meta.get(key, {}).get(metafield, default)

    def meta_set(self, key, metafield, value):
        """Set the meta field for a key to a new value.

        Meta-fields are shared between all members of an overlay tree.
        """
        self._meta.setdefault(key, {})[metafield] = value

    def meta_list(self, key):
        """Return an iterable of meta field names defined for a key."""
        return self._meta.get(key, {}).keys()

    def _define(self, key, default=_UNSET, help=_UNSET, validate=_UNSET):
        """(Unstable) Shortcut for plugins to define own config parameters."""
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
        """
        # Cleanup dead references
        self._overlays[:] = [ref for ref in self._overlays if ref() is not None]

        overlay = ConfigDict()
        overlay._meta = self._meta
        overlay._source = self
        self._overlays.append(weakref.ref(overlay))
        for key in self:
            overlay._set_virtual(key, self[key])
        return overlay
