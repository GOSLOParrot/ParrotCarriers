# How To: Multi Iteration Convergence Early Exit

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: retrieve() with max_iterations>1 triggers convergence break.

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

### Step 1: 'retrieve() with max_iterations>1 triggers convergence break.'

```python
'retrieve() with max_iterations>1 triggers convergence break.'
```

**Verification:**
```python
assert state.converged
```

### Step 2: Assign d = 16

```python
d = 16
```

**Verification:**
```python
assert state.iterations < 10
```

### Step 3: Assign config = HopfieldConfig(...)

```python
config = HopfieldConfig(dimension=d, max_iterations=10, convergence_epsilon=0.001)
```

### Step 4: Assign net = ModernHopfieldNetwork(...)

```python
net = ModernHopfieldNetwork(config)
```

### Step 5: Assign memory = _orthogonal_patterns(...)

```python
memory = _orthogonal_patterns(3, d)
```

### Step 6: Assign query = value

```python
query = memory[1].copy() + 0.01 * np.ones(d, dtype=np.float32)
```

### Step 7: Assign query = value

```python
query = query / np.linalg.norm(query)
```

### Step 8: Assign state = net.retrieve(...)

```python
state = net.retrieve(query.astype(np.float32), memory, max_iterations=10)
```

**Verification:**
```python
assert state.converged
```


## Complete Example

```python
# Workflow
'retrieve() with max_iterations>1 triggers convergence break.'
from superlocalmemory.math.hopfield import HopfieldConfig, ModernHopfieldNetwork
d = 16
config = HopfieldConfig(dimension=d, max_iterations=10, convergence_epsilon=0.001)
net = ModernHopfieldNetwork(config)
memory = _orthogonal_patterns(3, d)
query = memory[1].copy() + 0.01 * np.ones(d, dtype=np.float32)
query = query / np.linalg.norm(query)
state = net.retrieve(query.astype(np.float32), memory, max_iterations=10)
assert state.converged
assert state.iterations < 10
```

## Next Steps


---

*Source: test_hopfield.py:311 | Complexity: Advanced | Last updated: 2026-05-05*