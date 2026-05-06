# How To: Hopfield Convergence One Step

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test hopfield convergence one step

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
assert np.argmax(similarities) == 2
```

### Step 2: Assign config = HopfieldConfig(...)

```python
config = HopfieldConfig(dimension=d)
```

### Step 3: Assign net = ModernHopfieldNetwork(...)

```python
net = ModernHopfieldNetwork(config)
```

### Step 4: Assign memory = _orthogonal_patterns(...)

```python
memory = _orthogonal_patterns(5, d)
```

### Step 5: Assign rng = np.random.default_rng(...)

```python
rng = np.random.default_rng(77)
```

### Step 6: Assign noise = value

```python
noise = rng.standard_normal(d).astype(np.float32) * 0.1
```

### Step 7: Assign query = value

```python
query = memory[2] + noise
```

### Step 8: Assign query = value

```python
query = query / np.linalg.norm(query)
```

### Step 9: Assign xi_new = net.update(...)

```python
xi_new = net.update(query.astype(np.float32), memory)
```

### Step 10: Assign similarities = value

```python
similarities = memory @ xi_new
```

**Verification:**
```python
assert np.argmax(similarities) == 2
```


## Complete Example

```python
# Workflow
from superlocalmemory.math.hopfield import HopfieldConfig, ModernHopfieldNetwork
d = 768
config = HopfieldConfig(dimension=d)
net = ModernHopfieldNetwork(config)
memory = _orthogonal_patterns(5, d)
rng = np.random.default_rng(77)
noise = rng.standard_normal(d).astype(np.float32) * 0.1
query = memory[2] + noise
query = query / np.linalg.norm(query)
xi_new = net.update(query.astype(np.float32), memory)
similarities = memory @ xi_new
assert np.argmax(similarities) == 2
```

## Next Steps


---

*Source: test_hopfield.py:149 | Complexity: Advanced | Last updated: 2026-05-05*