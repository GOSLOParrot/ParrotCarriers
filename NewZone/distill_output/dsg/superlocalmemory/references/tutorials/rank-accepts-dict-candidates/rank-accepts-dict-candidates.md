# How To: Rank Accepts Dict Candidates

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test rank accepts dict candidates

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

### Step 1: Assign unknown = _trained_model(...)

```python
_, model = _trained_model(tmp_path)
```

**Verification:**
```python
assert len(out) == 2
```

### Step 2: Assign ranker = AdaptiveRanker(...)

```python
ranker = AdaptiveRanker(signal_count=500, active_model=model)
```

### Step 3: Assign dicts = value

```python
dicts = [{'fact_id': 'a', 'channel_scores': {'semantic': 0.9}}, {'fact_id': 'b', 'channel_scores': {'semantic': 0.2}}]
```

### Step 4: Assign out = ranker.rank(...)

```python
out = ranker.rank(dicts, {})
```

**Verification:**
```python
assert len(out) == 2
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
_, model = _trained_model(tmp_path)
ranker = AdaptiveRanker(signal_count=500, active_model=model)
dicts = [{'fact_id': 'a', 'channel_scores': {'semantic': 0.9}}, {'fact_id': 'b', 'channel_scores': {'semantic': 0.2}}]
out = ranker.rank(dicts, {})
assert len(out) == 2
```

## Next Steps


---

*Source: test_ranker_v2.py:103 | Complexity: Intermediate | Last updated: 2026-05-05*