# How To: Rank With Unknown Drift Falls Back

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test rank with unknown drift falls back

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
_, good_model = _trained_model(tmp_path)
```

**Verification:**
```python
assert [c.fact_id for c in out] == ['f-0', 'f-1', 'f-2']
```

### Step 2: Assign drifted = ActiveModel(...)

```python
drifted = ActiveModel(profile_id=good_model.profile_id, booster=good_model.booster, feature_names=tuple(FEATURE_NAMES) + ('mystery',), trained_at=good_model.trained_at, sha256=good_model.sha256)
```

### Step 3: Assign ranker = AdaptiveRanker(...)

```python
ranker = AdaptiveRanker(signal_count=500, active_model=drifted)
```

### Step 4: Assign cands = value

```python
cands = [SignalCandidate(fact_id=f'f-{i}') for i in range(3)]
```

### Step 5: Assign out = ranker.rank(...)

```python
out = ranker.rank(cands, {})
```

**Verification:**
```python
assert [c.fact_id for c in out] == ['f-0', 'f-1', 'f-2']
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
_, good_model = _trained_model(tmp_path)
drifted = ActiveModel(profile_id=good_model.profile_id, booster=good_model.booster, feature_names=tuple(FEATURE_NAMES) + ('mystery',), trained_at=good_model.trained_at, sha256=good_model.sha256)
ranker = AdaptiveRanker(signal_count=500, active_model=drifted)
cands = [SignalCandidate(fact_id=f'f-{i}') for i in range(3)]
out = ranker.rank(cands, {})
assert [c.fact_id for c in out] == ['f-0', 'f-1', 'f-2']
```

## Next Steps


---

*Source: test_ranker_v2.py:86 | Complexity: Intermediate | Last updated: 2026-05-05*