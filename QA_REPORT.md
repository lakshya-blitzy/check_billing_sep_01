# QA Report

Node `v22.23.2` [/usr/bin/node:--version]; baseline `a3cb672` [.git/packed-refs:a3cb672] tracks only `server.js` and `README.md`, both unchanged: `git diff --name-status a3cb672` returns `A QA_REPORT.md` alone.

## Missing test coverage

- **No test suite, and nothing invoking a runner** — no `test`/`tests`/`__tests__`/`spec`/`e2e` directory, `*.test.*`/`*.spec.*`/`test*.js` file or manifest test script is tracked [.git/index:paths]; the gap is the absence of any automated check, not of a runner [/usr/bin/node:--test] — the runtime supplies `node --test` and `node:assert`; nothing invokes them.
- **No runtime reproducibility anchor** — no `package.json` (hence no `engines` pin), lockfile, `node_modules`, `.nvmrc` or `.node-version` is tracked [.git/index:paths].
- **No coverage configuration** — no `.nycrc`, `.c8rc`, `codecov.yml`, `coverage/` or `lcov.info` is tracked [.git/index:paths]; the runtime's `--experimental-test-coverage` is available but unconfigured [/usr/bin/node:--help].
- **No automated quality gate** — no CI workflow (`.github`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci`, `.travis.yml`), `Makefile`/`Taskfile.yml`, or linter, formatter or type-checker config is tracked [.git/index:paths].
- **No testing documentation** — no `TESTING.md`, `CONTRIBUTING.md`, `QA.md` or `docs/` is present; `README.md` is the bare 22-byte heading `# check_billing_sep_01`, with no run command [README.md:1].
- **Nothing testable in process** — nothing is exported and no `require.main` guard exists [server.js:1], so loading `server.js` binds TCP 3000 and logs rather than yielding a handler; checks go over the socket.

## Response confirmation

Root response probe (includes headers):

```bash
curl -sS -i --max-time 5 http://127.0.0.1:3000/
```

- The probe returned `HTTP/1.1 200 OK` and exactly 14 bytes of `Hello, World!\n`, the `res.end` literal [server.js:1], SHA-256 `c98c24b677eff44860afea6f493bbaec5bb1c4cbb209c6fc2bbb47f66ff2ad31`.
- That response carried exactly four headers — `Date`, `Connection: keep-alive`, `Keep-Alive: timeout=5`, `Content-Length: 14` — and **no `Content-Type`**; the source has no `setHeader` or `writeHead` [server.js:1].
- Those bytes differ from the request's `Hello World` shorthand — comma, trailing `!`, newline [server.js:1]; the measured bytes are the contract.
- A second request, `GET /billing/invoices?x=1`, returned identical status and a byte-identical body; the handler never reads `req` [server.js:1].

## Error paths

- **Startup port contention — CHECKED**: a second `node server.js` exited 1 on an unhandled `'error'`, `listen EADDRINUSE: address already in use :::3000` — the dual-stack wildcard, not the logged `127.0.0.1`; the source has no `'error'` listener [server.js:1].
- **Termination, default exit and port release — CHECKED**: `kill -TERM` left no shutdown message (stdout still 41 bytes) and released the port, a following `net.connect` probe printing `ECONNREFUSED`; the source logs only at startup [server.js:1].
- **Termination, in-flight draining — UNTESTED**: the process was idle when signalled; the source registers no signal handler and no `server.close()` [server.js:1].
- **Configuration and project entry points — UNTESTED**: `process.env` is never read [server.js:1], so port and log text are literals; no manifest or project script exists, so the npm-script path is unavailable rather than passing.
- **Request handling beyond the two probes — UNTESTED**: the source caps no header size, framing, payload or concurrency [server.js:1]; `HEAD`, `CONNECT`, malformed requests and load were not measured.
- **Exposure, transport and recovery — UNTESTED**: no host is passed to `.listen` and no TLS or restart mechanism appears in `server.js` [server.js:1]; deployment supervision and restart/reboot recovery were not exercised.
