const test = require('node:test');
const assert = require('node:assert/strict');
require('./server.js');

// GET / returns 200 and the exact body
const getCase = test('GET / returns 200 and the exact body', async () => {
  const res = await fetch('http://127.0.0.1:3000/');
  assert.equal(res.status, 200);
  assert.deepEqual(Buffer.from(await res.arrayBuffer()), Buffer.from('Hello, World!\n'));
});

// A POST to the same path gets the identical response
const postCase = test('POST / returns the identical response', async () => {
  const res = await fetch('http://127.0.0.1:3000/', { method: 'POST' });
  assert.equal(res.status, 200);
  assert.deepEqual(Buffer.from(await res.arrayBuffer()), Buffer.from('Hello, World!\n'));
});

Promise.all([getCase, postCase]).then(() => setImmediate(() => process.exit(0)));
