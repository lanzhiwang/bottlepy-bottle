"""
Templates
"""

from bottle import route, template, view


@route("/hello")
@route("/hello/<name>")
def hello(name="World"):
    return template("hello_template", name=name)


@route("/hello")
@route("/hello/<name>")
@view("hello_template")
def hello(name="World"):
    return dict(name=name)
