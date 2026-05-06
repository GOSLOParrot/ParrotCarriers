# How To: Hopfield Energy Decreases After Update

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test hopfield energy decreases after update

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
assert e_after <= e_before + 1e-09, f'Energy increased: {e_before:.6f} -> {e_after:.6f}'
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
memory = _random_patterns(10, d, seed=99)
```

### Step 5: Assign rng = np.random.default_rng(...)

```python
rng = np.random.default_rng(123)
```

### Step 6: Assign query = rng.standard_normal.astype(...)

```python
query = rng.standard_normal(d).astype(np.float32)
```

### Step 7: Assign query = value

```python
query = query / np.linalg.norm(query)
```

### Step 8: Assign e_before = net.energy(...)

```python
e_before = net.energy(query, memory)
```

### Step 9: Assign xi_new = net.update(...)

```python
xi_new = net.update(query, memory)
```

### Step 10: Assign e_after = net.energy(...)

```python
e_after = net.energy(xi_new, memory)
```

**Verification:**
```python
assert e_after <= e_before + 1e-09, f'Energy increased: {e_before:.6f} -> {e_after:.6f}'
```


## Complete Example

```python
# Workflow
from superlocalmemory.math.hopfield import HopfieldConfig, ModernHopfieldNetwork
d = 768
config = HopfieldConfig(dimension=d)
net = ModernHopfieldNetwork(config)
memory = _random_patterns(10, d, seed=99)
rng = np.random.default_rng(123)
query = rng.standard_normal(d).astype(np.float32)
query = query / np.linalg.norm(query)
e_before = net.energy(query, memory)
xi_new = net.update(query, memory)
e_after = net.energy(xi_new, memory)
assert e_after <= e_before + 1e-09, f'Energy increased: {e_before:.6f} -> {e_after:.6f}'
```

## Next Steps


---

*Source: test_hopfield.py:121 | Complexity: Advanced | Last updated: 2026-05-05*