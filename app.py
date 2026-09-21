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


# Werkzeug's `path` converter matches slashes but not a line feed. Its regex
# is `[^/].*?`, which a rule compiles into `(?P<__werkzeug_0>[^/].*?)\Z` and
# the routing matcher applies with a plain `re.compile(...).match(...)` —
# never with DOTALL — so `.` excludes 0x0A. A percent-decoded LF anywhere
# past the first character of the path therefore matched neither rule below
# and Werkzeug raised NotFound: `/a%0ab`, `/a%0a`, `/a%0ab/c`, `/x/y%0az`,
# `/%0a%0a`, `/a%0d%0ab` and every other such shape were answered with a 404
# and an HTML error body, for every verb, where Node answers 200 with the
# 14-byte payload. `[\s\S]` is `.` plus the line feed, so widening the
# trailing class restores the every-path contract without narrowing anything:
# the class is a strict superset of the one it replaces, every path that
# matched before still matches, the first character stays non-slash, and the
# `/` rule below is therefore still required for the empty path.
#
# Subclassing the converter this map already holds keeps the file to its one
# import, and registering the subclass under the name the rule already uses
# keeps the routing table to the two declared rules. This is the same kind of
# framework-default reconciliation as `static_folder=None` above, not added
# behavior: no handler, no error page and no configuration surface appears,
# and a default that contradicted the stated contract stops deciding which
# paths the ported view sees. The registration must precede the `add` calls
# below, because a rule resolves its converters when the map compiles it.
class _AnyPathConverter(app.url_map.converters["path"]):
    regex = r"[^/][\s\S]*?"
    # Carried over from the base converter rather than inferred: the regex
    # spans slashes, so one rule consumes every remaining path segment.
    part_isolating = False


app.url_map.converters["path"] = _AnyPathConverter

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
    #
    # Four further differences from the Node reference belong to the server
    # this call selects rather than to the application, and each was measured
    # against the source: a malformed request line is answered by the
    # standard library's pre-dispatch error path with a 400 whose body and
    # reason phrase carry the request line back (Node sends a bodiless 400);
    # `HTTP/9.9` and HTTP/0.9 requests are answered with no status line,
    # because that path treats the request as HTTP/0.9 and suppresses the
    # status line and headers (Node answers both with a well-formed
    # response); every response carries `Server: Werkzeug/... Python/...`
    # (Node sends no `Server` header); and conflicting `Content-Length` with
    # `Transfer-Encoding: chunked` is accepted rather than rejected, though
    # no second response is emitted and the smuggled request is never
    # processed (Node rejects the framing with a 400). All four are decided
    # before or outside WSGI dispatch, so the view cannot reach them; the
    # only levers are a request-handler subclass, which would need a second
    # import and error-handling code, or a production server or proxy in
    # front — an added dependency. The plan excludes every one of those
    # (§0.2.2 no error handler of any kind and no security hardening; §0.6.1
    # and §0.6.2 one dependency and one import; §0.5.2 accepts the
    # framework's own response headers and adds no code to suppress them),
    # so they are recorded here and closed by an operator fronting the
    # service, not by this file.
    app.run(host="::", port=3000, debug=False)
