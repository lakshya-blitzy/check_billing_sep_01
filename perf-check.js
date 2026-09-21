const http = require('http');

(async () => {
  console.log('idle memory, script process:', process.memoryUsage());
  for (const c of [1, 50]) {
    const t0 = process.hrtime.bigint();
    for (let i = 0; i < 200; i += c)
      await Promise.all(Array.from({ length: c }, () => new Promise((resolve, reject) => {
        http.get('http://127.0.0.1:3000/', (res) => {
          res.resume();
          res.on('end', () => (res.statusCode === 200 ? resolve() : reject(new Error(`unexpected status ${res.statusCode}`))));
        }).on('error', reject);
      })));
    const elapsed = Number(process.hrtime.bigint() - t0) / 1e6;
    console.log(`concurrency=${c} requests=200 elapsed=${elapsed.toFixed(3)}ms amortized_latency=${(elapsed / 200).toFixed(3)}ms throughput=${(200 / (elapsed / 1000)).toFixed(3)}req/s`);
  }
  console.log('post-load memory, script process:', process.memoryUsage());
})();
