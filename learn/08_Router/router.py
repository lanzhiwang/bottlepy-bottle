import re, warnings
from urllib.parse import urlencode

DEBUG = True


def depr(major, minor, cause, fix, stacklevel=3):
    text = (
        "Warning: Use of deprecated feature or API. (Deprecated in Bottle-%d.%d)\n"
        "Cause: %s\n"
        "Fix: %s\n" % (major, minor, cause, fix)
    )
    if DEBUG == "strict":
        raise DeprecationWarning(text)
    warnings.warn(text, DeprecationWarning, stacklevel=stacklevel)
    return DeprecationWarning(text)


def _re_flatten(p):
    """Turn all capturing groups in a regular expression pattern into
    non-capturing groups."""
    if "(" not in p:
        return p
    return re.sub(
        r"(\\*)(\(\?P<[^>]+>|\((?!\?))",
        lambda m: m.group(0) if len(m.group(1)) % 2 else m.group(1) + "(?:",
        p,
    )


class BottleException(Exception):
    """A base class for exceptions used by bottle."""

    pass


class RouteError(BottleException):
    """This is a base class for all routing related exceptions"""


class RouteSyntaxError(RouteError):
    """The route parser found something not supported by this router."""


class Router(object):
    """A Router is an ordered collection of route->target pairs. It is used to
    efficiently match WSGI requests against a number of routes and return
    the first target that satisfies the request. The target may be anything,
    usually a string, ID or callable object. A route consists of a path-rule
    and a HTTP method.

    The path-rule is either a static path (e.g. `/contact`) or a dynamic
    path that contains wildcards (e.g. `/wiki/<page>`). The wildcard syntax
    and details on the matching order are described in docs:`routing`.
    """

    default_pattern = "[^/]+"
    default_filter = "re"

    #: The current CPython regexp implementation does not allow more
    #: than 99 matching groups per regular expression.
    _MAX_GROUPS_PER_PATTERN = 99

    def __init__(self, strict=False):
        self.rules = []  # All rules in order
        self._groups = {}  # index of regexes to find them in dyna_routes
        self.builder = {}  # Data structure for the url builder
        self.static = {}  # Search structure for static routes
        self.dyna_routes = {}
        self.dyna_regexes = {}  # Search structure for dynamic routes
        #: If true, static routes are no longer checked first.
        self.strict_order = strict
        self.filters = {
            "re": lambda conf: (_re_flatten(conf or self.default_pattern), None, None),
            "int": lambda conf: (r"-?\d+", int, lambda x: str(int(x))),
            "float": lambda conf: (r"-?[\d.]+", float, lambda x: str(float(x))),
            "path": lambda conf: (r".+?", None, None),
        }

    def add_filter(self, name, func):
        """Add a filter. The provided function is called with the configuration
        string as parameter and must return a (regexp, to_python, to_url) tuple.
        The first element is a string, the last two are callables or None."""
        self.filters[name] = func

    rule_syntax = re.compile(
        "(\\\\*)"
        "(?:(?::([a-zA-Z_][a-zA-Z_0-9]*)?()(?:#(.*?)#)?)"
        "|(?:<([a-zA-Z_][a-zA-Z_0-9]*)?(?::([a-zA-Z_]*)"
        "(?::((?:\\\\.|[^\\\\>])+)?)?)?>))"
    )

    def _itertokens(self, rule):
        print(f"Router _itertokens rule: {rule}")

        offset, prefix = 0, ""
        for match in self.rule_syntax.finditer(rule):
            print(f"Router _itertokens 动态路由")
            print(f"Router _itertokens match: {match}")

            print(f"Router _itertokens match.start(): {match.start()}")
            print(f"Router _itertokens match.groups(): {match.groups()}")
            prefix += rule[offset : match.start()]
            g = match.groups()
            print(f"Router _itertokens prefix: {prefix}")
            print(f"Router _itertokens g: {g}")

            if g[2] is not None:
                depr(
                    0,
                    13,
                    "Use of old route syntax.",
                    "Use <name> instead of :name in routes.",
                    stacklevel=4,
                )

            if len(g[0]) % 2:  # Escaped wildcard
                prefix += match.group(0)[len(g[0]) :]
                offset = match.end()
                continue
            if prefix:
                yield prefix, None, None
            name, filtr, conf = g[4:7] if g[2] is None else g[1:4]
            yield name, filtr or "default", conf or None
            offset, prefix = match.end(), ""

        if offset <= len(rule) or prefix:
            yield prefix + rule[offset:], None, None

    def add(self, rule, method, target, name=None):
        """Add a new rule or replace the target for an existing rule."""

        print(f"Router add rule: {rule}")
        print(f"Router add method: {method}")
        print(f"Router add target: {target}")
        print(f"Router add name: {name}")

        anons = 0  # Number of anonymous wildcards found
        keys = []  # Names of keys
        pattern = ""  # Regular expression pattern with named groups
        filters = []  # Lists of wildcard input filters
        builder = []  # Data structure for the URL builder
        is_static = True

        for key, mode, conf in self._itertokens(rule):
            print(f"Router add key: {key}")
            print(f"Router add mode: {mode}")
            print(f"Router add conf: {conf}")

            """
            如果 mode 是 None, 说明匹配的是 url 中的静态部分
            如果 mode 不是 None, 说明匹配的是 url 中的动态部分, 也就是 filtr
            """

            if mode:
                is_static = False
                if mode == "default":
                    mode = self.default_filter
                mask, in_filter, out_filter = self.filters[mode](conf)
                if not key:
                    pattern += "(?:%s)" % mask
                    key = "anon%d" % anons
                    anons += 1
                else:
                    pattern += "(?P<%s>%s)" % (key, mask)
                    keys.append(key)
                if in_filter:
                    filters.append((key, in_filter))
                builder.append((key, out_filter or str))
            elif key:
                pattern += re.escape(key)
                builder.append((None, key))
            print(f"Router add pattern: {pattern}")
            print(f"Router add builder: {builder}")

        self.builder[rule] = builder
        if name:
            self.builder[name] = builder
        print(f"Router add self.builder: {self.builder}")

        if is_static and not self.strict_order:
            self.static.setdefault(method, {})
            self.static[method][self.build(rule)] = (target, None)
            print(f"Router add self.static: {self.static}")
            return

        try:
            re_pattern = re.compile("^(%s)$" % pattern)
            re_match = re_pattern.match
        except re.error as e:
            raise RouteSyntaxError("Could not add Route: %s (%s)" % (rule, e))

        if filters:

            def getargs(path):
                url_args = re_match(path).groupdict()
                for name, wildcard_filter in filters:
                    try:
                        url_args[name] = wildcard_filter(url_args[name])
                    except ValueError:
                        raise HTTPError(400, "Path has wrong format.")
                return url_args

        elif re_pattern.groupindex:

            def getargs(path):
                return re_match(path).groupdict()

        else:
            getargs = None

        flatpat = _re_flatten(pattern)
        whole_rule = (rule, flatpat, target, getargs)

        if (flatpat, method) in self._groups:
            if DEBUG:
                msg = "Route <%s %s> overwrites a previously defined route"
                warnings.warn(msg % (method, rule), RuntimeWarning, stacklevel=3)
            self.dyna_routes[method][self._groups[flatpat, method]] = whole_rule
        else:
            self.dyna_routes.setdefault(method, []).append(whole_rule)
            self._groups[flatpat, method] = len(self.dyna_routes[method]) - 1

        self._compile(method)

    def _compile(self, method):
        all_rules = self.dyna_routes[method]
        comborules = self.dyna_regexes[method] = []
        maxgroups = self._MAX_GROUPS_PER_PATTERN
        for x in range(0, len(all_rules), maxgroups):
            some = all_rules[x : x + maxgroups]
            combined = (flatpat for (_, flatpat, _, _) in some)
            combined = "|".join("(^%s$)" % flatpat for flatpat in combined)
            combined = re.compile(combined).match
            rules = [(target, getargs) for (_, _, target, getargs) in some]
            comborules.append((combined, rules))

    def build(self, _name, *anons, **query):
        """Build an URL by filling the wildcards in a rule."""

        print(f"Router build _name: {_name}")
        print(f"Router build anons: {anons}")
        print(f"Router build query: {query}")

        print(f"Router build self.builder: {self.builder}")
        builder = self.builder.get(_name)
        print(f"Router build builder: {builder}")

        if not builder:
            raise RouteBuildError("No route with that name.", _name)
        try:
            for i, value in enumerate(anons):
                query["anon%d" % i] = value
            url = "".join([f(query.pop(n)) if n else f for (n, f) in builder])
            return url if not query else url + "?" + urlencode(query)
        except KeyError as E:
            raise RouteBuildError("Missing URL argument: %r" % E.args[0])

    def match(self, environ):
        """Return a (target, url_args) tuple or raise HTTPError(400/404/405)."""
        verb = environ["REQUEST_METHOD"].upper()
        path = environ["PATH_INFO"] or "/"

        methods = (
            ("PROXY", "HEAD", "GET", "ANY")
            if verb == "HEAD"
            else ("PROXY", verb, "ANY")
        )

        for method in methods:
            if method in self.static and path in self.static[method]:
                target, getargs = self.static[method][path]
                return target, getargs(path) if getargs else {}
            elif method in self.dyna_regexes:
                for combined, rules in self.dyna_regexes[method]:
                    match = combined(path)
                    if match:
                        target, getargs = rules[match.lastindex - 1]
                        return target, getargs(path) if getargs else {}

        # No matching route found. Collect alternative methods for 405 response
        allowed = set([])
        nocheck = set(methods)
        for method in set(self.static) - nocheck:
            if path in self.static[method]:
                allowed.add(method)
        for method in set(self.dyna_regexes) - allowed - nocheck:
            for combined, rules in self.dyna_regexes[method]:
                match = combined(path)
                if match:
                    allowed.add(method)
        if allowed:
            allow_header = ",".join(sorted(allowed))
            raise HTTPError(405, "Method not allowed.", Allow=allow_header)

        # No matching route and no alternative method found. We give up
        raise HTTPError(404, "Not found: " + repr(path))


if __name__ == "__main__":
    r = Router()
    # add(self, rule, method, target, name=None):
    rules = [
        "/",
        "/hello",
        "/hello/<name>",
        "/<action>/<user>",
        "/object/<id:int>",
        "/show/<name:re:[a-z]+>",
        "/static/<path:path>",
    ]
    methods = ["GET", "POST", "PUT", "GET", "POST", "PUT", "GET"]
    name = None
    for i in range(len(rules)):
        r.add(rules[i], methods[i], "target", f"name_{i}")
        print("-----" * 10)
