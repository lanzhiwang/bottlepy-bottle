import time, re
import bottle
from bottle import (
    route,
    run,
    request,
    response,
    view,
    template,
    SimpleTemplate,
    hook,
    static_file,
)


print(1, "----------------" * 10)

bottle.debug(True)

print(2, "----------------" * 10)


class SomePlugin(object):
    def setup(self, app):
        app.config.meta_set("some.int", "filter", int)
        app.config.meta_set("some.list", "filter", lambda val: str(val).split(";"))
        app.config.meta_set("some.list", "help", "A semicolon separated list.")

    def apply(self, callback, route):
        pass


def stopwatch(callback):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = callback(*args, **kwargs)
        end = time.time()
        response.headers["X-Exec-Time"] = str(end - start)
        return result

    return wrapper


app = bottle.default_app()  # or bottle.Bottle() if you prefer

app.config["autojson"] = False  # Turns off the "autojson" feature
app.config["sqlite.db"] = ":memory:"  # Tells the sqlite plugin which db to use
app.config["myapp.param"] = "value"  # Example for a custom config value.
app.config["myapp.admin_user"] = "admin"

# Change many values at once
app.config.update({"autojson": False, "sqlite.db": ":memory:", "myapp.param": "value"})


# Add default values
app.config.setdefault("myapp.param2", "some default")
"""
print(app._global_config)
{}
print(app._global_config._meta)
{
    'catchall': {
        'validate': <class 'bool'>
    },
    'json.enable': {
        'help': 'Enable or disable automatic dict->json filter.',
        'validate': <class 'bool'>
    },
    'json.ascii': {
        'help': 'Use only 7-bit ASCII characters in output.',
        'validate': <class 'bool'>
    },
    'json.indent': {
        'help': 'Add whitespace to make json more readable.',
        'validate': <class 'bool'>
    },
    'json.dump_func': {
        'help': 'If defined, use this function to transform dict into json. The other options no longer apply.'
    }
}
print(app._global_config._change_listener)
[]
print(app._global_config._overlays)
[<weakref at 0x7fa24c379170; to 'ConfigDict' at 0x7fa24c332d50>]
print(app._global_config._source)
None
print(app._global_config._virtual_keys)
set()

print(app.config)
{
    'catchall': True,
    'json.enable': True,
    'json.ascii': False,
    'json.indent': True,
    'json.dump_func': None,
    'autojson': False,
    'sqlite.db': ':memory:',
    'myapp.param': 'value',
    'myapp.admin_user': 'admin',
    'myapp.param2': 'some default'
}
print(app.config._meta)
{
    'catchall': {
        'validate': <class 'bool'>
    },
    'json.enable': {
        'help': 'Enable or disable automatic dict->json filter.',
        'validate': <class 'bool'>
    },
    'json.ascii': {
        'help': 'Use only 7-bit ASCII characters in output.',
        'validate': <class 'bool'>
    },
    'json.indent': {
        'help': 'Add whitespace to make json more readable.',
        'validate': <class 'bool'>
    },
    'json.dump_func': {
        'help': 'If defined, use this function to transform dict into json. The other options no longer apply.'
    }
}
print(app.config._change_listener)
[functools.partial(<bound method Bottle.trigger_hook of <bottle.Bottle object at 0x7fa24e507920>>, 'config')]
print(app.config._overlays)
[]
print(app.config._source)
{}
print(app.config._virtual_keys)
set()
"""

# Receive values
param = app.config["myapp.param"]
param2 = app.config.get("myapp.param2", "fallback value")
print(f"param: {param}")
print(f"param2: {param2}")

