# H4 Latency Benchmark — Summary

Run timestamp: 20260505_002654
Duration: 1385.4 seconds (23.1 minutes)
Queries per NPC: 500
Total queries: 1500
Successful: 1500
Failed: 0

## Overall latency distribution (ms)

| Metric | Value |
| --- | --- |
| count | 1500 |
| mean_ms | 923.5 |
| median_ms | 897.8 |
| stdev_ms | 249.2 |
| min_ms | 419.3 |
| max_ms | 4445.7 |
| p50_ms | 897.9 |
| p90_ms | 1173.6 |
| p95_ms | 1285.8 |
| p99_ms | 1729.4 |

**H4 supported (median < 2000 ms): YES**

## Per-NPC latency distribution (ms)

| NPC | Count | Median | Mean | Stdev | p95 | p99 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| initiate_joren | 500 | 798.8 | 820.5 | 190.8 | 1159.5 | 1296.2 | 1623.6 |
| squire_ren | 500 | 904.1 | 963.1 | 311.8 | 1467.9 | 2439.3 | 4445.7 |
| knight_instructor_marek | 500 | 963.3 | 987.0 | 191.6 | 1316.9 | 1686.8 | 2139.2 |

## Resource utilisation during run

Samples: 273 (every 5 s)

| Metric | Min | Mean | Max |
| --- | --- | --- | --- |
| GPU memory (MB) | 11845 | 12130 | 13093 |
| GPU utilisation (%) | 0 | 58.6 | 97 |
| GPU temperature (°C) | 51 | 75.5 | 79 |