# How To: Monotonically Decreasing

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test monotonically decreasing

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `datetime`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.retrieval.temporal_channel`
- `datetime`


## Step-by-Step Guide

### Step 1: Assign q = datetime(...)

```python
q = datetime(2026, 3, 11)
```

**Verification:**
```python
assert scores[i] >= scores[i + 1]
```

### Step 2: Assign scores = value

```python
scores = []
```

### Step 3: Assign e = datetime(...)

```python
e = datetime(2026, 3, 11 - min(days, 10))
```

**Verification:**
```python
assert scores[i] >= scores[i + 1]
```

### Step 4: Assign e = value

```python
e = q - timedelta(days=days)
```

### Step 5: Call scores.append()

```python
scores.append(_proximity_score(q, e))
```


## Complete Example

```python
# Workflow
q = datetime(2026, 3, 11)
scores = []
for days in [0, 10, 30, 60, 90, 180]:
    e = datetime(2026, 3, 11 - min(days, 10))
    if days <= 10:
        from datetime import timedelta
        e = q - timedelta(days=days)
        scores.append(_proximity_score(q, e))
for i in range(len(scores) - 1):
    assert scores[i] >= scores[i + 1]
```

## Next Steps


---

*Source: test_temporal_channel.py:81 | Complexity: Intermediate | Last updated: 2026-05-05*