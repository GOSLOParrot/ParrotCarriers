# How To: Never Touches User Profile Data

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Harness must refuse any profile_id other than bench_v1 AND refuse
any data_dir that points under ``~/.superlocalmemory`` — two
independent gates per LLD-14 §3 constructor contract.

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
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'Harness must refuse any profile_id other than bench_v1 AND refuse\n    any data_dir that points under ``~/.superlocalmemory`` — two\n    independent gates per LLD-14 §3 constructor contract.'

```python
'Harness must refuse any profile_id other than bench_v1 AND refuse\n    any data_dir that points under ``~/.superlocalmemory`` — two\n    independent gates per LLD-14 §3 constructor contract.'
```

**Verification:**
```python
assert user_slm.stat().st_mtime == stat_before, 'Benchmark mutated ~/.superlocalmemory — data-sacred rule broken'
```

### Step 2: Assign fake_user_dir = value

```python
fake_user_dir = tmp_path / '.superlocalmemory' / 'inside'
```

### Step 3: Call fake_user_dir.mkdir()

```python
fake_user_dir.mkdir(parents=True)
```

### Step 4: Assign user_slm = value

```python
user_slm = Path.home() / '.superlocalmemory'
```

### Step 5: Assign existed_before = user_slm.exists(...)

```python
existed_before = user_slm.exists()
```

### Step 6: Assign stat_before = value

```python
stat_before = user_slm.stat().st_mtime if existed_before else None
```

### Step 7: Assign bench = EvoMemoryBenchmark(...)

```python
bench = EvoMemoryBenchmark(profile_id='bench_v1', data_dir=tmp_path)
```

### Step 8: Call bench.seed_day_0()

```python
bench.seed_day_0()
```

### Step 9: Call bench.simulate_day()

```python
bench.simulate_day(1)
```

### Step 10: Assign _ = bench.measure_day_n(...)

```python
_ = bench.measure_day_n(1, test_queries=10)
```

### Step 11: Call EvoMemoryBenchmark()

```python
EvoMemoryBenchmark(profile_id='user_varun', data_dir=tmp_path)
```

### Step 12: Call EvoMemoryBenchmark()

```python
EvoMemoryBenchmark(profile_id='bench_v1', data_dir=fake_user_dir)
```

**Verification:**
```python
assert user_slm.stat().st_mtime == stat_before, 'Benchmark mutated ~/.superlocalmemory — data-sacred rule broken'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'Harness must refuse any profile_id other than bench_v1 AND refuse\n    any data_dir that points under ``~/.superlocalmemory`` — two\n    independent gates per LLD-14 §3 constructor contract.'
with pytest.raises(ValueError, match='bench'):
    EvoMemoryBenchmark(profile_id='user_varun', data_dir=tmp_path)
fake_user_dir = tmp_path / '.superlocalmemory' / 'inside'
fake_user_dir.mkdir(parents=True)
with pytest.raises(ValueError, match='superlocalmemory'):
    EvoMemoryBenchmark(profile_id='bench_v1', data_dir=fake_user_dir)
user_slm = Path.home() / '.superlocalmemory'
existed_before = user_slm.exists()
stat_before = user_slm.stat().st_mtime if existed_before else None
bench = EvoMemoryBenchmark(profile_id='bench_v1', data_dir=tmp_path)
bench.seed_day_0()
bench.simulate_day(1)
_ = bench.measure_day_n(1, test_queries=10)
if existed_before:
    assert user_slm.stat().st_mtime == stat_before, 'Benchmark mutated ~/.superlocalmemory — data-sacred rule broken'
```

## Next Steps


---

*Source: test_evo_memory_runner.py:329 | Complexity: Advanced | Last updated: 2026-05-05*