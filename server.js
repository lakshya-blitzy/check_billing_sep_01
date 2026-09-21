require('http').createServer((req,res)=>{
if(req.url==='/status'){
res.writeHead(200,{'Content-Type':'application/json'});
return res.end('{"status":"ok"}');
}
res.end('Hello, World!\n');
}).listen(3000,()=>console.log('Server running at http://127.0.0.1:3000/'));
