# User Flow — server.js Startup to HTTP 200

This is a lightweight walkthrough of the trivial single-file Node.js HTTP server at the repository root, whose whole implementation is one chained statement in `server.js` [server.js:1]. It follows that server from process start to a delivered HTTP 200 carrying the Hello World body, over an ordinary HTTP/1.1 `GET` on a persistent connection, noting at each step what could fail or add latency.

## 1. Start Process

`node server.js` from the repository root loads the file's single CommonJS statement, resolves the built-in `http` module and registers the inline request handler without calling it [server.js:1]; nothing is installed or built beforehand, so a cold process still does its own start-up work before it can answer anything and its first response can feel slower than the ones that follow.

## 2. Bind and Listen

`.listen(3000, ...)` asks the operating system for TCP port 3000, and its callback then prints a single readiness line naming the loopback address and that port even though no host argument is given, so the listener actually answers on every interface [server.js:1]. If something else already holds the port the server emits an `'error'` event, and because no `'error'` listener is registered [server.js:1] that event is rethrown and the process exits without ever listening.

## 3. Receive Request

The runtime accepts the connection and parses the request line and headers before it emits the request event, so no application code has run yet — and a request its parser turns away, whether malformed, carrying an oversized header block, or with headers that never finish arriving, is answered by the runtime alone and never reaches the handler, leaving no application-side trace because nothing is logged per request [server.js:1]. A fresh connection also pays setup cost that a reused keep-alive connection avoids, and a socket left idle past its window has already been closed by the runtime, so a caller that comes back to it has to reconnect first.

## 4. Handler Runs

The handler runs on the request event, reads nothing at all from the request — not the method, path, query, headers or body — and its only statement is `res.end('Hello, World!\n')` [server.js:1]; it is synchronous with no awaited application work, so latency here reflects the single event loop being occupied elsewhere rather than anything the handler itself does.

## 5. Response Sent

That `res.end` call hands the body to the runtime, which supplies the entire status line and header block because the handler sets neither a status nor a header [server.js:1] — a `200` with `Date`, `Content-Length: 14` and keep-alive headers, the 14-byte body, and no `Content-Type`, which a caller relying on media-type negotiation has to tolerate. If the caller has already disconnected the write is discarded and the process carries on serving others, while stopping the process releases the port immediately and cuts off anything still in flight.

Confirmed by running it during this work: the process started on the Node.js already installed in this environment, printed its readiness line, and answered the traced `GET` with `200` and the unchanged 14-byte body.
