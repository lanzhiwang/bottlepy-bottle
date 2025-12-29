import time
import bottle
from bottle import (
    route,
    run,
    request,
    response,
    abort,
    template,
    hook,
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


# Lets start with "Hello World!"
# Point your Browser to 'http://localhost:8080/' and greet the world :D
@route("/")
def hello_world():
    return "Hello World!"


# Receiving GET parameter (/hello?name=Tim) is as easy as using a dict.
# @route("/hello")
# def hello_get():
#     name = request.GET["name"]
#     return "Hello %s!" % name


# This example handles POST requests to '/hello_post'
# @route("/hello_post", method="POST")
# def hello_post():
#     name = request.POST["name"]
#     return "Hello %s!" % name


# URL-parameter are a useful tool and generate nice looking URLs
# This handles requests such as '/hello/Tim' or '/hello/Jane'
# @route("/hello/<name>")
# def hello_url(name):
#     return "Hello %s!" % name


# Throwing an error using abort()
# @route("/private")
# def private():
#     if request.GET.get("password", "") != "secret":
#         abort(401, "Go away!")
#     return "Welcome!"


print(4, "----------------" * 10)

run(host="localhost", port=8080)
