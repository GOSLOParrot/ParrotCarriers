# How To: Sigmoid Gating Applies Threshold

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Sigmoid(u - theta) transforms raw activation.

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `sqlite3`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.retrieval.spreading_activation`
- `superlocalmemory.storage.schema_v32`


## Step-by-Step Guide

### Step 1: 'Sigmoid(u - theta) transforms raw activation.'

```python
'Sigmoid(u - theta) transforms raw activation.'
```

**Verification:**
```python
assert expected == pytest.approx(0.6224593, rel=0.0001)
```

### Step 2: Assign theta = 0.5

```python
theta = 0.5
```

**Verification:**
```python
assert expected_low < 0.5
```

### Step 3: Assign raw = 1.0

```python
raw = 1.0
```

### Step 4: Assign expected = value

```python
expected = 1.0 / (1.0 + math.exp(-(raw - theta)))
```

**Verification:**
```python
assert expected == pytest.approx(0.6224593, rel=0.0001)
```

### Step 5: Assign raw_low = 0.0

```python
raw_low = 0.0
```

### Step 6: Assign expected_low = value

```python
expected_low = 1.0 / (1.0 + math.exp(-(raw_low - theta)))
```

**Verification:**
```python
assert expected_low < 0.5
```


## Complete Example

```python
# Workflow
'Sigmoid(u - theta) transforms raw activation.'
theta = 0.5
raw = 1.0
expected = 1.0 / (1.0 + math.exp(-(raw - theta)))
assert expected == pytest.approx(0.6224593, rel=0.0001)
raw_low = 0.0
expected_low = 1.0 / (1.0 + math.exp(-(raw_low - theta)))
assert expected_low < 0.5
```

## Next Steps


---

*Source: test_spreading_activation.py:163 | Complexity: Intermediate | Last updated: 2026-05-05*