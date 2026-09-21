const express = require('express');
const morgan = require('morgan');

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '127.0.0.1';
const MESSAGE = process.env.MESSAGE || 'Hello, World!\n';

const app = express();
app.use(morgan('combined'));
app.all('/{*splat}', (req, res) => res.send(MESSAGE));

// HOST is only advertised in the startup line; app.listen omits it to keep the original all-interfaces bind.
const server = app.listen(PORT);
server.once('listening', () => {
  const bound = server.address();
  console.log(typeof bound === 'string' ? `Server running on UNIX socket ${bound}` : `Server running at http://${HOST}:${bound.port}/`);
});
