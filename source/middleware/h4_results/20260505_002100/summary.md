# H4 Latency Benchmark — Summary

Run timestamp: 20260505_002100
Duration: 114.7 seconds (1.9 minutes)
Queries per NPC: 50
Total queries: 150
Successful: 150
Failed: 0

## Overall latency distribution (ms)

| Metric | Value |
| --- | --- |
| count | 150 |
| mean_ms | 764.9 |
| median_ms | 755.2 |
| stdev_ms | 155.8 |
| min_ms | 437.4 |
| max_ms | 1311.5 |
| p50_ms | 758.0 |
| p90_ms | 964.8 |
| p95_ms | 1049.8 |
| p99_ms | 1146.7 |

**H4 supported (median < 2000 ms): YES**

## Per-NPC latency distribution (ms)

| NPC | Count | Median | Mean | Stdev | p95 | p99 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| initiate_joren | 50 | 650.7 | 647.5 | 103.5 | 811.4 | 822.3 | 822.3 |
| squire_ren | 50 | 825.0 | 839.8 | 134.2 | 1081.7 | 1146.7 | 1146.7 |
| knight_instructor_marek | 50 | 831.4 | 807.3 | 153.2 | 977.4 | 1311.5 | 1311.5 |

## Resource utilisation during run

Samples: 23 (every 5 s)

| Metric | Min | Mean | Max |
| --- | --- | --- | --- |
| GPU memory (MB) | 11776 | 11852 | 11893 |
| GPU utilisation (%) | 0 | 82.9 | 97 |
| GPU temperature (°C) | 50 | 69.2 | 77 |