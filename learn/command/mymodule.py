import bottle

app = bottle.default_app()


@app.route("/hello")
def hello():
    return "Hello World!"
