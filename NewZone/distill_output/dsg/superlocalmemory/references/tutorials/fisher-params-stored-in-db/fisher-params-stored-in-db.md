# How To: Fisher Params Stored In Db

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Fisher mean and variance should be persisted for stored facts.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `json`
- `sys`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.storage.models`
- `superlocalmemory.math.sheaf`
- `superlocalmemory.math.langevin`
- `superlocalmemory.math.langevin`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: loaded_engine
```

## Step-by-Step Guide

### Step 1: 'Fisher mean and variance should be persisted for stored facts.'

```python
'Fisher mean and variance should be persisted for stored facts.'
```

**Verification:**
```python
assert len(rows) > 0, 'DO NOT SHIP: No facts have Fisher params in DB'
```

### Step 2: Assign rows = loaded_engine._db.execute(...)

```python
rows = loaded_engine._db.execute("SELECT fisher_mean, fisher_variance FROM atomic_facts WHERE profile_id = 'default' AND fisher_mean IS NOT NULL AND fisher_variance IS NOT NULL LIMIT 1")
```

**Verification:**
```python
assert len(fisher_mean) == 768, f'Fisher mean dimension {len(fisher_mean)} != 768'
```

### Step 3: Assign d = dict(...)

```python
d = dict(rows[0])
```

**Verification:**
```python
assert len(fisher_variance) == 768, f'Fisher variance dimension {len(fisher_variance)} != 768'
```

### Step 4: Assign fisher_mean = json.loads(...)

```python
fisher_mean = json.loads(d['fisher_mean'])
```

**Verification:**
```python
assert var_arr.std() > 0.01, 'Fisher variance is nearly uniform — content-derived variance not working'
```

### Step 5: Assign fisher_variance = json.loads(...)

```python
fisher_variance = json.loads(d['fisher_variance'])
```

**Verification:**
```python
assert len(fisher_mean) == 768, f'Fisher mean dimension {len(fisher_mean)} != 768'
```

### Step 6: Assign var_arr = np.array(...)

```python
var_arr = np.array(fisher_variance)
```

**Verification:**
```python
assert var_arr.std() > 0.01, 'Fisher variance is nearly uniform — content-derived variance not working'
```


## Complete Example

```python
# Setup
# Fixtures: loaded_engine

# Workflow
'Fisher mean and variance should be persisted for stored facts.'
rows = loaded_engine._db.execute("SELECT fisher_mean, fisher_variance FROM atomic_facts WHERE profile_id = 'default' AND fisher_mean IS NOT NULL AND fisher_variance IS NOT NULL LIMIT 1")
assert len(rows) > 0, 'DO NOT SHIP: No facts have Fisher params in DB'
d = dict(rows[0])
fisher_mean = json.loads(d['fisher_mean'])
fisher_variance = json.loads(d['fisher_variance'])
assert len(fisher_mean) == 768, f'Fisher mean dimension {len(fisher_mean)} != 768'
assert len(fisher_variance) == 768, f'Fisher variance dimension {len(fisher_variance)} != 768'
var_arr = np.array(fisher_variance)
assert var_arr.std() > 0.01, 'Fisher variance is nearly uniform — content-derived variance not working'
```

## Next Steps


---

*Source: test_final_locomo_mini.py:516 | Complexity: Intermediate | Last updated: 2026-05-05*