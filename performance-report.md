# Performance check: hello-world HTTP server

I measured this repository's hello-world HTTP server (`server.js`, which answers every request with a fixed `Hello, World!\n` body on hardcoded port 3000) from the outside, driving it over TCP from a separate client process at `127.0.0.1:3000`: 200 requests at each of two concurrency levels, dispatched in `Promise.all` waves of the level's width and timed with `process.hrtime.bigint()`. Every figure below is quoted from that one run's console output, and nothing here comes from anywhere else.

At concurrency 1, where the 200 requests are strictly serial, the batch took elapsed 36.280ms at amortized_latency 0.181ms and throughput 5512.752req/s. Because no two requests overlap at this level, that 0.181ms is a genuine mean per-request latency.

At concurrency 50 the batch took elapsed 33.366ms at amortized_latency 0.167ms and throughput 5994.191req/s. That 0.167ms is not a per-request latency here but the reciprocal of throughput, i.e. mean amortized service time; this run produced no per-request latency statistic at this level and none is inferred. What can be said about the waves is the mean wave makespan, 33.366ms / 4 waves (200 requests / 50 per wave) = 8.3415ms, which each wave's slowest request sets and which is therefore an upper bound on the typical request rather than a measurement of it.

The throughput ratio between the two levels is 5994.191 / 5512.752 = 1.087. So raising the number of in-flight requests fiftyfold bought under a tenth more throughput: across these two levels the achieved rate is close to flat, and the batch is plainly not gated by how many requests are in flight. This run does not localise what does set that rate, and the numbers cannot be read as the server saturating, because they are a lower bound on its capacity rather than its ceiling; the flatness is equally consistent with the server being the limiter and with the measuring client being it.

Memory, for the measuring script's own process and not the server's: at idle, before any request, rss 47292416, heapTotal 5611520, heapUsed 4442464, external 1690124, arrayBuffers 10767 bytes; after the load batch, rss 56619008, heapTotal 10067968, heapUsed 6305352, external 1704286, arrayBuffers 23753 bytes. The server's memory was not measured at all, since `process.memoryUsage()` reports only the process that calls it.

Limits worth holding in mind while reading the above:
- First-request JIT warm-up may inflate the slowest sample, which lands in the serial batch and raises its mean, so read the serial figure as slightly pessimistic; it is reported, not discarded.
- A co-resident client competes with the server for CPU, both being single-threaded Node processes on the same host, so no throughput figure is attributable to the server alone.
- Keep-alive socket reuse shapes the achieved concurrency: the default agent keeps connections alive, so only the first wave pays TCP handshake cost and later waves reuse warm sockets.
- The `Promise.all` wave barrier gates each wave on its slowest request, which makes the throughput figures a lower bound on what the server can sustain rather than its ceiling.
- This is a single, unrepeated run, with no trial-to-trial variance characterised and no percentile computed, so no figure here should be treated as a stable value.
- The memory figures are the script's process; the server's own memory is not measured.

Suggestions for future investigation, not findings: per-request percentiles, a wider concurrency sweep, repeated trials, server-side instrumentation, and CPU or GC data.
