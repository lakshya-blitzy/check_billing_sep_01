Black-box checks on a running instance: Node `v22.23.2` (`node --version`); `server.js` last committed at `a3cb672` (`git log -- server.js`).

## Missing test coverage

- **No test suite, and nothing invoking a runner** — `ls -d` finds no `test`/`tests`/`__tests__`/`spec`/`e2e` directory, `find` no `*.test.*`/`*.spec.*`/`test*.js` match, and no manifest declares a test script; the gap is the absence of any automated check, not of a runner — `node --test` with `node:assert` runs here and reports `# tests 0`.
- **No runtime reproducibility anchor** — that sweep finds no `package.json`, lockfile, `node_modules`, `.nvmrc` or `.node-version`, so no `engines` pin either.
- **No coverage configuration** — that sweep finds no `.nycrc`, `.c8rc`, `codecov.yml`, `coverage/` or `lcov.info`; `node --help` lists `--experimental-test-coverage` and thresholds, none configured or invoked.
- **No automated quality gate** — that sweep finds no CI workflow (`.github`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci`, `.travis.yml`), no `Makefile`/`Taskfile.yml`, no linter, formatter or type-checker config.
- **No testing documentation** — that sweep finds no `TESTING.md`, `CONTRIBUTING.md`, `QA.md` or `docs/`; `README.md` is the bare 22-byte heading `# check_billing_sep_01`, with no run command [README.md:1].
- **Nothing testable in process** — `grep -c -F` returns 0 for `module.exports`, `exports.`, `export ` and `require.main` [server.js:1], so loading `server.js` binds TCP 3000 and logs rather than yielding a handler; checks go over the socket.

## Response confirmation

- `curl -sS -i --max-time 5 http://127.0.0.1:3000/` returned `HTTP/1.1 200 OK` and exactly 14 bytes (`wc -c`) of `Hello, World!\n`, the `res.end` literal [server.js:1], SHA-256 `c98c24b677eff44860afea6f493bbaec5bb1c4cbb209c6fc2bbb47f66ff2ad31` (`sha256sum`).
- That response carried exactly four headers — `Date`, `Connection: keep-alive`, `Keep-Alive: timeout=5`, `Content-Length: 14` — and **no `Content-Type`**; the source has no `setHeader` or `writeHead` [server.js:1].
- Those bytes differ from the request's `Hello World` shorthand — comma, trailing `!`, newline [server.js:1]; the measured bytes are the contract.
- A second request, `GET /billing/invoices?x=1`, returned identical status and a byte-identical body; the handler never reads `req` (`grep -c 'req\.'` → 0) [server.js:1].

## Error paths

- **Startup port contention — CHECKED**: a second `node server.js` exited 1 on an unhandled `'error'`, `listen EADDRINUSE: address already in use :::3000` — the dual-stack wildcard, not the logged `127.0.0.1`; the source has no `'error'` listener [server.js:1].
- **Termination, default exit and port release — CHECKED**: `kill -TERM` left no shutdown message (stdout still 41 bytes) and released the port; a following `net.connect` probe printed `ECONNREFUSED`.
- **Termination, in-flight draining — UNTESTED**: the process was idle when signalled; the source registers no signal handler and no `server.close()` [server.js:1].
- **Configuration and project entry points — UNTESTED**: `process.env` is never read [server.js:1], so port and log text are literals; with no manifest (above), the npm-script path is unavailable rather than passing.
- **Request handling beyond the two probes — UNTESTED**: the source caps no header size, framing, payload or concurrency [server.js:1]; `HEAD`, `CONNECT`, malformed requests and load were not measured.
- **Exposure, transport and recovery — UNTESTED**: no host is passed to `.listen` and no TLS or restart path exists [server.js:1], so the unauthenticated endpoint is reachable on every interface, plaintext, unsupervised.
