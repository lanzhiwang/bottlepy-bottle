"""
Configuration
"""

import bottle
from bottle import request

app = bottle.default_app()  # or bottle.Bottle() if you prefer

app.config["autojson"] = False  # Turns off the "autojson" feature
app.config["sqlite.db"] = ":memory:"  # Tells the sqlite plugin which db to use
app.config["myapp.param"] = "value"  # Example for a custom config value.

# Change many values at once
app.config.update({"autojson": False, "sqlite.db": ":memory:", "myapp.param": "value"})

# Add default values
app.config.setdefault("myapp.param2", "some default")

# Receive values
param = app.config["myapp.param"]
param2 = app.config.get("myapp.param2", "fallback value")


# An example route using configuration values
@app.route("/about", view="about.rst")
def about():
    email = app.config.get("my.email", "nomail@example.com")
    return {"email": email}


def is_admin(user):
    return user == request.app.config["myapp.admin_user"]


def switch_own_debug_mode_to(value):
    pass


@app.hook("config")
def on_config_change(key, value):
    if key == "debug":
        switch_own_debug_mode_to(value)


class SomePlugin(object):
    def setup(app):
        app.config.meta_set("some.int", "filter", int)
        app.config.meta_set("some.list", "filter", lambda val: str(val).split(";"))
        app.config.meta_set("some.list", "help", "A semicolon separated list.")

    def apply(self, callback, route):
        pass


app = bottle.default_app()
app.install(SomePlugin())

app.config["some.list"] = "a;b;c"  # Actually stores ['a', 'b', 'c']
app.config["some.int"] = "not an int"  # raises ValueError
