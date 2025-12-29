"""
The Application Object
"""

import bottle
from bottle import Bottle

app = Bottle()

# Enable debug at runtime
bottle.debug(True)


@app.route("/hello")
def hello():
    return "Hello World!"


if __name__ == "__main__":
    app.run(host="localhost", port=8080)
    # Debug Mode
    app.run(host="localhost", port=8080, debug=True)
    # Auto Reloading reloader=True)
    app.run(host="localhost", port=8080, debug=True, reloader=True)
