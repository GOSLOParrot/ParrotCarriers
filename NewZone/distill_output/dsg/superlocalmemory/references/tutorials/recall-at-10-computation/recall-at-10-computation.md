# How To: Recall At 10 Computation

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Recall@10: 2-of-3 relevant present in top-10 → 2/3.

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

### Step 1: 'Recall@10: 2-of-3 relevant present in top-10 → 2/3.'

```python
'Recall@10: 2-of-3 relevant present in top-10 → 2/3.'
```

**Verification:**
```python
assert abs(recall - 2.0 / 3.0) < 1e-09
```

### Step 2: Assign ranked = value

```python
ranked = ['r1', 'junk', 'r2', 'more_junk']
```

**Verification:**
```python
assert recall_empty == 0.0
```

### Step 3: Assign relevant = value

```python
relevant = {'r1', 'r2', 'r3'}
```

### Step 4: Assign recall = compute_recall_at_k(...)

```python
recall = compute_recall_at_k([(ranked, relevant)], k=10)
```

**Verification:**
```python
assert abs(recall - 2.0 / 3.0) < 1e-09
```

### Step 5: Assign recall_empty = compute_recall_at_k(...)

```python
recall_empty = compute_recall_at_k([(ranked, set())], k=10)
```

**Verification:**
```python
assert recall_empty == 0.0
```


## Complete Example

```python
# Workflow
'Recall@10: 2-of-3 relevant present in top-10 → 2/3.'
ranked = ['r1', 'junk', 'r2', 'more_junk']
relevant = {'r1', 'r2', 'r3'}
recall = compute_recall_at_k([(ranked, relevant)], k=10)
assert abs(recall - 2.0 / 3.0) < 1e-09
recall_empty = compute_recall_at_k([(ranked, set())], k=10)
assert recall_empty == 0.0
```

## Next Steps


---

*Source: test_evo_memory_runner.py:79 | Complexity: Intermediate | Last updated: 2026-05-05*