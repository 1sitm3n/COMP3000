"""
Numen: Knightfall — H4 Latency Benchmark
=========================================

Automated test harness for H4 (Latency).

H4 claim: end-to-end median dialogue latency stays below 2000 ms,
making the system suitable for real-time interactive use.

This script:
1. Submits 500 queries per NPC (1500 total) to the FastAPI middleware.
2. Records request-submission timestamp, response-receipt timestamp,
   and computed elapsed time per query.
3. Samples system resource utilisation (GPU memory, RAM, GPU utilisation)
   every 5 seconds in a background thread for the duration of the run.
4. Computes median, mean, std, p95, p99, max latencies overall and per-NPC.
5. Writes JSON+CSV raw results, resource samples, and a Markdown summary.

H4 is supported if median end-to-end latency < 2000 ms per §5.6.

Run from the middleware directory while FastAPI + llama-server are up:
    python h4_latency_benchmark.py [--queries-per-npc N]

Default 500 per NPC takes ~30-60 minutes on RTX 4090 Laptop depending
on inference speed. Pass --queries-per-npc 50 for a smoke-test run (~5 min).

Outputs land in ./h4_results/<timestamp>/
"""

import argparse
import csv
import json
import statistics
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import httpx

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

FASTAPI_URL = "http://127.0.0.1:8000/dialogue"
REQUEST_TIMEOUT = 120.0  # generous; p99/max can be high under load

NPCS = ["initiate_joren", "squire_ren", "knight_instructor_marek"]

# Realistic-ish utterances mixing question types so the LLM faces varied prompts
# rather than the same utterance 500 times. Per-NPC sets are tier-appropriate.
QUERY_BANK = {
    "initiate_joren": [
        "Tell me about yourself.",
        "What's training like?",
        "What do you do at St Damson's?",
        "How long have you been here?",
        "Tell me about your village.",
        "What weapons do you train with?",
        "What's the daily routine?",
        "What do the squires think of you?",
        "Are you nervous about the spring exam?",
        "What's the best part of your day?",
    ],
    "squire_ren": [
        "Tell me about yourself.",
        "What's it like training squires?",
        "How are the roads around here?",
        "Tell me about the local fief.",
        "Who's currently teaching at the institute?",
        "What's the spring exam like?",
        "Why do you mentor the initiates?",
        "How did you come to be at St Damson's?",
        "What's the trouble on the Eastern Road?",
        "What can you tell me about the neighbouring lands?",
    ],
    "knight_instructor_marek": [
        "Tell me about yourself.",
        "What was your campaign service?",
        "Tell me about the Knight-Commander.",
        "What was the Conclave of Stormhold?",
        "How do the orders relate to the Crown?",
        "What's the curriculum like?",
        "Tell me about the caravan attacks.",
        "Who is currently in residence?",
        "Why did you become an instructor?",
        "What is the relationship between the three orders?",
    ],
}

RESOURCE_SAMPLE_INTERVAL_S = 5.0


# --------------------------------------------------------------------------
# Resource sampling (GPU memory, GPU utilisation, RAM)
# --------------------------------------------------------------------------

def sample_resources() -> dict:
    """
    Capture a single resource snapshot. Returns dict with timestamp and
    available metrics. Falls back gracefully if nvidia-smi isn't available
    (e.g. on a non-NVIDIA system).
    """
    snapshot = {"timestamp": time.time()}
    try:
        # nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=2.0,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Take the first GPU line
            line = result.stdout.strip().splitlines()[0]
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 4:
                snapshot["gpu_mem_used_mb"] = int(parts[0])
                snapshot["gpu_mem_total_mb"] = int(parts[1])
                snapshot["gpu_utilisation_pct"] = int(parts[2])
                snapshot["gpu_temp_c"] = int(parts[3])
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass

    # RAM via psutil if available, otherwise skip
    try:
        import psutil
        vm = psutil.virtual_memory()
        snapshot["ram_used_mb"] = vm.used // (1024 * 1024)
        snapshot["ram_total_mb"] = vm.total // (1024 * 1024)
        snapshot["ram_pct"] = vm.percent
    except ImportError:
        pass

    return snapshot


class ResourceSampler:
    """Background thread that samples resources at fixed intervals."""

    def __init__(self, interval_s: float):
        self.interval_s = interval_s
        self.samples: list[dict] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def _loop(self):
        while not self._stop.is_set():
            try:
                self.samples.append(sample_resources())
            except Exception as e:
                # Don't let sampling errors crash the benchmark
                self.samples.append({"timestamp": time.time(), "error": str(e)})
            self._stop.wait(self.interval_s)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join(timeout=self.interval_s + 1.0)


# --------------------------------------------------------------------------
# Single-query runner
# --------------------------------------------------------------------------

