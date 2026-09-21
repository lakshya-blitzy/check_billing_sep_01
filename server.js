const server = require('http').createServer((req, res) => {
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    req.resume(); // discard any body so the connection stays reusable
    res.writeHead(405, { 'Allow': 'GET, HEAD', 'Content-Length': '0' });
    return res.end();
  }
  res.end('Hello, World!\n');
});

let stopping = false;
const stopServer = (reason) => {
  if (stopping) return;
  stopping = true;
  console.log('Shutting down:', reason);
  server.close(); // in-flight requests finish, then the empty event loop ends the process
  setTimeout(() => server.closeAllConnections(), 5000).unref(); // backstop; must not hold the process open
};

const fatal = (label) => (err) => {
  console.error(label + ':', err);
  process.exitCode = 1;
  stopServer(label); // never resume after a fatal error
};

server.on('error', (err) => {
  console.error('Server error:', err.message);
  process.exitCode = 1;
});
server.on('connect', (req, socket) => socket.on('error', () => socket.destroy()).resume().end('HTTP/1.1 405 Method Not Allowed\r\nAllow: GET, HEAD\r\nContent-Length: 0\r\nConnection: close\r\n\r\n', () => socket.destroy()));
server.on('checkExpectation', (req, res) => (req.method !== 'GET' && req.method !== 'HEAD') ? server.emit('request', req, res) : res.writeHead(417).end());
process.on('SIGTERM', () => stopServer('SIGTERM'));
process.on('SIGINT', () => stopServer('SIGINT'));
process.on('uncaughtException', fatal('uncaught exception'));
process.on('unhandledRejection', fatal('unhandled rejection'));
server.listen(3000, () => console.log('Server running at http://127.0.0.1:3000/'));
