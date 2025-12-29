"""
Using Plugins
"""

import time
from bottle import route, response, install, uninstall


def stopwatch(callback):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = callback(*args, **kwargs)
        end = time.time()
        response.headers["X-Exec-Time"] = str(end - start)
        return result

    return wrapper


@route("/timed")
@stopwatch  # <-- This works, but do not do this
def timed():
    time.sleep(1)
    return "DONE"


install(stopwatch)


@route("/timed")
def timed():
    pass


class SQLitePlugin(object):
    pass


sqlite_plugin = SQLitePlugin(dbfile="/tmp/test.db")
install(sqlite_plugin)

uninstall(sqlite_plugin)  # uninstall a specific plugin
uninstall(SQLitePlugin)  # uninstall all plugins of that type
uninstall("sqlite")  # uninstall all plugins with that name
uninstall(True)  # uninstall all plugins at once


@route("/timed", apply=[stopwatch])
def timed():
    pass


@route("/notime", skip=[stopwatch])
def no_time():
    pass
