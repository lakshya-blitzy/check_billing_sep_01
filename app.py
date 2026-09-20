# Flask port of server.js — behavioral parity with the Node reference.
#
# Reference (server.js, read-only behavioral contract, 142 bytes):
#   require('http').createServer((req,res)=>res.end('Hello, World!\n'))
#   .listen(3000,()=>console.log('Server running at http://127.0.0.1:3000/'));
#
# The Node handler never inspects `req`, so it answers HTTP 200 with the same
# 14-byte body for every path and every method that reaches it. This module
# reproduces that on four dimensions: response body bytes, status code,
# the bound port and interface, and a startup line printed exactly once.
#
# Parity is byte-exact for every path and for every method the application
# layer sees. It stops at two HTTP-parser edges that differ before any
# application code runs: Werkzeug accepts an unknown verb such as `FOO` (200
# here, 400 from Node's parser) and accepts `CONNECT` (200 here, no response
# from Node). Neither is special-cased — a 200 on any method is the required
# behavior, and reproducing Node's parser rejections would add status paths
# that are not part of the contract.

# The only import in this module. The body literal needs no helper, the
# startup line uses the builtin `print`, and the port is a hard-coded
# literal never read from outside this file, so nothing else is imported.
from flask import Flask

# The WSGI application object.
#
# `static_folder=None` is load-bearing parity reconciliation, not decoration
# and not hardening. Constructed conventionally, Flask auto-registers a
# `/static/<path:filename>` rule for GET/HEAD/OPTIONS, and Werkzeug matches
# more specific rules first — a static first segment outranks a variable
# one — so every request under `/static/` would be dispatched to the
# built-in static view and answered with 404 and an HTML error body where
# Node answers 200 with the 14-byte literal. Flask registers that route
# only if `static_folder` is set, so passing None prevents the registration
# entirely rather than competing with it. It is passed by keyword because
# Flask's second positional parameter is `static_url_path`, not
# `static_folder`.
app = Flask(__name__, static_folder=None)


# The request handler: answers every request with the reference body.
def hello(path):
    # Returning a plain `str` fixes both the status code and the body bytes:
    # Flask converts a returned string into a 200 response whose body is the
    # string encoded to UTF-8, with no newline normalization or trimming, so
    # the trailing "\n" is carried through and the body is exactly the 14
    # bytes 48656c6c6f2c20576f726c64210a. Building an explicit response
    # object would be more code for the same result. `path` is ignored,
    # mirroring the Node handler, which never inspects `req`.
    return "Hello, World!\n"


# Register the view under the endpoint name both URL rules reference.
app.view_functions["hello"] = hello

# The rule for the root URL. A second rule for "/" is structurally required:
# the `path` converter's pattern requires a non-slash first character, so it
# cannot match the empty string and `/<path:path>` alone would leave the root
# URL unmatched. `defaults={"path": ""}` supplies the view's argument so one
# function serves both rules.
#
# Leaving the `methods` argument as None on both rules is the only
# construction that answers every method, which is what the Node server
# does. A Werkzeug rule with no method list allows all methods, whereas
# Flask's route decorator resolves an absent method list to GET alone and
# any enumerated list answers 405 for verbs outside it. The rules are
# therefore added directly through three documented public Flask
# attributes — `url_rule_class` (the rule class `add_url_rule` itself
# uses), `url_map` (the map that stores the rules) and `view_functions`
# (the endpoint-to-view mapping) — which keeps the module to a single
# import in a single file.
app.url_map.add(
    app.url_rule_class(
        "/", defaults={"path": ""}, endpoint="hello", methods=None
    )
)

# The rule for every other URL. The `path` converter matches slashes as
# well as text, so it covers arbitrary depth. Werkzeug's slash-merging and
# strict-slash defaults need no argument here, for three separate reasons.
# Repeated leading slashes are canonicalized before matching:
# `MapAdapter.match` strips the leading slashes from the path it matches
# with and prepends a single one, so `//foo` is matched as `/foo`, returns
# 200 and resolves to path='foo' rather than redirecting. Repeated slashes
# *inside* a captured path are separately exempt from merge redirects
# because they fall within a variable part, so `/a//b` returns 200 and
# resolves to path='a//b'. And a trailing-slash redirect applies only to
# rules that themselves end in a slash, which neither rule does, so
# `/foo/` returns 200 and resolves to path='foo/'.
app.url_map.add(
    app.url_rule_class("/<path:path>", endpoint="hello", methods=None)
)


if __name__ == "__main__":
    # The startup line, reproducing the Node literal character-for-character.
    # `print` supplies the terminating newline. Exactly one construct emits
    # it, so it appears exactly once.
    print("Server running at http://127.0.0.1:3000/")

    # The bind and the serve loop. Each argument reconciles one documented
    # Flask default with the reference implementation:
    #   host="::"    — the default binds IPv4 loopback only, while the Node
    #                  server binds the dual-stack wildcard and is reachable
    #                  on every interface.
    #   port=3000    — the documented default is 5000; 3000 is the literal
    #                  server.js passes to .listen(), never a runtime lookup.
    #   debug=False  — with the argument absent, Flask resolves debug state
    #                  from ambient process state outside this file, so a
    #                  stray debug flag would start the reloader and
    #                  re-execute this module, emitting the startup line
    #                  twice. An explicitly passed `debug` overrides all
    #                  other sources, so the line is emitted once either
    #                  way. This argument introduces no configuration of
    #                  its own; it stops ambient state configuring the
    #                  process.
    app.run(host="::", port=3000, debug=False)
