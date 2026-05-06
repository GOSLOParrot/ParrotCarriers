# How To: Temporal Scaling Reduces Severity

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Temporal restriction (0.6*I) should reduce effective severity
compared to identity restriction.

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `dataclasses`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.math.sheaf`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'Temporal restriction (0.6*I) should reduce effective severity\n        compared to identity restriction.'

```python
'Temporal restriction (0.6*I) should reduce effective severity\n        compared to identity restriction.'
```

### Step 2: Assign emb_a = np.array(...)

```python
emb_a = np.array([1.0, 0.0, 0.0])
```

### Step 3: Assign emb_b = np.array(...)

```python
emb_b = np.array([0.0, 1.0, 0.0])
```

### Step 4: Assign R_id = np.eye(...)

```python
R_id = np.eye(3)
```

### Step 5: Assign R_temp = value

```python
R_temp = TEMPORAL_TOLERANCE * np.eye(3)
```

### Step 6: Assign sev_entity = coboundary_norm(...)

```python
sev_entity = coboundary_norm(emb_a, emb_b, R_id, R_id)
```

### Step 7: Assign sev_temporal = coboundary_norm(...)

```python
sev_temporal = coboundary_norm(emb_a, emb_b, R_temp, R_temp)
```

### Step 8: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(sev_entity, sev_temporal, atol=1e-08)
```


## Complete Example

```python
# Workflow
'Temporal restriction (0.6*I) should reduce effective severity\n        compared to identity restriction.'
emb_a = np.array([1.0, 0.0, 0.0])
emb_b = np.array([0.0, 1.0, 0.0])
R_id = np.eye(3)
R_temp = TEMPORAL_TOLERANCE * np.eye(3)
sev_entity = coboundary_norm(emb_a, emb_b, R_id, R_id)
sev_temporal = coboundary_norm(emb_a, emb_b, R_temp, R_temp)
np.testing.assert_allclose(sev_entity, sev_temporal, atol=1e-08)
```

## Next Steps


---

*Source: test_sheaf.py:147 | Complexity: Advanced | Last updated: 2026-05-05*