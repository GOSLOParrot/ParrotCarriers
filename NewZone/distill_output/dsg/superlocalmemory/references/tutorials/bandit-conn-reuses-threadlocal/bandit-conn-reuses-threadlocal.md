# How To: Bandit Conn Reuses Threadlocal

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Second call on same thread returns the same connection.

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

### Step 1: 'Second call on same thread returns the same connection.'

```python
'Second call on same thread returns the same connection.'
```

**Verification:**
```python
assert c1 is c2
```

### Step 2: Assign learning = value

```python
learning = tmp_path / 'learning.db'
```

### Step 3: Assign memory = value

```python
memory = tmp_path / 'memory.db'
```

### Step 4: Call apply_all()

```python
apply_all(learning, memory)
```

### Step 5: Assign c1 = _conn_for(...)

```python
c1 = _conn_for(learning)
```

### Step 6: Assign c2 = _conn_for(...)

```python
c2 = _conn_for(learning)
```

**Verification:**
```python
assert c1 is c2
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Second call on same thread returns the same connection.'
learning = tmp_path / 'learning.db'
memory = tmp_path / 'memory.db'
apply_all(learning, memory)
c1 = _conn_for(learning)
c2 = _conn_for(learning)
assert c1 is c2
```

## Next Steps


---

*Source: test_bandit_supplementary.py:404 | Complexity: Intermediate | Last updated: 2026-05-05*