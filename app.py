from flask import Flask

# Passing `static_folder` as None suppresses the `/static/<path:filename>`
# rule that Flask registers only when a static folder is set. Its first
# segment is static, so Werkzeug ranks it above the catch-all, and it claims
# only GET, HEAD and OPTIONS under `/static/`: GET is met with a 404 and an
# HTML error body where Node sends the 14-byte payload, HEAD with a bodiless
# 404 where Node sends a bodiless 200, and OPTIONS with an automatic bodiless
# 200 where Node sends those 14 bytes. Every other verb falls through to the
# catch-all, which `hello` answers.
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
# URL unmatched. Passing `defaults` with an empty `path` supplies the view's
# argument so one function serves both rules.
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
    # terminating newline. The `__main__` guard, plus `debug` passed as
    # False to keep the reloader off, hold this to a single emission.
    print("Server running at http://127.0.0.1:3000/")

    # Each argument overrides a documented Flask default that differs from
    # the Node reference: `host` defaults to IPv4 loopback where Node binds
    # the dual-stack wildcard, `port` defaults to 5000 rather than 3000, and
    # an absent `debug` is resolved from ambient process state, which an
    # explicitly passed value overrides.
    #
    # `debug=False` is also the limit of what this call can assert about
    # ambient state. Within that limit it holds: measured, the reloader
    # stays off and the line above is emitted once whatever FLASK_DEBUG
    # holds. Outside it sits one variable belonging to the development
    # server rather than to Flask — WERKZEUG_RUN_MAIN set to the literal
    # "true", the marker a reloader parent leaves for its child. The
    # server reads it before any argument given here, then expects to
    # inherit the listener that parent had already bound, so with the
    # marker present and no such parent it raises instead of binding.
    # No argument reaches that read, and the two changes that would —
    # editing the ambient values, or bypassing this call for a lower-level
    # Werkzeug entry point — are both prohibited for this file, so the
    # limit is recorded here rather than closed.
    app.run(host="::", port=3000, debug=False)
