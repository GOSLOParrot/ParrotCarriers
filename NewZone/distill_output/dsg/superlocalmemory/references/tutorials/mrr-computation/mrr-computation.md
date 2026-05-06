# How To: Mrr Computation

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: MRR@10: relevant at rank 3 → 1/3; no-relevant → 0; ties broken.

## Prerequisites

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


## Step-by-Step Guide

### Step 1: 'MRR@10: relevant at rank 3 → 1/3; no-relevant → 0; ties broken.'

```python
'MRR@10: relevant at rank 3 → 1/3; no-relevant → 0; ties broken.'
```

**Verification:**
```python
assert abs(mrr - 1.0 / 3.0) < 1e-09
```

### Step 2: Assign ranked = value

```python
ranked = ['a', 'b', 'relevant', 'c', 'd']
```

**Verification:**
```python
assert mrr_zero == 0.0
```

### Step 3: Assign relevant = value

```python
relevant = {'relevant'}
```

**Verification:**
```python
assert abs(mrr_mean - 0.75) < 1e-09
```

### Step 4: Assign mrr = compute_mrr_at_k(...)

```python
mrr = compute_mrr_at_k([(ranked, relevant)], k=10)
```

**Verification:**
```python
assert abs(mrr - 1.0 / 3.0) < 1e-09
```

### Step 5: Assign mrr_zero = compute_mrr_at_k(...)

```python
mrr_zero = compute_mrr_at_k([(ranked[:2], {'missing'})], k=10)
```

**Verification:**
```python
assert mrr_zero == 0.0
```

### Step 6: Assign mrr_mean = compute_mrr_at_k(...)

```python
mrr_mean = compute_mrr_at_k([(['x'], {'x'}), (['y', 'z'], {'z'})], k=10)
```

**Verification:**
```python
assert abs(mrr_mean - 0.75) < 1e-09
```


## Complete Example

```python
# Workflow
'MRR@10: relevant at rank 3 → 1/3; no-relevant → 0; ties broken.'
ranked = ['a', 'b', 'relevant', 'c', 'd']
relevant = {'relevant'}
mrr = compute_mrr_at_k([(ranked, relevant)], k=10)
assert abs(mrr - 1.0 / 3.0) < 1e-09
mrr_zero = compute_mrr_at_k([(ranked[:2], {'missing'})], k=10)
assert mrr_zero == 0.0
mrr_mean = compute_mrr_at_k([(['x'], {'x'}), (['y', 'z'], {'z'})], k=10)
assert abs(mrr_mean - 0.75) < 1e-09
```

## Next Steps


---

*Source: test_evo_memory_runner.py:60 | Complexity: Intermediate | Last updated: 2026-05-05*