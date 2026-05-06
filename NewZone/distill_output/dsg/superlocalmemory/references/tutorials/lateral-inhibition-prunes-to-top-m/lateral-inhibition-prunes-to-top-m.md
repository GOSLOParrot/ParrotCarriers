# How To: Lateral Inhibition Prunes To Top M

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: More than top_m nodes get pruned to top_m.

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

### Step 1: 'More than top_m nodes get pruned to top_m.'

```python
'More than top_m nodes get pruned to top_m.'
```

**Verification:**
```python
assert len(activations) <= 3
```

### Step 2: Assign config = SpreadingActivationConfig(...)

```python
config = SpreadingActivationConfig(enabled=True, top_m=3, max_iterations=1, tau_gate=0.0)
```

### Step 3: Assign sa = SpreadingActivation(...)

```python
sa = SpreadingActivation(mock_db, mock_vector_store, config)
```

### Step 4: Assign seeds = value

```python
seeds = [('f1', 0.9), ('f2', 0.8), ('f3', 0.7), ('f4', 0.6), ('f5', 0.5)]
```

### Step 5: Assign activations = sa._propagate(...)

```python
activations = sa._propagate(seeds, 'default')
```

**Verification:**
```python
assert len(activations) <= 3
```


## Complete Example

```python
# Setup
# Fixtures: mock_db, mock_vector_store

# Workflow
'More than top_m nodes get pruned to top_m.'
config = SpreadingActivationConfig(enabled=True, top_m=3, max_iterations=1, tau_gate=0.0)
sa = SpreadingActivation(mock_db, mock_vector_store, config)
seeds = [('f1', 0.9), ('f2', 0.8), ('f3', 0.7), ('f4', 0.6), ('f5', 0.5)]
activations = sa._propagate(seeds, 'default')
assert len(activations) <= 3
```

## Next Steps


---

*Source: test_spreading_activation.py:151 | Complexity: Intermediate | Last updated: 2026-05-05*