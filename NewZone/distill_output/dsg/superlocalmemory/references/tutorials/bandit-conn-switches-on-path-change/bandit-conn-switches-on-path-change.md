# How To: Bandit Conn Switches On Path Change

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test bandit conn switches on path change

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `threading`
- `time`
- `dataclasses`
- `datetime`
- `pathlib`
- `typing`
- `pytest`
- `superlocalmemory.learning.arm_catalog`
- `superlocalmemory.learning.bandit`
- `superlocalmemory.learning.bandit_cache`
- `superlocalmemory.learning.ensemble`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.storage.migration_runner`
- `superlocalmemory.learning.features`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning.reward_proxy`
- `superlocalmemory.learning`
- `superlocalmemory.learning`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign learning1 = value

```python
learning1 = tmp_path / 'l1.db'
```

**Verification:**
```python
assert c1 is not c2
```

### Step 2: Assign learning2 = value

```python
learning2 = tmp_path / 'l2.db'
```

### Step 3: Assign memory = value

```python
memory = tmp_path / 'm.db'
```

### Step 4: Call apply_all()

```python
apply_all(learning1, memory)
```

### Step 5: Call apply_all()

```python
apply_all(learning2, memory)
```

### Step 6: Assign c1 = _conn_for(...)

```python
c1 = _conn_for(learning1)
```

### Step 7: Assign c2 = _conn_for(...)

```python
c2 = _conn_for(learning2)
```

**Verification:**
```python
assert c1 is not c2
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
learning1 = tmp_path / 'l1.db'
learning2 = tmp_path / 'l2.db'
memory = tmp_path / 'm.db'
apply_all(learning1, memory)
apply_all(learning2, memory)
c1 = _conn_for(learning1)
c2 = _conn_for(learning2)
assert c1 is not c2
```

## Next Steps


---

*Source: test_bandit_supplementary.py:492 | Complexity: Intermediate | Last updated: 2026-05-05*