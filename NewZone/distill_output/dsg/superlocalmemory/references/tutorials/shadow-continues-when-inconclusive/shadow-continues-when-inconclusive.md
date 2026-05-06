# How To: Shadow Continues When Inconclusive

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Below PHASE_B_N with marginal effect → decide returns 'continue'.

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

### Step 1: "Below PHASE_B_N with marginal effect → decide returns 'continue'."

```python
"Below PHASE_B_N with marginal effect → decide returns 'continue'."
```

**Verification:**
```python
assert decision == 'continue', f'expected continue, got {decision} ({stats})'
```

### Step 2: Assign st = ShadowTest(...)

```python
st = ShadowTest(profile_id='p', candidate_model_id='cand-4')
```

### Step 3: Assign rng = random.Random(...)

```python
rng = random.Random(238)
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
assert decision == 'continue', f'expected continue, got {decision} ({stats})'
```

### Step 6: Assign a = value

```python
a = 0.5 + rng.gauss(0, 0.2)
```

### Step 7: Assign c = value

```python
c = a + 0.02 + rng.gauss(0, 0.2)
```

### Step 8: Call pairs.append()

```python
pairs.append((a, c))
```


## Complete Example

```python
# Workflow
"Below PHASE_B_N with marginal effect → decide returns 'continue'."
st = ShadowTest(profile_id='p', candidate_model_id='cand-4')
rng = random.Random(238)
pairs: list[tuple[float, float]] = []
for _ in range(st.PHASE_A_N):
    a = 0.5 + rng.gauss(0, 0.2)
    c = a + 0.02 + rng.gauss(0, 0.2)
    pairs.append((a, c))
_record_pairs(st, pairs=pairs)
decision, stats = st.decide()
assert decision == 'continue', f'expected continue, got {decision} ({stats})'
```

## Next Steps


---

*Source: test_shadow_test.py:133 | Complexity: Advanced | Last updated: 2026-05-05*