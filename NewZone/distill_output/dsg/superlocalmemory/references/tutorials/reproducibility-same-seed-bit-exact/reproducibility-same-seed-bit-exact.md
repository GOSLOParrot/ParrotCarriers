# How To: Reproducibility Same Seed Bit Exact

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Two identical runs produce byte-identical result JSON (minus clock).

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

### Step 1: 'Two identical runs produce byte-identical result JSON (minus clock).'

```python
'Two identical runs produce byte-identical result JSON (minus clock).'
```

**Verification:**
```python
assert results[0] == results[1], 'Benchmark is not bit-exact across runs — reproducibility violated.'
```

### Step 2: Assign run_dirs = value

```python
run_dirs = [tmp_path / 'r1', tmp_path / 'r2']
```

### Step 3: Assign results = value

```python
results = []
```

**Verification:**
```python
assert results[0] == results[1], 'Benchmark is not bit-exact across runs — reproducibility violated.'
```

### Step 4: Call d.mkdir()

```python
d.mkdir()
```

### Step 5: Assign bench = EvoMemoryBenchmark(...)

```python
bench = EvoMemoryBenchmark(profile_id='bench_v1', data_dir=d)
```

### Step 6: Assign res = bench.run_full_30_day_simulation(...)

```python
res = bench.run_full_30_day_simulation()
```

### Step 7: Call results.append()

```python
results.append(res)
```

### Step 8: Call res.pop()

```python
res.pop(drop, None)
```

### Step 9: Call day_metrics.pop()

```python
day_metrics.pop('p95_latency_ms', None)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Two identical runs produce byte-identical result JSON (minus clock).'
run_dirs = [tmp_path / 'r1', tmp_path / 'r2']
results = []
for d in run_dirs:
    d.mkdir()
    bench = EvoMemoryBenchmark(profile_id='bench_v1', data_dir=d)
    res = bench.run_full_30_day_simulation()
    for drop in ('ran_at_iso', 'wall_seconds'):
        res.pop(drop, None)
    for day_key, day_metrics in res.get('metrics', {}).items():
        day_metrics.pop('p95_latency_ms', None)
    results.append(res)
assert results[0] == results[1], 'Benchmark is not bit-exact across runs — reproducibility violated.'
```

## Next Steps


---

*Source: test_evo_memory_runner.py:107 | Complexity: Advanced | Last updated: 2026-05-05*