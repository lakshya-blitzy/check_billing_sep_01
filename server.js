const express = require('express');
const morgan = require('morgan');

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '127.0.0.1';
const MESSAGE = process.env.MESSAGE || 'Hello, World!\n';

const app = express();
app.use(morgan('combined'));
app.all('/{*splat}', (req, res) => res.send(MESSAGE));

// HOST is only advertised in the startup line; app.listen omits it to keep the original all-interfaces bind, and omits a callback because Express 5 would route a bind error to it instead of crashing.
app.listen(PORT).once('listening', () => console.log(`Server running at http://${HOST}:${PORT}/`));
