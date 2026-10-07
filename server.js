/

/** Starts an HTTP server on port 3000 that answers every request with "Hello, World!". */
/** Starts an HTTP server on port 3000 that answers every request with "Hello, World!". */

require('http').createServer((req,res)=>res.end('Hello, World!\n')).listen(3000,()=>console.log('Server running at http://127.0.0.1:3000/'));
