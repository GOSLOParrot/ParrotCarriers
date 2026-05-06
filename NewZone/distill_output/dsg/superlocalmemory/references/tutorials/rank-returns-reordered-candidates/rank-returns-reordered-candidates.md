# How To: Rank Returns Reordered Candidates

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test rank returns reordered candidates

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
assert len(out) == 5
```

### Step 2: Assign ranker = AdaptiveRanker(...)

```python
ranker = AdaptiveRanker(signal_count=500, active_model=model)
```

**Verification:**
```python
assert {c.fact_id for c in out} == {c.fact_id for c in candidates}
```

### Step 3: Assign candidates = value

```python
candidates = [SignalCandidate(fact_id=f'f-{i}', channel_scores={'semantic': i / 10}, cross_encoder_score=float(i)) for i in range(5)]
```

### Step 4: Assign out = ranker.rank(...)

```python
out = ranker.rank(candidates, {'query_type': 'single_hop'})
```

**Verification:**
```python
assert len(out) == 5
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
_, model = _trained_model(tmp_path)
ranker = AdaptiveRanker(signal_count=500, active_model=model)
candidates = [SignalCandidate(fact_id=f'f-{i}', channel_scores={'semantic': i / 10}, cross_encoder_score=float(i)) for i in range(5)]
out = ranker.rank(candidates, {'query_type': 'single_hop'})
assert len(out) == 5
assert {c.fact_id for c in out} == {c.fact_id for c in candidates}
```

## Next Steps


---

*Source: test_ranker_v2.py:59 | Complexity: Intermediate | Last updated: 2026-05-05*