# Performance And Load Testing

This guide defines benchmarks, provides JMeter load plans, shows how to capture latency/throughput + resource usage, and outlines profiling-driven optimization for this FastAPI stack.

## Benchmarks (Baseline Targets)

Use these as initial targets for `POST /api/v1/beta/translate` under local Docker Compose:

- Latency: p50 ≤ 120 ms, p95 ≤ 300 ms, p99 ≤ 600 ms
- Throughput: ≥ 150 requests/sec sustained for 5 minutes at ≤ 1% error rate
- Resource usage: CPU ≤ 80% average, memory growth ≤ 5% over 10 minutes, no swap thrash

Adjust after your first baseline run based on hardware and environment.

## JMeter Load Tests

### Files

- JMeter test plan: `c:\Users\galan\translator_middleware\scripts\perf\jmeter\translator_load_test.jmx`
- Payloads: `c:\Users\galan\translator_middleware\scripts\perf\jmeter\payloads.csv`

### One-Time Setup

Install JMeter and make sure `jmeter` is on your PATH.

### Run (CLI)

```powershell
.\scripts\perf\run_jmeter.ps1 `
  -TargetHost localhost `
  -Port 8000 `
  -Threads 50 `
  -RampUp 30 `
  -Duration 180 `
  -Jwt "<YOUR_JWT_TOKEN>"
```

Outputs:

- JTL results: `c:\Users\galan\translator_middleware\perf_results\results_<timestamp>.jtl`
- HTML report: `c:\Users\galan\translator_middleware\perf_results\report_<timestamp>\index.html`

### Tuning Parameters

- Increase concurrency: `-Threads 100` or higher
- Increase load duration: `-Duration 600`
- Override payload list: `-Payloads c:\path\to\payloads.csv`

## Resource Usage Sampling

Collect CPU/RAM/threads for the FastAPI process while load runs:

```powershell
.\scripts\perf\collect_metrics.ps1 -ProcessName "python" -DurationSec 300 -IntervalSec 1 -OutFile .\perf_results\resource_metrics.csv
```

If multiple Python processes exist, use `-Pid` to pin the server process:

```powershell
.\scripts\perf\collect_metrics.ps1 -Pid 12345 -DurationSec 300 -IntervalSec 1 -OutFile .\perf_results\resource_metrics.csv
```

## Profiling (FastAPI / Uvicorn)

Use these tools to identify bottlenecks after you find a latency hotspot.

### py-spy (sampling, low overhead)

```powershell
py-spy record -o .\perf_results\pyspy.svg --pid <PID>
```

### pyinstrument (request-level profiling)

```powershell
pip install pyinstrument
pyinstrument -r html -o .\perf_results\pyinstrument.html -m uvicorn app.main:app --reload
```

### Scalene (CPU + memory)

```powershell
pip install scalene
scalene --html .\perf_results\scalene.html -m uvicorn app.main:app --reload
```

## Interpreting Results

Focus on:

- p95/p99 latency and tail spikes
- Throughput stability (RPS vs. time)
- Error rate and top error types
- CPU saturation vs. memory pressure

If CPU is high and latency spikes, profile CPU hot paths.  
If memory grows, inspect caches, Redis enablement, and any unbounded lists.

## Likely Bottlenecks And Fixes (Based On Stack)

1. **Semantic mapping (OWL + PyDatalog)**  
   - Cache resolved concepts in Redis (`REDIS_ENABLED=true`).  
   - Preload ontologies on startup to avoid per-request parsing.

2. **Orchestrator / Translator path building**  
   - Keep `Orchestrator` singleton (already is) to avoid rebuilding the graph.  
   - If new protocol edges are dynamic, debounce graph rebuilds.

3. **DB roundtrips on failure logging**  
   - Batch writes for `MappingFailureLog` or reduce `MAPPING_FAILURE_MAX_FIELDS`.  
   - Move heavy logging to background tasks if not user-facing.

4. **JSON Schema validation**  
   - Cache compiled schemas or skip validation for known safe payloads.

## Suggested Next Steps After First Run

1. Share the JMeter HTML report and `resource_metrics.csv`
2. Pick the top 1-2 hotspots from profiling
3. Apply targeted optimizations and re-run the same test for comparison
