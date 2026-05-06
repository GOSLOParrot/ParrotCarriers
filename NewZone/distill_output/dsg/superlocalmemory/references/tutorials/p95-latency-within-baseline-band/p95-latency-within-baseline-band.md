# How To: P95 Latency Within Baseline Band

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Each measured day's p95 stays under the pinned baseline band.

M-P-03: reproducibility strips p95 from bit-exact compare (defensible —
clocks drift), but without this check nothing catches a 2–3× jump
in recall p95 between retrain cycles.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `os`
- `time`
- `xml.etree.ElementTree`
- `pathlib`
- `pytest`
- `tests.test_benchmarks.evo_memory`
- `tests.test_benchmarks.chart_export`
- `sqlite3`
- `superlocalmemory.learning.ranker_retrain_legacy`
- `superlocalmemory.learning.ranker_retrain_legacy`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: "Each measured day's p95 stays under the pinned baseline band.\n\n    M-P-03: reproducibility strips p95 from bit-exact compare (defensible —\n    clocks drift), but without this check nothing catches a 2–3× jump\n    in recall p95 between retrain cycles.\n    "

```python
"Each measured day's p95 stays under the pinned baseline band.\n\n    M-P-03: reproducibility strips p95 from bit-exact compare (defensible —\n    clocks drift), but without this check nothing catches a 2–3× jump\n    in recall p95 between retrain cycles.\n    "
```

**Verification:**
```python
assert observed <= p95_cap_ms, f'day {day} p95 latency {observed:.2f} ms exceeded baseline band cap {p95_cap_ms:.2f} ms'
```

### Step 2: Assign bench = EvoMemoryBenchmark(...)

```python
bench = EvoMemoryBenchmark(profile_id='bench_v1', data_dir=tmp_path)
```

### Step 3: Assign result = bench.run_full_30_day_simulation(...)

```python
result = bench.run_full_30_day_simulation()
```

### Step 4: Assign day_metrics = value

```python
day_metrics = result['metrics'][f'day_{day}']
```

### Step 5: Assign observed = value

```python
observed = day_metrics['p95_latency_ms']
```

**Verification:**
```python
assert observed <= p95_cap_ms, f'day {day} p95 latency {observed:.2f} ms exceeded baseline band cap {p95_cap_ms:.2f} ms'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
"Each measured day's p95 stays under the pinned baseline band.\n\n    M-P-03: reproducibility strips p95 from bit-exact compare (defensible —\n    clocks drift), but without this check nothing catches a 2–3× jump\n    in recall p95 between retrain cycles.\n    "
bench = EvoMemoryBenchmark(profile_id='bench_v1', data_dir=tmp_path)
result = bench.run_full_30_day_simulation()
for day, p95_cap_ms in _P95_BASELINE_MS.items():
    day_metrics = result['metrics'][f'day_{day}']
    observed = day_metrics['p95_latency_ms']
    assert observed <= p95_cap_ms, f'day {day} p95 latency {observed:.2f} ms exceeded baseline band cap {p95_cap_ms:.2f} ms'
```

## Next Steps


---

*Source: test_evo_memory_runner.py:152 | Complexity: Intermediate | Last updated: 2026-05-05*