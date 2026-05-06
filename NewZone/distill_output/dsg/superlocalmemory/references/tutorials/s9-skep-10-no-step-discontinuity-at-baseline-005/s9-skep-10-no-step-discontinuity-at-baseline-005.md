# How To: S9 Skep 10 No Step Discontinuity At Baseline 005

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Threshold at baseline=0.049 vs 0.050 vs 0.051 must not produce
a 20× sensitivity jump.

## Prerequisites

**Required Modules:**
- `__future__`
- `sqlite3`
- `time`
- `pytest`
- `superlocalmemory.learning`
- `superlocalmemory.learning.shadow_test`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.core`
- `superlocalmemory.core.security_primitives`
- `superlocalmemory.core.security_primitives`
- `superlocalmemory.core.security_primitives`
- `superlocalmemory.core.security_primitives`
- `superlocalmemory.evolution.llm_dispatch`
- `superlocalmemory.hooks.user_prompt_rehash_hook`


## Step-by-Step Guide

### Step 1: 'Threshold at baseline=0.049 vs 0.050 vs 0.051 must not produce\n    a 20× sensitivity jump.'

```python
'Threshold at baseline=0.049 vs 0.050 vs 0.051 must not produce\n    a 20× sensitivity jump.'
```

**Verification:**
```python
assert max(n049, n050, n051) / min(n049, n050, n051) < 3.0, f'step discontinuity at baseline=0.05: n049={n049:.4f} n050={n050:.4f} n051={n051:.4f}'
```

### Step 2: Assign n049 = needed_drop(...)

```python
n049 = needed_drop(0.049)
```

### Step 3: Assign n050 = needed_drop(...)

```python
n050 = needed_drop(0.05)
```

### Step 4: Assign n051 = needed_drop(...)

```python
n051 = needed_drop(0.051)
```

**Verification:**
```python
assert max(n049, n050, n051) / min(n049, n050, n051) < 3.0, f'step discontinuity at baseline=0.05: n049={n049:.4f} n050={n050:.4f} n051={n051:.4f}'
```

### Step 5: Assign unknown = value

```python
lo, hi = (0.0, baseline + 0.2)
```

### Step 6: Assign mid = value

```python
mid = (lo + hi) / 2.0
```

### Step 7: Assign r2 = ModelRollback(...)

```python
r2 = ModelRollback(learning_db_path=':memory:', profile_id='p', baseline_ndcg=baseline)
```

### Step 8: Call r2.record_post_promotion()

```python
r2.record_post_promotion(query_id=f'q{i}', ndcg_at_10=baseline - mid)
```

### Step 9: Assign hi = mid

```python
hi = mid
```

### Step 10: Assign lo = mid

```python
lo = mid
```


## Complete Example

```python
# Workflow
'Threshold at baseline=0.049 vs 0.050 vs 0.051 must not produce\n    a 20× sensitivity jump.'
from superlocalmemory.learning.model_rollback import ModelRollback

def needed_drop(baseline: float) -> float:
    lo, hi = (0.0, baseline + 0.2)
    for _ in range(30):
        mid = (lo + hi) / 2.0
        r2 = ModelRollback(learning_db_path=':memory:', profile_id='p', baseline_ndcg=baseline)
        for i in range(r2.WATCH_WINDOW):
            r2.record_post_promotion(query_id=f'q{i}', ndcg_at_10=baseline - mid)
        if r2.should_rollback():
            hi = mid
        else:
            lo = mid
    return hi
n049 = needed_drop(0.049)
n050 = needed_drop(0.05)
n051 = needed_drop(0.051)
assert max(n049, n050, n051) / min(n049, n050, n051) < 3.0, f'step discontinuity at baseline=0.05: n049={n049:.4f} n050={n050:.4f} n051={n051:.4f}'
```

## Next Steps


---

*Source: test_s9_w6_skeptic.py:59 | Complexity: Advanced | Last updated: 2026-05-05*