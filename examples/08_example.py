"""
Error handling
"""

from bottle import route, abort, error


@error(404)
def error404(error):
    return "Nothing here, sorry"


@route("/restricted")
def restricted():
    abort(401, "Sorry, access denied.")
