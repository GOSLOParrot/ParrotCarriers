# How To: Signature Nonbacktracking On Pathological Input

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test signature nonbacktracking on pathological input

## Prerequisites

**Required Modules:**
- `__future__`
- `time`
- `unicodedata`
- `pytest`
- `superlocalmemory.core`


## Step-by-Step Guide

### Step 1: Assign pathological = value

```python
pathological = ('/' + 'a' * 100) * 40
```

**Verification:**
```python
assert len(sig) == 16
```

### Step 2: Assign start = time.perf_counter(...)

```python
start = time.perf_counter()
```

**Verification:**
```python
assert elapsed < 0.5, f'took {elapsed:.3f}s'
```

### Step 3: Assign sig = ts.compute_topic_signature(...)

```python
sig = ts.compute_topic_signature(pathological)
```

### Step 4: Assign elapsed = value

```python
elapsed = time.perf_counter() - start
```

**Verification:**
```python
assert len(sig) == 16
```


## Complete Example

```python
# Workflow
pathological = ('/' + 'a' * 100) * 40
start = time.perf_counter()
sig = ts.compute_topic_signature(pathological)
elapsed = time.perf_counter() - start
assert len(sig) == 16
assert elapsed < 0.5, f'took {elapsed:.3f}s'
```

## Next Steps


---

*Source: test_topic_signature.py:111 | Complexity: Intermediate | Last updated: 2026-05-05*