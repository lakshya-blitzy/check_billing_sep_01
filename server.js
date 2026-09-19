const express = require('express');
const app = express();
app.get('/',(req,res)=>res.send('Hello, World!\n'));
app.get('/good-evening',(req,res)=>res.type('text/plain').send('Good evening\n'));
app.listen(3000).on('listening',()=>console.log('Server running at http://127.0.0.1:3000/'));
