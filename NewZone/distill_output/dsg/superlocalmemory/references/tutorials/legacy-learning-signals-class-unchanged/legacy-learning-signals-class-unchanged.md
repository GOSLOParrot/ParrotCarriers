# How To: Legacy Learning Signals Class Unchanged

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: ``LearningSignals`` class is the 3.4.20 API — must still work.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `pytest`
- `lightgbm`
- `numpy`
- `superlocalmemory.learning`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.features`
- `superlocalmemory.learning.labeler`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.ranker`
- `superlocalmemory.learning.signals`
- `tests.test_learning._signal_fixtures`
- `lightgbm`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.model_cache`
- `hashlib`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.model_cache`
- `hashlib`
- `json`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: '``LearningSignals`` class is the 3.4.20 API — must still work.'

```python
'``LearningSignals`` class is the 3.4.20 API — must still work.'
```

**Verification:**
```python
assert 'co_retrieval_edges' in stats
```

### Step 2: Assign db_path = str(...)

```python
db_path = str(tmp_path / 'sig.db')
```

**Verification:**
```python
assert 0.0 <= gap <= 1.0
```

### Step 3: Assign ls = LearningSignals(...)

```python
ls = LearningSignals(db_path)
```

**Verification:**
```python
assert LearningSignals.compute_entropy_gap([], []) == 0.5
```

### Step 4: Call ls.credit_channel()

```python
ls.credit_channel('p1', 'single_hop', 'semantic', hit=True)
```

### Step 5: Call ls.credit_channel()

```python
ls.credit_channel('p1', 'single_hop', 'semantic', hit=False)
```

### Step 6: Call ls.record_co_retrieval()

```python
ls.record_co_retrieval('p1', ['a', 'b', 'c'])
```

### Step 7: Assign stats = ls.get_signal_stats(...)

```python
stats = ls.get_signal_stats('p1')
```

**Verification:**
```python
assert 'co_retrieval_edges' in stats
```

### Step 8: Assign gap = LearningSignals.compute_entropy_gap(...)

```python
gap = LearningSignals.compute_entropy_gap([1.0, 0.0], [[0.0, 1.0]])
```

**Verification:**
```python
assert 0.0 <= gap <= 1.0
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'``LearningSignals`` class is the 3.4.20 API — must still work.'
from superlocalmemory.learning.signals import LearningSignals
db_path = str(tmp_path / 'sig.db')
ls = LearningSignals(db_path)
ls.credit_channel('p1', 'single_hop', 'semantic', hit=True)
ls.credit_channel('p1', 'single_hop', 'semantic', hit=False)
ls.record_co_retrieval('p1', ['a', 'b', 'c'])
stats = ls.get_signal_stats('p1')
assert 'co_retrieval_edges' in stats
gap = LearningSignals.compute_entropy_gap([1.0, 0.0], [[0.0, 1.0]])
assert 0.0 <= gap <= 1.0
assert LearningSignals.compute_entropy_gap([], []) == 0.5
```

## Next Steps


---

*Source: test_ranker_v2.py:220 | Complexity: Advanced | Last updated: 2026-05-05*