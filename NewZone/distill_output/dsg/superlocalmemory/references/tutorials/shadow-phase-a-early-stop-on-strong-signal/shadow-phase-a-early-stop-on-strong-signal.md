# How To: Shadow Phase A Early Stop On Strong Signal

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Phase A (n=100) early-stops when |effect| > 0.08 AND p<0.01.

Seed a strong, low-variance lift; after Phase A's 100 pairs the
decision should be ``promote`` without waiting for Phase B.

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

### Step 1: "Phase A (n=100) early-stops when |effect| > 0.08 AND p<0.01.\n\n    Seed a strong, low-variance lift; after Phase A's 100 pairs the\n    decision should be ``promote`` without waiting for Phase B.\n    "

```python
"Phase A (n=100) early-stops when |effect| > 0.08 AND p<0.01.\n\n    Seed a strong, low-variance lift; after Phase A's 100 pairs the\n    decision should be ``promote`` without waiting for Phase B.\n    "
```

**Verification:**
```python
assert decision == 'promote', f'expected promote, got {decision} ({stats})'
```

### Step 2: Assign st = ShadowTest(...)

```python
st = ShadowTest(profile_id='p', candidate_model_id='cand-1')
```

**Verification:**
```python
assert stats.get('phase') == 'A'
```

### Step 3: Assign rng = random.Random(...)

```python
rng = random.Random(163)
```

**Verification:**
```python
assert abs(stats.get('effect', 0.0)) > 0.08
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
assert decision == 'promote', f'expected promote, got {decision} ({stats})'
```

### Step 6: Assign a = value

```python
a = 0.4 + rng.gauss(0, 0.01)
```

### Step 7: Assign c = value

```python
c = a + 0.12 + rng.gauss(0, 0.01)
```

### Step 8: Call pairs.append()

```python
pairs.append((a, c))
```


## Complete Example

```python
# Workflow
"Phase A (n=100) early-stops when |effect| > 0.08 AND p<0.01.\n\n    Seed a strong, low-variance lift; after Phase A's 100 pairs the\n    decision should be ``promote`` without waiting for Phase B.\n    "
st = ShadowTest(profile_id='p', candidate_model_id='cand-1')
rng = random.Random(163)
pairs: list[tuple[float, float]] = []
for _ in range(st.PHASE_A_N):
    a = 0.4 + rng.gauss(0, 0.01)
    c = a + 0.12 + rng.gauss(0, 0.01)
    pairs.append((a, c))
_record_pairs(st, pairs=pairs)
decision, stats = st.decide()
assert decision == 'promote', f'expected promote, got {decision} ({stats})'
assert stats.get('phase') == 'A'
assert abs(stats.get('effect', 0.0)) > 0.08
```

## Next Steps


---

*Source: test_shadow_test.py:79 | Complexity: Advanced | Last updated: 2026-05-05*