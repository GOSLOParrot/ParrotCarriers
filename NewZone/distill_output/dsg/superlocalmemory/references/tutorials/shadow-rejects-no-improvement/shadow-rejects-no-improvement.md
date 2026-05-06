# How To: Shadow Rejects No Improvement

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Zero-effect (candidate == active) → reject after Phase B.

## Prerequisites

**Required Modules:**
- `__future__`
- `hashlib`
- `random`
- `typing`
- `pytest`
- `superlocalmemory.learning.shadow_test`
- `superlocalmemory.learning.shadow_test`
- `superlocalmemory.learning.shadow_test`
- `superlocalmemory.learning.shadow_test`
- `scipy.stats`


## Step-by-Step Guide

### Step 1: 'Zero-effect (candidate == active) → reject after Phase B.'

```python
'Zero-effect (candidate == active) → reject after Phase B.'
```

**Verification:**
```python
assert decision == 'reject', f'expected reject, got {decision} ({stats})'
```

### Step 2: Assign st = ShadowTest(...)

```python
st = ShadowTest(profile_id='p', candidate_model_id='cand-3')
```

### Step 3: Assign rng = random.Random(...)

```python
rng = random.Random(204)
```

### Step 4: Call _record_pairs()

```python
_record_pairs(st, pairs=pairs)
```

### Step 5: Assign unknown = st.decide(...)

```python
decision, stats = st.decide()
```

**Verification:**
```python
assert decision == 'reject', f'expected reject, got {decision} ({stats})'
```

### Step 6: Assign base = value

```python
base = 0.5 + rng.gauss(0, 0.1)
```

### Step 7: Call pairs.append()

```python
pairs.append((base, base + rng.gauss(0, 0.001)))
```


## Complete Example

```python
# Workflow
'Zero-effect (candidate == active) → reject after Phase B.'
st = ShadowTest(profile_id='p', candidate_model_id='cand-3')
rng = random.Random(204)
pairs: list[tuple[float, float]] = []
for _ in range(st.PHASE_B_N):
    base = 0.5 + rng.gauss(0, 0.1)
    pairs.append((base, base + rng.gauss(0, 0.001)))
_record_pairs(st, pairs=pairs)
decision, stats = st.decide()
assert decision == 'reject', f'expected reject, got {decision} ({stats})'
```

## Next Steps


---

*Source: test_shadow_test.py:120 | Complexity: Intermediate | Last updated: 2026-05-05*