"""
The response Object

response.set_header('Set-Cookie', 'name=value')
response.add_header('Set-Cookie', 'name=value2')

"""

from bottle import route, request, response, redirect


@route("/wiki/<page>")
def wiki(page):
    response.set_header("Content-Language", "en")


@route("/wrong/url")
def wrong():
    redirect("/right/url")


# Cookies
@route("/hello")
def hello_again():
    if request.get_cookie("visited"):
        return "Welcome back! Nice to see you again"
    else:
        response.set_cookie("visited", "yes")
        return "Hello there! Nice to meet you"
