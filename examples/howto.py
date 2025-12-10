from bottle import (
    route,
    run,
    request,
    response,
    abort,
    template,
    debug,
)

debug(True)


# Lets start with "Hello World!"
# Point your Browser to 'http://localhost:8080/' and greet the world :D
@route("/")
def hello_world():
    return "Hello World!"


# Receiving GET parameter (/hello?name=Tim) is as easy as using a dict.
@route("/hello")
def hello_get():
    name = request.GET["name"]
    return "Hello %s!" % name


# This example handles POST requests to '/hello_post'
@route("/hello_post", method="POST")
def hello_post():
    name = request.POST["name"]
    return "Hello %s!" % name


# URL-parameter are a useful tool and generate nice looking URLs
# This handles requests such as '/hello/Tim' or '/hello/Jane'
@route("/hello/<name>")
def hello_url(name):
    return "Hello %s!" % name


# Throwing an error using abort()
@route("/private")
def private():
    if request.GET.get("password", "") != "secret":
        abort(401, "Go away!")
    return "Welcome!"


run(host="localhost", port=8080)
