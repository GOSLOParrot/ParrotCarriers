# How To: Bandit Update Write Error Returns False

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: If the UPDATE fails (corrupt table), update returns False.

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

### Step 1: 'If the UPDATE fails (corrupt table), update returns False.'

```python
'If the UPDATE fails (corrupt table), update returns False.'
```

**Verification:**
```python
assert b.update(ch.play_id, reward=1.0) is False
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

### Step 5: Assign b = ContextualBandit(...)

```python
b = ContextualBandit(learning, profile_id='p', cache=_BanditCache(max_entries=4))
```

### Step 6: Assign ch = b.choose(...)

```python
ch = b.choose({'query_type': 'single_hop', 'entity_count': 0, 'time_bucket': 'morning'}, query_id='q-w')
```

### Step 7: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(learning), isolation_level=None)
```

**Verification:**
```python
assert b.update(ch.play_id, reward=1.0) is False
```

### Step 8: Call _b._holder.conn.close()

```python
_b._holder.conn.close()
```

### Step 9: Assign _b._holder.conn = None

```python
_b._holder.conn = None
```

### Step 10: Assign _b._holder.path = None

```python
_b._holder.path = None
```

### Step 11: Call conn.execute()

```python
conn.execute('DROP TABLE bandit_arms')
```

### Step 12: Call conn.close()

```python
conn.close()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'If the UPDATE fails (corrupt table), update returns False.'
learning = tmp_path / 'learning.db'
memory = tmp_path / 'memory.db'
apply_all(learning, memory)
b = ContextualBandit(learning, profile_id='p', cache=_BanditCache(max_entries=4))
ch = b.choose({'query_type': 'single_hop', 'entity_count': 0, 'time_bucket': 'morning'}, query_id='q-w')
from superlocalmemory.learning import bandit as _b
if _b._holder.conn is not None:
    _b._holder.conn.close()
    _b._holder.conn = None
    _b._holder.path = None
conn = sqlite3.connect(str(learning), isolation_level=None)
try:
    conn.execute('DROP TABLE bandit_arms')
finally:
    conn.close()
assert b.update(ch.play_id, reward=1.0) is False
```

## Next Steps


---

*Source: test_bandit_supplementary.py:460 | Complexity: Advanced | Last updated: 2026-05-05*