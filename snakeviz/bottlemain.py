#!/usr/bin/env python

import os.path
from pstats import Stats

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from .stats import table_rows, json_stats

from bottle import route, run
from jinja2 import Environment, FileSystemLoader, select_autoescape

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "debug": True,
    "gzip": True,
}

env = Environment(loader=FileSystemLoader(settings["templates_path"]), autoescape=select_autoescape(["html", "xml"]))


def _list_dir(path):
    """
    Show a directory listing.

    """
    entries = os.listdir(path)
    dir_entries = [[["..", quote(os.path.normpath(os.path.join(path, "..")), safe="")]]]
    for name in entries:
        if name.startswith("."):
            # skip invisible files/directories
            continue
        fullname = os.path.join(path, name)
        displayname = linkname = name
        # Append / for directories or @ for symbolic links
        if os.path.isdir(fullname):
            displayname += "/"
        if os.path.islink(fullname):
            displayname += "@"
        dir_entries.append([[displayname, quote(os.path.join(path, linkname), safe="")]])
    return dir_entries


@route("/snakeviz/<profile_name>")
def snakeviz(profile_name):
    abspath = os.path.abspath(profile_name)
    if os.path.isdir(abspath):
        template = env.get_template("dir.html")
        return template.render(dir_name=abspath, dir_entries=dir_entries)
    else:
        try:
            s = Stats(profile_name)
        except:
            raise RuntimeError("Could not read %s." % profile_name)
        template = env.get_template("viz.html")
        return template.render(profile_name=profile_name, table_rows=table_rows(s), callees=json_stats(s))


if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True)
