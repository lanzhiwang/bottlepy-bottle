"""
Changing the Default Encoding
"""

from bottle import (
    route,
    response,
)


@route("/iso")
def get_iso():
    response.charset = "ISO-8859-15"
    return "This will be sent with ISO-8859-15 encoding."


@route("/latin9")
def get_latin():
    response.content_type = "text/html; charset=latin9"
    return "ISO-8859-15 is also known as latin9."
