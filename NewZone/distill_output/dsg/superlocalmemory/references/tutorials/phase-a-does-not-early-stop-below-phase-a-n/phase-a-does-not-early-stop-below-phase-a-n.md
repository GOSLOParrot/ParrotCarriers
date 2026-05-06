# How To: Phase A Does Not Early Stop Below Phase A N

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Phase A requires n_pairs ≥ PHASE_A_N (100). At n=50 (well below),
even a huge lift returns 'continue' — accumulating more data, not
firing on noise.

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

### Step 1: "Phase A requires n_pairs ≥ PHASE_A_N (100). At n=50 (well below),\n    even a huge lift returns 'continue' — accumulating more data, not\n    firing on noise.\n    "

```python
"Phase A requires n_pairs ≥ PHASE_A_N (100). At n=50 (well below),\n    even a huge lift returns 'continue' — accumulating more data, not\n    firing on noise.\n    "
```

**Verification:**
```python
assert decision == 'continue'
```

### Step 2: Assign st = ShadowTest(...)

```python
st = ShadowTest(profile_id='p', candidate_model_id='cand-small-n')
```

**Verification:**
```python
assert stats['phase'] == 'A'
```

### Step 3: Assign rng = random.Random(...)

```python
rng = random.Random(167)
```

### Step 4: Assign pairs = value

```python
pairs = []
```

### Step 5: Call _record_pairs()

```python
_record_pairs(st, pairs=pairs)
```

### Step 6: Assign unknown = st.decide(...)

```python
decision, stats = st.decide()
```

**Verification:**
```python
assert decision == 'continue'
```

### Step 7: Assign a = value

```python
a = 0.4 + rng.gauss(0, 0.01)
```

### Step 8: Assign c = value

```python
c = a + 0.12 + rng.gauss(0, 0.01)
```

### Step 9: Call pairs.append()

```python
pairs.append((a, c))
```


## Complete Example

```python
# Workflow
"Phase A requires n_pairs ≥ PHASE_A_N (100). At n=50 (well below),\n    even a huge lift returns 'continue' — accumulating more data, not\n    firing on noise.\n    "
st = ShadowTest(profile_id='p', candidate_model_id='cand-small-n')
rng = random.Random(167)
pairs = []
for _ in range(50):
    a = 0.4 + rng.gauss(0, 0.01)
    c = a + 0.12 + rng.gauss(0, 0.01)
    pairs.append((a, c))
_record_pairs(st, pairs=pairs)
decision, stats = st.decide()
assert decision == 'continue'
assert stats['phase'] == 'A'
```

## Next Steps


---

*Source: test_shadow_test.py:276 | Complexity: Advanced | Last updated: 2026-05-05*