# QA Report — check_billing_sep_01

Black-box verification of the running server on Node v22.23.2, commit `a3cb672`.

## Missing test coverage

- **No test suite, and nothing invoking a runner** — no `test`/`tests`/`__tests__`/`spec`/`e2e` directory, no `*.test.*`/`*.spec.*`/`test*.js` match, no manifest to declare a test script; the gap is the absence of any automated check, not of a runner — `node --test` and `node:assert` resolve here with no manifest.
- **No runtime reproducibility anchor** — no `package.json`, lockfile or `node_modules`, and no `engines`, `.nvmrc` or `.node-version`.
- **No coverage configuration** — `.nycrc`, `.c8rc`, `codecov.yml`, `coverage/`, `lcov.info` all absent; `--experimental-test-coverage` is available on this runtime but unconfigured and uninvoked.
- **No automated quality gate** — no CI workflow of any provider (`.github`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci`, `.travis.yml`), no `Makefile`/`Taskfile.yml`, no linter, formatter or type-checker config.
- **No testing documentation** — no `TESTING.md`, `CONTRIBUTING.md`, `QA.md` or `docs/`; `README.md` is the bare 22-byte heading `# check_billing_sep_01`, with no run command [README.md:1].
- **Nothing testable in process** — `grep -c -F` returns 0 for `module.exports`, `exports.`, `export ` and `require.main`, so loading `server.js` binds TCP 3000 and logs rather than yielding an assertable handler; checks go over the socket [server.js:1].

## Response confirmation

- `curl -sS -i --max-time 5 http://127.0.0.1:3000/` returned `HTTP/1.1 200 OK` with a body of exactly 14 bytes, `Hello, World!\n`, SHA-256 `c98c24b6…ad31` [server.js:1].
- Exactly four headers — `Date`, `Connection: keep-alive`, `Keep-Alive: timeout=5`, `Content-Length: 14` — and **no `Content-Type`**; the source has no `setHeader` or `writeHead` [server.js:1].
- Those bytes differ from the request's `Hello World` shorthand — comma, trailing `!`, newline; the measured bytes are the contract.
- A second request, `GET /billing/invoices?x=1`, returned identical status and a byte-identical body; the handler never reads `req` (`grep -c 'req\.'` → 0) [server.js:1].
- Startup wrote one 41-byte line, `Server running at http://127.0.0.1:3000/`, then nothing: stdout was still 41 bytes and stderr empty after both probes [server.js:1].

## Error paths

- **Startup port contention — CHECKED**: a second instance exited 1 on an unhandled `'error'` event, `listen EADDRINUSE: address already in use :::3000` — the dual-stack wildcard, not the advertised `127.0.0.1`; the source has no `'error'` listener [server.js:1].
- **Termination, default exit and port release — CHECKED**: `SIGTERM` left no shutdown message (stdout still 41 bytes) and released the port; a following `net.connect` was refused, `ECONNREFUSED`.
- **Termination, in-flight draining — UNTESTED**: the process was idle when signalled, and the source registers no signal handler and no `server.close()` [server.js:1].
- **Configuration and project entry points — UNTESTED**: `process.env` is never read, so port and log text are literals with no override [server.js:1]; with no manifest, the npm-script path is unavailable rather than passing.
- **Request handling beyond the two probes — UNTESTED**: the source caps no header size, framing, payload or concurrency [server.js:1]; `HEAD`, `CONNECT`, malformed requests and load were not measured.
- **Exposure, transport and recovery — UNTESTED**: the wildcard bind leaves the unauthenticated endpoint reachable on every interface, the source configures no TLS, and the checkout has no supervision or restart mechanism [server.js:1].