def run_query(client: httpx.Client, npc_id: str, utterance: str) -> dict:
    submitted_at = time.time()
    t0 = time.perf_counter()
    try:
        r = client.post(
            FASTAPI_URL,
            json={"npc_id": npc_id, "utterance": utterance},
            timeout=REQUEST_TIMEOUT,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        received_at = time.time()
        if r.status_code != 200:
            return {
                "ok": False,
                "submitted_at": submitted_at,
                "received_at": received_at,
                "elapsed_ms": elapsed_ms,
                "error": f"HTTP {r.status_code}",
                "response_chars": 0,
            }
        data = r.json()
        return {
            "ok": True,
            "submitted_at": submitted_at,
            "received_at": received_at,
            "elapsed_ms": elapsed_ms,
            "error": None,
            "response_chars": len(data.get("response", "")),
        }
    except Exception as e:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "ok": False,
            "submitted_at": submitted_at,
            "received_at": time.time(),
            "elapsed_ms": elapsed_ms,
            "error": f"{type(e).__name__}: {e}",
            "response_chars": 0,
        }


# --------------------------------------------------------------------------
# Stats
# --------------------------------------------------------------------------

def compute_stats(latencies_ms: list[float]) -> dict:
    if not latencies_ms:
        return {"count": 0}
    sorted_ms = sorted(latencies_ms)
    n = len(sorted_ms)
    return {
        "count": n,
        "mean_ms": round(statistics.mean(sorted_ms), 1),
        "median_ms": round(statistics.median(sorted_ms), 1),
        "stdev_ms": round(statistics.stdev(sorted_ms), 1) if n > 1 else 0.0,
        "min_ms": round(sorted_ms[0], 1),
        "max_ms": round(sorted_ms[-1], 1),
        "p50_ms": round(sorted_ms[n // 2], 1),
        "p90_ms": round(sorted_ms[int(n * 0.90)], 1) if n > 10 else round(sorted_ms[-1], 1),
        "p95_ms": round(sorted_ms[int(n * 0.95)], 1) if n > 20 else round(sorted_ms[-1], 1),
        "p99_ms": round(sorted_ms[int(n * 0.99)], 1) if n > 100 else round(sorted_ms[-1], 1),
    }


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries-per-npc", type=int, default=500,
                    help="Queries per NPC (default 500, smoke-test with 50)")
    args = ap.parse_args()

    n_per_npc = args.queries_per_npc
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(f"./h4_results/{timestamp}")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"H4 Latency Benchmark")
    print(f"  Queries per NPC: {n_per_npc}")
    print(f"  NPCs: {len(NPCS)}")
    print(f"  Total queries: {n_per_npc * len(NPCS)}")
    print(f"  Output: {out_dir}")
    print(f"  Targeting: {FASTAPI_URL}")
    print("-" * 70)

    # Resource sampler
    sampler = ResourceSampler(RESOURCE_SAMPLE_INTERVAL_S)

    all_results = []

    with httpx.Client() as client:
        # Health check
        try:
            health = client.post(
                FASTAPI_URL,
                json={"npc_id": NPCS[0], "utterance": "Hello."},
                timeout=10.0,
            )
            if health.status_code != 200:
                print(f"FATAL: middleware health check failed: HTTP {health.status_code}")
                sys.exit(1)
            print(f"Health check OK ({health.elapsed.total_seconds() * 1000:.0f} ms)")
        except Exception as e:
            print(f"FATAL: cannot reach {FASTAPI_URL}")
            print(f"  {type(e).__name__}: {e}")
            print("  Ensure FastAPI is running on port 8000 and llama-server on port 8080.")
            sys.exit(1)

        sampler.start()
        run_started_at = time.time()

        try:
            for npc_id in NPCS:
                queries = QUERY_BANK[npc_id]
                print(f"\n{npc_id}: {n_per_npc} queries")

                npc_started_at = time.time()
                npc_latencies = []

                for i in range(n_per_npc):
                    utterance = queries[i % len(queries)]
                    result = run_query(client, npc_id, utterance)
                    result["npc_id"] = npc_id
                    result["query_index"] = i + 1
                    result["utterance"] = utterance
                    all_results.append(result)
                    if result["ok"]:
                        npc_latencies.append(result["elapsed_ms"])

                    # Progress logging — every 50 queries
                    if (i + 1) % 50 == 0 or i == n_per_npc - 1:
                        if npc_latencies:
                            running_median = statistics.median(npc_latencies)
                            elapsed_sec = time.time() - npc_started_at
                            rate = (i + 1) / elapsed_sec
                            print(f"  [{i + 1:4d}/{n_per_npc}] "
                                  f"running median: {running_median:.0f} ms, "
                                  f"rate: {rate:.1f} q/s")

        finally:
            sampler.stop()

    run_finished_at = time.time()
    duration_sec = run_finished_at - run_started_at

    # ----------------------------------------------------------------------
    # Persist raw results
    # ----------------------------------------------------------------------

    raw_path = out_dir / "raw_results.json"
    with raw_path.open("w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    csv_path = out_dir / "raw_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["npc_id", "query_index", "utterance", "submitted_at",
                      "received_at", "elapsed_ms", "ok", "error", "response_chars"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_results:
            writer.writerow({k: r.get(k, "") for k in fieldnames})

    # Resource samples
    res_path = out_dir / "resource_samples.json"
    with res_path.open("w", encoding="utf-8") as f:
        json.dump(sampler.samples, f, indent=2)

    res_csv_path = out_dir / "resource_samples.csv"
    if sampler.samples:
        keys = sorted(set().union(*(s.keys() for s in sampler.samples)))
        with res_csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for s in sampler.samples:
                writer.writerow(s)

    # Histogram-ready single-column file (one latency per line)
    hist_path = out_dir / "latencies_ms.txt"
    with hist_path.open("w", encoding="utf-8") as f:
        for r in all_results:
            if r["ok"]:
                f.write(f"{r['elapsed_ms']:.1f}\n")

    # ----------------------------------------------------------------------
    # Compute stats
    # ----------------------------------------------------------------------

    overall_latencies = [r["elapsed_ms"] for r in all_results if r["ok"]]
    overall_stats = compute_stats(overall_latencies)

    per_npc_stats = {}
    for npc_id in NPCS:
        npc_lats = [r["elapsed_ms"] for r in all_results if r["ok"] and r["npc_id"] == npc_id]
        per_npc_stats[npc_id] = compute_stats(npc_lats)

    failures = sum(1 for r in all_results if not r["ok"])

    # ----------------------------------------------------------------------
    # Summary markdown
    # ----------------------------------------------------------------------

    lines = [
        "# H4 Latency Benchmark — Summary",
        "",
        f"Run timestamp: {timestamp}",
        f"Duration: {duration_sec:.1f} seconds ({duration_sec / 60:.1f} minutes)",
        f"Queries per NPC: {n_per_npc}",
        f"Total queries: {len(all_results)}",
        f"Successful: {len(overall_latencies)}",
        f"Failed: {failures}",
        "",
        "## Overall latency distribution (ms)",
        "",
        "| Metric | Value |",
        "| --- | --- |",
    ]
    for k, v in overall_stats.items():
        lines.append(f"| {k} | {v} |")

    h4_supported = overall_stats.get("median_ms", float("inf")) < 2000.0
    lines.extend([
        "",
        f"**H4 supported (median < 2000 ms): {'YES' if h4_supported else 'NO'}**",
        "",
        "## Per-NPC latency distribution (ms)",
        "",
        "| NPC | Count | Median | Mean | Stdev | p95 | p99 | Max |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ])
    for npc_id, s in per_npc_stats.items():
        lines.append(
            f"| {npc_id} | {s['count']} | {s['median_ms']} | "
            f"{s['mean_ms']} | {s['stdev_ms']} | {s['p95_ms']} | "
            f"{s['p99_ms']} | {s['max_ms']} |"
        )

    # Resource summary
    if sampler.samples:
        gpu_mem = [s.get("gpu_mem_used_mb") for s in sampler.samples if s.get("gpu_mem_used_mb") is not None]
        gpu_util = [s.get("gpu_utilisation_pct") for s in sampler.samples if s.get("gpu_utilisation_pct") is not None]
        ram_pct = [s.get("ram_pct") for s in sampler.samples if s.get("ram_pct") is not None]
        gpu_temp = [s.get("gpu_temp_c") for s in sampler.samples if s.get("gpu_temp_c") is not None]

        lines.extend([
            "",
            "## Resource utilisation during run",
            "",
            f"Samples: {len(sampler.samples)} (every {RESOURCE_SAMPLE_INTERVAL_S:.0f} s)",
            "",
            "| Metric | Min | Mean | Max |",
            "| --- | --- | --- | --- |",
        ])
        if gpu_mem:
            lines.append(f"| GPU memory (MB) | {min(gpu_mem)} | {statistics.mean(gpu_mem):.0f} | {max(gpu_mem)} |")
        if gpu_util:
            lines.append(f"| GPU utilisation (%) | {min(gpu_util)} | {statistics.mean(gpu_util):.1f} | {max(gpu_util)} |")
        if gpu_temp:
            lines.append(f"| GPU temperature (\u00b0C) | {min(gpu_temp)} | {statistics.mean(gpu_temp):.1f} | {max(gpu_temp)} |")
        if ram_pct:
            lines.append(f"| RAM utilisation (%) | {min(ram_pct):.1f} | {statistics.mean(ram_pct):.1f} | {max(ram_pct):.1f} |")

    summary_path = out_dir / "summary.md"
    summary_path.write_text("\n".join(lines), encoding="utf-8")

    # ----------------------------------------------------------------------
    # Final console summary
    # ----------------------------------------------------------------------

    print("\n" + "=" * 70)
    print(f"Benchmark complete in {duration_sec / 60:.1f} minutes.")
    print(f"Results in: {out_dir}")
    print()
    print(f"Total queries: {len(all_results)}  successful: {len(overall_latencies)}  failed: {failures}")
    if overall_latencies:
        print(f"Overall median: {overall_stats['median_ms']} ms")
        print(f"Overall p95:    {overall_stats['p95_ms']} ms")
        print(f"Overall p99:    {overall_stats['p99_ms']} ms")
        print(f"Overall max:    {overall_stats['max_ms']} ms")
        print(f"\nH4 supported (median < 2000 ms): {'YES' if h4_supported else 'NO'}")


if __name__ == "__main__":
    main()
