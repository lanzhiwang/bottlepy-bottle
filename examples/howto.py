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

app.install(SomePlugin())
app.install(stopwatch)


app.config["autojson"] = False  # Turns off the "autojson" feature
app.config["sqlite.db"] = ":memory:"  # Tells the sqlite plugin which db to use
app.config["myapp.param"] = "value"  # Example for a custom config value.
app.config["myapp.admin_user"] = "admin"

# Change many values at once
app.config.update({"autojson": False, "sqlite.db": ":memory:", "myapp.param": "value"})

app.config["some.list"] = "a;b;c"  # Actually stores ['a', 'b', 'c']
# app.config["some.int"] = "not an int"  # raises ValueError
app.config["some.int"] = "3"  # raises ValueError

# Add default values
app.config.setdefault("myapp.param2", "some default")

# Receive values
param = app.config["myapp.param"]
param2 = app.config.get("myapp.param2", "fallback value")


# An example route using configuration values
@app.route("/about", view="about.rst")
def about():
    email = app.config.get("my.email", "nomail@example.com")
    admin_user = request.app.config["myapp.admin_user"]
    return {"admin_user": admin_user, "email": email}


@hook("config")
def on_config_change(key, value):
    print(f"on_config_change key: {key}")
    print(f"on_config_change value: {value}")


print(3, "----------------" * 10)


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


@app.route("/follow/<ids:list>")
def follow_users(ids):
    return ids


# Lets start with "Hello World!"
# Point your Browser to 'http://localhost:8080/' and greet the world :D
@route("/")
def hello_world():
    return "Hello World!"


@route("/hello")
def hello():
    return "Hello World!"


@route("/")
@route("/hello/<name>")
def greet(name="Stranger"):
    return template("Hello {{name}}, how are you?", name=name)


@route("/wiki/<pagename>")  # matches /wiki/Learning_Python
def show_wiki_page(pagename):
    return pagename


@route("/<action>/<user>")  # matches /follow/defnull
def user_api(action, user):
    return {"action": action, "user": user}


@route("/object/<id:int>")
def callback(id):
    assert isinstance(id, int)


@route("/show/<name:re:[a-z]+>")
def callback(name):
    assert name.isalpha()


@route("/static/<path:path>")
def callback(path):
    return static_file(path, ...)


# This example handles POST requests to '/hello_post'
@route("/hello_post", method="POST")
def hello_post():
    name = request.POST["name"]
    return "Hello %s!" % name


print(4, "----------------" * 10)

tpl = SimpleTemplate("Hello {{name}}!")
print(tpl.render(name="World"))

print(template("Hello {{name}}!", name="World"))

my_dict = {"number": "123", "street": "Fake St.", "city": "Fakeville"}
print(template("I live at {{number}} {{street}}, {{city}}", **my_dict))


@route("/hello")
@route("/hello/<name>")
@view("hello_template")
def hello(name="World"):
    return dict(name=name)


print(5, "----------------" * 10)

run(host="localhost", port=8080)
