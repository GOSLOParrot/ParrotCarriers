# How To: Hopfield Capacity 100 Patterns

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test hopfield capacity 100 patterns

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `numpy`
- `pytest`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.math.hopfield`
- `superlocalmemory.math.hopfield`


## Step-by-Step Guide

### Step 1: Assign d = 768

```python
d = 768
```

**Verification:**
```python
assert correct >= 95, f'Only {correct}/100 correct (need >= 95)'
```

### Step 2: Assign config = HopfieldConfig(...)

```python
config = HopfieldConfig(dimension=d)
```

### Step 3: Assign net = ModernHopfieldNetwork(...)

```python
net = ModernHopfieldNetwork(config)
```

### Step 4: Assign memory = _random_patterns(...)

```python
memory = _random_patterns(100, d, seed=11)
```

### Step 5: Assign correct = 0

```python
correct = 0
```

**Verification:**
```python
assert correct >= 95, f'Only {correct}/100 correct (need >= 95)'
```

### Step 6: Assign rng = np.random.default_rng(...)

```python
rng = np.random.default_rng(1000 + idx)
```

### Step 7: Assign noise = value

```python
noise = rng.standard_normal(d).astype(np.float32) * 0.1
```

### Step 8: Assign query = value

```python
query = memory[idx] + noise
```

### Step 9: Assign query = value

```python
query = query / np.linalg.norm(query)
```

### Step 10: Assign attention = net.attention_scores(...)

```python
attention = net.attention_scores(query.astype(np.float32), memory)
```


## Complete Example

```python
# Workflow
from superlocalmemory.math.hopfield import HopfieldConfig, ModernHopfieldNetwork
d = 768
config = HopfieldConfig(dimension=d)
net = ModernHopfieldNetwork(config)
memory = _random_patterns(100, d, seed=11)
correct = 0
for idx in range(100):
    rng = np.random.default_rng(1000 + idx)
    noise = rng.standard_normal(d).astype(np.float32) * 0.1
    query = memory[idx] + noise
    query = query / np.linalg.norm(query)
    attention = net.attention_scores(query.astype(np.float32), memory)
    if np.argmax(attention) == idx:
        correct += 1
assert correct >= 95, f'Only {correct}/100 correct (need >= 95)'
```

## Next Steps


---

*Source: test_hopfield.py:257 | Complexity: Advanced | Last updated: 2026-05-05*