# Hello World Response Audit - FAIL

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| Status code | `200` (runtime default; `server.js` sets none) | `200` | PASS |
| Content-Type | `text/plain` per the plain-text spec | (absent) | FAIL |
| Body | `Hello, World!\n`, 14 bytes (`server.js` literal) | `Hello, World!\n`, 14 bytes | PASS |

Checked 2026-09-22T06:46:12Z - one `GET http://127.0.0.1:3000/` against `node server.js`.
