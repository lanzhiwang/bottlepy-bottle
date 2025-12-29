"""
Request Data

Request.GET: Query parameters

Request.query: Alias for Request.GET

Request.POST: orm fields and file uploads combined

Request.forms: orm fields

Request.files: File uploads or very large form fields

Request.params: Query parameters and form fields combined

"""

from bottle import request, response, route, template


@route("/hello")
def hello():
    name = request.cookies.username or "Guest"
    return template("Hello {{name}}", name=name)


@route("/is_ajax")
def is_ajax():
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return "This is an AJAX request"
    else:
        return "This is a normal request"


@route("/counter")
def counter():
    count = int(request.cookies.get("counter", "0"))
    count += 1
    response.set_cookie("counter", str(count))
    return "You visited this page %d times" % count


@route("/my_ip")
def show_ip():
    ip = request.environ.get("REMOTE_ADDR")
    # or ip = request.get('REMOTE_ADDR')
    # or ip = request['REMOTE_ADDR']
    return template("Your IP is: {{ip}}", ip=ip)
