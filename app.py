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
    # Re-measured: the line above is already out when that happens, the
    # process then exits non-zero with nothing bound, and Node serves
    # normally under the same variable. `use_reloader=False` does not
    # help either — the read sits ahead of the reloader check that
    # argument reaches. No argument reaches that read, and the two
    # changes that would — editing the ambient values, or bypassing this
    # call for a lower-level Werkzeug entry point — are both prohibited
    # for this file (§0.2.2 excludes environment-variable configuration,
    # §0.3.1 fixes the statements this file holds), so the limit is
    # recorded here rather than closed: this process is started with no
    # WERKZEUG_RUN_MAIN in its environment.
    #
    # Six further differences from the Node reference belong to the server
    # this call selects rather than to the application. Every one is
    # decided by the standard library's HTTP machinery, or by the
    # development server building the environ, before WSGI dispatch — so
    # the view never sees the request and no argument here reaches it.
    # Each was re-measured against the running source.
    #
    # 1. A request line that is not exactly three tokens — one carrying a
    # space, a quote, a raw tab or a raw carriage return — draws a 400
    # that echoes the request line back: raw in the reason phrase, and
    # HTML-escaped in a `text/html` body. Measured, that is a 646, 624 or
    # 586-byte response around a 406, 392 or 373-byte body, where Node
    # sends a bodiless 47-byte 400. The echo is bounded to the sender's
    # own request line on the sender's own connection; it is not stored
    # and no other client can reach it.
    #
    # 2. Request lines the standard library resolves as HTTP/0.9 are
    # answered with no status line and no headers: `HTTP/9.9` draws a
    # 340-byte error page carrying no status line, and an HTTP/0.9
    # request line or a bare CRLF inside the target draws the 14 payload
    # bytes alone, where Node answers a well-formed 89-byte 200. A
    # request line of no tokens at all — a leading blank line, which
    # RFC 9112 §2.2 says a recipient should ignore — draws nothing and
    # the connection closes, where Node answers 200 with the payload.
    # Carriage-return-only framing draws nothing while the client keeps
    # its write side open, and a 357-byte status-line-free error page
    # once it half-closes.
    #
    # 3. Conflicting `Content-Length` and `Transfer-Encoding: chunked` is
    # accepted with a 200 and the payload where Node rejects the framing
    # with a bodiless 400. It stays bounded: one response per connection,
    # and a request smuggled after the body never reaches the access log.
    #
    # 4. The header reader's budget is 100 lines counting the blank
    # terminator, so a request carrying 100 or more header fields draws
    # `431 Too many headers` with a 333-byte body that echoes neither
    # names nor values; 99 fields still answer the payload, and Node
    # answers it at every count measured.
    #
    # 5. `Expect: 100-continue` draws two interim `100 Continue` lines,
    # the standard library's expect handler and the environ construction
    # each sending one, where Node sends one before the 200.
    #
    # 6. Every response carries `Server: Werkzeug/... Python/...`, which
    # Node does not send.
    #
    # The machinery behind all six is reachable from objects this module
    # already holds, so these are excluded rather than out of reach. A
    # request-handler subclass suppressing the echo was measured to
    # answer the four malformed request lines with Node's bodiless
    # 47-byte 400 exactly — and to leave the status-line-free shapes
    # unfixed, moving the version case from an error page to zero bytes.
    # It is error-handling and suppression code whichever shape it takes,
    # and §0.2.2 excludes an error handler of any kind and any hardening,
    # §0.6.1 and §0.6.2 hold this file to one dependency and one import,
    # and §0.5.2 accepts the framework's own responses and adds no code
    # to suppress them — having already decided this class by declining
    # to reproduce the source parser's rejections rather than add status
    # paths no request asked for. So all six are recorded here and
    # closed, where an operator needs them closed, by the server or proxy
    # in front of this one rather than by this file.
    #
    # One difference is not about requests at all. This file installs no
    # signal handling and CPython leaves an inherited `SIG_IGN` in place,
    # so started as a background job of a non-interactive shell — where
    # SIGINT arrives already ignored — the process keeps serving on
    # SIGINT and stops on SIGTERM, while Node installs its own handler
    # and exits on either. Started with the disposition at its default,
    # both stop on SIGINT. SIGTERM stops this process in both cases;
    # matching Node in the first would need a second import — the
    # standard library's signal module — which §0.6.2 excludes.
    app.run(host="::", port=3000, debug=False)
