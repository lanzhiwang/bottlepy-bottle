"""
Serving Assets
"""

from bottle import (
    route,
    static_file,
)


@route("/static/<filepath:path>")
def server_static(filepath):
    return static_file(filepath, root="/path/to/your/static/files")


# File downloads


@route("/download/<filename>")
def download(filename):
    return static_file(
        filename, root="/path/to/static/files", download=f"download-{filename}"
    )
