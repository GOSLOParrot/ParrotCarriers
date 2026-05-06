# How To: Initialization Scales By Alpha

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Seeds get alpha * similarity as initial activation.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `math`
- `sqlite3`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.retrieval.spreading_activation`
- `superlocalmemory.storage.schema_v32`

**Setup Required:**
```python
# Fixtures: mock_db, mock_vector_store
```

## Step-by-Step Guide

### Step 1: 'Seeds get alpha * similarity as initial activation.'

```python
'Seeds get alpha * similarity as initial activation.'
```

**Verification:**
```python
assert activations['fact_A'] == pytest.approx(2.0 * 0.9)
```

### Step 2: Assign config = SpreadingActivationConfig(...)

```python
config = SpreadingActivationConfig(enabled=True, alpha=2.0, max_iterations=0, tau_gate=0.0)
```

**Verification:**
```python
assert activations['fact_B'] == pytest.approx(2.0 * 0.5)
```

### Step 3: Assign sa = SpreadingActivation(...)

```python
sa = SpreadingActivation(mock_db, mock_vector_store, config)
```

### Step 4: Assign seeds = value

```python
seeds = [('fact_A', 0.9), ('fact_B', 0.5)]
```

### Step 5: Assign activations = sa._propagate(...)

```python
activations = sa._propagate(seeds, 'default')
```

**Verification:**
```python
assert activations['fact_A'] == pytest.approx(2.0 * 0.9)
```


## Complete Example

```python
# Setup
# Fixtures: mock_db, mock_vector_store

# Workflow
'Seeds get alpha * similarity as initial activation.'
config = SpreadingActivationConfig(enabled=True, alpha=2.0, max_iterations=0, tau_gate=0.0)
sa = SpreadingActivation(mock_db, mock_vector_store, config)
seeds = [('fact_A', 0.9), ('fact_B', 0.5)]
activations = sa._propagate(seeds, 'default')
assert activations['fact_A'] == pytest.approx(2.0 * 0.9)
assert activations['fact_B'] == pytest.approx(2.0 * 0.5)
```

## Next Steps


---

*Source: test_spreading_activation.py:108 | Complexity: Intermediate | Last updated: 2026-05-05*