# app.install(SomePlugin())
# app.install(stopwatch)
"""
print(app._global_config)
{}
print(app._global_config._meta)
{
    'catchall': {
        'validate': <class 'bool'>
    },
    'json.enable': {
        'help': 'Enable or disable automatic dict->json filter.',
        'validate': <class 'bool'>
    },
    'json.ascii': {
        'help': 'Use only 7-bit ASCII characters in output.',
        'validate': <class 'bool'>
    },
    'json.indent': {
        'help': 'Add whitespace to make json more readable.',
        'validate': <class 'bool'>
    },
    'json.dump_func': {
        'help': 'If defined, use this function to transform dict into json. The other options no longer apply.'
    },
    'some.int': {
        'filter': <class 'int'>
    },
    'some.list': {
        'filter': <function SomePlugin.setup.<locals>.<lambda> at 0x7fe73899d8a0>,
        'help': 'A semicolon separated list.'
    }
}
print(app._global_config._change_listener)
[]
print(app._global_config._overlays)
[<weakref at 0x7fe73270d030; to 'ConfigDict' at 0x7fe7326c2d50>]
print(app._global_config._source)
None
print(app._global_config._virtual_keys)
set()

print(app.config)
{'catchall': True, 'json.enable': True, 'json.ascii': False, 'json.indent': True, 'json.dump_func': None, 'autojson': False, 'sqlite.db': ':memory:', 'myapp.param': 'value', 'myapp.admin_user': 'admin', 'myapp.param2': 'some default'}
print(app.config._meta)
{
    'catchall': {
        'validate': <class 'bool'>
    },
    'json.enable': {
        'help': 'Enable or disable automatic dict->json filter.',
        'validate': <class 'bool'>
    },
    'json.ascii': {
        'help': 'Use only 7-bit ASCII characters in output.',
        'validate': <class 'bool'>
    },
    'json.indent': {
        'help': 'Add whitespace to make json more readable.',
        'validate': <class 'bool'>
    },
    'json.dump_func': {
        'help': 'If defined, use this function to transform dict into json. The other options no longer apply.'
    },
    'some.int': {
        'filter': <class 'int'>
    },
    'some.list': {
        'filter': <function SomePlugin.setup.<locals>.<lambda> at 0x7fe73899d8a0>,
        'help': 'A semicolon separated list.'
    }
}
print(app.config._change_listener)
[functools.partial(<bound method Bottle.trigger_hook of <bottle.Bottle object at 0x7fe738bdb9b0>>, 'config')]
print(app.config._overlays)
[]
print(app.config._source)
{}
print(app.config._virtual_keys)
set()
"""

app.config["some.list"] = "a;b;c"  # Actually stores ['a', 'b', 'c']
# app.config["some.int"] = "not an int"  # raises ValueError
app.config["some.int"] = "3"  # raises ValueError

print(3, "----------------" * 10)


@hook("config")
def on_config_change(key, value):
    print(f"on_config_change key: {key}")
    print(f"on_config_change value: {value}")


"""
print(app._hooks)
{'before_request': [], 'after_request': [], 'app_reset': [], 'config': [<function on_config_change at 0x7f87246977e0>]}
"""

print(4, "----------------" * 10)


def list_filter(config):
    """Matches a comma separated list of numbers."""
    delimiter = config or ","
    regexp = r"\d+(%s\d)*" % re.escape(delimiter)

    def to_python(match):
        return map(int, match.split(delimiter))

    def to_url(numbers):
        return delimiter.join(map(str, numbers))

    return regexp, to_python, to_url


app.router.add_filter("list", list_filter)


@app.route("/hello")
def hello():
    return "Hello World!"


# This example handles POST requests to '/hello_post'
@app.route("/hello_post", method="POST")
def hello_post():
    name = request.POST["name"]
    return "Hello %s!" % name


# An example route using configuration values
@app.route("/about", view="about.rst")
def about():
    email = app.config.get("my.email", "nomail@example.com")
    admin_user = request.app.config["myapp.admin_user"]
    return {"admin_user": admin_user, "email": email}


print(f"app.routes: {app.routes}")
print(f"app.router: {app.router}")
print(f"app.router.rules: {app.router.rules}")
print(f"app.router._groups: {app.router._groups}")
print(f"app.router.builder: {app.router.builder}")
print(f"app.router.static: {app.router.static}")
print(f"app.router.dyna_routes: {app.router.dyna_routes}")
print(f"app.router.dyna_regexes: {app.router.dyna_regexes}")
print(f"app.router.strict_order: {app.router.strict_order}")
print(f"app.router.filters: {app.router.filters}")


print(5, "----------------" * 10)


# tpl = SimpleTemplate("Hello {{name}}!")
# print(tpl.render(name="World"))

# print(template("Hello {{name}}!", name="World"))

# my_dict = {"number": "123", "street": "Fake St.", "city": "Fakeville"}
# print(template("I live at {{number}} {{street}}, {{city}}", **my_dict))


# @route("/hello")
# @route("/hello/<name>")
# @view("hello_template")
# def hello(name="World"):
#     return dict(name=name)


print(6, "----------------" * 10)


run(host="localhost", port=8080)

print(7, "----------------" * 10)
