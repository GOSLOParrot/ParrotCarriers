# How To: Shadow Phase B Requires 885 Pairs

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: When Phase A is inconclusive but Phase B criterion met, promote.

Set up a marginal effect (~+0.025) that does NOT trip Phase A's
0.08 early-stop. Provide 885 paired recalls. Phase B must
conclude promote.

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

### Step 1: "When Phase A is inconclusive but Phase B criterion met, promote.\n\n    Set up a marginal effect (~+0.025) that does NOT trip Phase A's\n    0.08 early-stop. Provide 885 paired recalls. Phase B must\n    conclude promote.\n    "

```python
"When Phase A is inconclusive but Phase B criterion met, promote.\n\n    Set up a marginal effect (~+0.025) that does NOT trip Phase A's\n    0.08 early-stop. Provide 885 paired recalls. Phase B must\n    conclude promote.\n    "
```

**Verification:**
```python
assert decision == 'promote', f'expected promote, got {decision} ({stats})'
```

### Step 2: Assign st = ShadowTest(...)

```python
st = ShadowTest(profile_id='p', candidate_model_id='cand-2')
```

**Verification:**
```python
assert stats.get('phase') == 'B'
```

### Step 3: Assign rng = random.Random(...)

```python
rng = random.Random(181)
```

**Verification:**
```python
assert stats.get('n_pairs', 0) >= st.PHASE_B_N
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
a = 0.45 + rng.gauss(0, 0.15)
```

### Step 7: Assign c = value

```python
c = a + 0.025 + rng.gauss(0, 0.015)
```

### Step 8: Call pairs.append()

```python
pairs.append((a, c))
```


## Complete Example

```python
# Workflow
"When Phase A is inconclusive but Phase B criterion met, promote.\n\n    Set up a marginal effect (~+0.025) that does NOT trip Phase A's\n    0.08 early-stop. Provide 885 paired recalls. Phase B must\n    conclude promote.\n    "
st = ShadowTest(profile_id='p', candidate_model_id='cand-2')
rng = random.Random(181)
pairs: list[tuple[float, float]] = []
for _ in range(st.PHASE_B_N):
    a = 0.45 + rng.gauss(0, 0.15)
    c = a + 0.025 + rng.gauss(0, 0.015)
    pairs.append((a, c))
_record_pairs(st, pairs=pairs)
decision, stats = st.decide()
assert decision == 'promote', f'expected promote, got {decision} ({stats})'
assert stats.get('phase') == 'B'
assert stats.get('n_pairs', 0) >= st.PHASE_B_N
```

## Next Steps


---

*Source: test_shadow_test.py:99 | Complexity: Advanced | Last updated: 2026-05-05*