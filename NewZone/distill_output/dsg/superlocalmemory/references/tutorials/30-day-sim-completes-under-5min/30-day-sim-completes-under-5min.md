# How To: 30 Day Sim Completes Under 5Min

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Full 30-day simulation must finish under MAX_WALL_SECONDS=300.

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

### Step 1: 'Full 30-day simulation must finish under MAX_WALL_SECONDS=300.'

```python
'Full 30-day simulation must finish under MAX_WALL_SECONDS=300.'
```

**Verification:**
```python
assert wall < 300.0, f'30-day sim took {wall:.1f}s > 300s budget'
```

### Step 2: Assign bench = EvoMemoryBenchmark(...)

```python
bench = EvoMemoryBenchmark(profile_id='bench_v1', data_dir=tmp_path)
```

**Verification:**
```python
assert result['wall_seconds'] < 300.0
```

### Step 3: Assign t0 = time.perf_counter(...)

```python
t0 = time.perf_counter()
```

**Verification:**
```python
assert result['days_measured'] == [1, 7, 14, 30]
```

### Step 4: Assign result = bench.run_full_30_day_simulation(...)

```python
result = bench.run_full_30_day_simulation()
```

**Verification:**
```python
assert 'comparison' in result
```

### Step 5: Assign wall = value

```python
wall = time.perf_counter() - t0
```

**Verification:**
```python
assert wall < 300.0, f'30-day sim took {wall:.1f}s > 300s budget'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Full 30-day simulation must finish under MAX_WALL_SECONDS=300.'
bench = EvoMemoryBenchmark(profile_id='bench_v1', data_dir=tmp_path)
t0 = time.perf_counter()
result = bench.run_full_30_day_simulation()
wall = time.perf_counter() - t0
assert wall < 300.0, f'30-day sim took {wall:.1f}s > 300s budget'
assert result['wall_seconds'] < 300.0
assert result['days_measured'] == [1, 7, 14, 30]
assert 'comparison' in result
```

## Next Steps


---

*Source: test_evo_memory_runner.py:91 | Complexity: Intermediate | Last updated: 2026-05-05*