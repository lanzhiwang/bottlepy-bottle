"""
Request Routing
"""

from bottle import (
    route,
    template,
    static_file,
)


@route("/hello")
def hello():
    return "Hello World!"


@route("/")
@route("/hello/<name>")
def greet(name="Stranger"):
    return template("Hello {{name}}, how are you?", name=name)


@route("/wiki/<pagename>")  # matches /wiki/Learning_Python
def show_wiki_page(pagename):
    pass


@route("/<action>/<user>")  # matches /follow/defnull
def user_api(action, user):
    pass


@route("/object/<id:int>")
def callback(id):
    assert isinstance(id, int)


@route("/show/<name:re:[a-z]+>")
def callback(name):
    assert name.isalpha()


@route("/static/<path:path>")
def callback(path):
    return static_file(path, ...)
