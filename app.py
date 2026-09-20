from flask import Flask

# `static_folder=None` suppresses the `/static/<path:filename>` rule that
# Flask registers only when `static_folder` is set. Its first segment is
# static, so Werkzeug ranks it above the catch-all and it claims the GET,
# HEAD and OPTIONS requests under `/static/` that `hello` should answer —
# GET and HEAD are met with 404 where Node sends the 14-byte body. Its
# method set excludes every other verb, which falls through to the catch-all.
app = Flask(__name__, static_folder=None)


def hello(path):
    # Flask encodes a returned string to UTF-8 as the body of a 200
    # response, with no newline normalization, so the trailing "\n" is part
    # of the 14-byte payload. `path` is ignored, as the Node handler never
    # inspects `req`.
    return "Hello, World!\n"


app.view_functions["hello"] = hello

# The rule for the root URL. A second rule for "/" is structurally required:
# the `path` converter's pattern requires a non-slash first character, so it
# cannot match the empty string and `/<path:path>` alone would leave the root
# URL unmatched. `defaults={"path": ""}` supplies the view's argument so one
# function serves both rules.
# Leaving `methods` as None on both rules is what answers every method: a
# Werkzeug rule with no method list allows all of them, whereas Flask's
# route decorator declares GET, with HEAD and OPTIONS added automatically,
# and any enumerated list — that default included — answers 405 for the
# verbs outside it.
app.url_map.add(
    app.url_rule_class(
        "/", defaults={"path": ""}, endpoint="hello", methods=None
    )
)

# The `path` converter matches slashes as well as text, so this one rule
# covers arbitrary depth.
app.url_map.add(
    app.url_rule_class("/<path:path>", endpoint="hello", methods=None)
)


if __name__ == "__main__":
    # The Node literal, character-for-character; `print` supplies the
    # terminating newline. The `__main__` guard and `debug=False` keeping the
    # reloader off are what hold this to a single emission.
    print("Server running at http://127.0.0.1:3000/")

    # Each argument overrides a documented Flask default that differs from
    # the Node reference: `host` defaults to IPv4 loopback where Node binds
    # the dual-stack wildcard, `port` defaults to 5000 rather than 3000, and
    # an absent `debug` is resolved from ambient process state, which an
    # explicitly passed value overrides.
    app.run(host="::", port=3000, debug=False)
