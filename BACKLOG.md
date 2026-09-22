# Hello World Service Backlog

This backlog decomposes the Hello World HTTP service in this repository — a single Node.js listener, built on the standard-library `http` module, that binds port 3000 and uses the same greeting handler for every request.

## Server Setup

Everything that gets the process listening on a known port and reporting that it is up.

### Start the HTTP listener

**Story:** An operator starts the service with one command and it accepts HTTP connections on port 3000.

**Estimate:** 1 point — one built-in `http` call with nothing to install.

**Acceptance:** Starting the service leaves it listening on port 3000, and a client can connect to it.

### Announce readiness on startup

**Story:** An operator sees one line confirming the service is up and where it is listening.

**Estimate:** 1 point

**Acceptance:** Starting the service prints a single line saying it is running and on which port.

### Set the port without editing source

**Story:** An operator chooses the listening port through an environment variable, falling back to 3000.

**Estimate:** 2 points — a configuration read plus a default, and the startup line has to report the same value.

**Acceptance:** With no port configured the service still listens on 3000; with one configured it listens on that port and the startup line names it.

## Request Routing

How a request is answered — today every path is answered identically, so the first increment is a branch on the request URL.

### Greeting on the root path

**Story:** A client requesting the root path receives the greeting.

**Estimate:** 1 point — today's handler already returns this body for every request, so the story only pins it to the root path.

**Acceptance:** GET / returns 200 with the greeting text

### Unknown paths answer 404

**Story:** A client requesting any other path gets a clear not-found response instead of the greeting.

**Estimate:** 2 points — this introduces the first branch on the request URL, so the handler stops being a constant function of its input.

**Acceptance:** A request to a path other than the root returns 404 with a short not-found message, and the root path is unaffected.
