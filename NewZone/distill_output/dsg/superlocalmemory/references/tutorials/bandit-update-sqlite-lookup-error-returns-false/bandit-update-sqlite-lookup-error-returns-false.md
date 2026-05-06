# How To: Bandit Update Sqlite Lookup Error Returns False

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: If the lookup SELECT raises, update returns False gracefully.

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
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'If the lookup SELECT raises, update returns False gracefully.'

```python
'If the lookup SELECT raises, update returns False gracefully.'
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
ch = b.choose({'query_type': 'single_hop', 'entity_count': 0, 'time_bucket': 'morning'}, query_id='q-err')
```

### Step 7: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(learning), isolation_level=None)
```

**Verification:**
```python
assert b.update(ch.play_id, reward=1.0) is False
```

### Step 8: Call conn.execute()

```python
conn.execute('DROP TABLE bandit_plays')
```

### Step 9: Call conn.close()

```python
conn.close()
```

### Step 10: Call _b._holder.conn.close()

```python
_b._holder.conn.close()
```

### Step 11: Assign _b._holder.conn = None

```python
_b._holder.conn = None
```

### Step 12: Assign _b._holder.path = None

```python
_b._holder.path = None
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'If the lookup SELECT raises, update returns False gracefully.'
learning = tmp_path / 'learning.db'
memory = tmp_path / 'memory.db'
apply_all(learning, memory)
b = ContextualBandit(learning, profile_id='p', cache=_BanditCache(max_entries=4))
ch = b.choose({'query_type': 'single_hop', 'entity_count': 0, 'time_bucket': 'morning'}, query_id='q-err')
conn = sqlite3.connect(str(learning), isolation_level=None)
try:
    conn.execute('DROP TABLE bandit_plays')
finally:
    conn.close()
from superlocalmemory.learning import bandit as _b
if _b._holder.conn is not None:
    _b._holder.conn.close()
    _b._holder.conn = None
    _b._holder.path = None
assert b.update(ch.play_id, reward=1.0) is False
```

## Next Steps


---

*Source: test_bandit_supplementary.py:431 | Complexity: Advanced | Last updated: 2026-05-05*