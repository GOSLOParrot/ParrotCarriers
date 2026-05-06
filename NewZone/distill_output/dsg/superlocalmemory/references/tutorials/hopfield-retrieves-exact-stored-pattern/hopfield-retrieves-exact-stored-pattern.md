# How To: Hopfield Retrieves Exact Stored Pattern

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test hopfield retrieves exact stored pattern

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
assert np.argmax(attention) == 7
```

### Step 2: Assign config = HopfieldConfig(...)

```python
config = HopfieldConfig(dimension=d)
```

**Verification:**
```python
assert np.argmax(state.retrieved_pattern) == 7
```

### Step 3: Assign net = ModernHopfieldNetwork(...)

```python
net = ModernHopfieldNetwork(config)
```

**Verification:**
```python
assert state.retrieved_pattern[7] > state.retrieved_pattern[0]
```

### Step 4: Assign memory = _orthogonal_patterns(...)

```python
memory = _orthogonal_patterns(20, d)
```

### Step 5: Assign query = unknown.copy(...)

```python
query = memory[7].copy()
```

### Step 6: Assign attention = net.attention_scores(...)

```python
attention = net.attention_scores(query, memory)
```

**Verification:**
```python
assert np.argmax(attention) == 7
```

### Step 7: Assign state = net.retrieve(...)

```python
state = net.retrieve(query, memory)
```

**Verification:**
```python
assert np.argmax(state.retrieved_pattern) == 7
```


## Complete Example

```python
# Workflow
from superlocalmemory.math.hopfield import HopfieldConfig, ModernHopfieldNetwork
d = 768
config = HopfieldConfig(dimension=d)
net = ModernHopfieldNetwork(config)
memory = _orthogonal_patterns(20, d)
query = memory[7].copy()
attention = net.attention_scores(query, memory)
assert np.argmax(attention) == 7
state = net.retrieve(query, memory)
assert np.argmax(state.retrieved_pattern) == 7
assert state.retrieved_pattern[7] > state.retrieved_pattern[0]
```

## Next Steps


---

*Source: test_hopfield.py:182 | Complexity: Intermediate | Last updated: 2026-05-05*