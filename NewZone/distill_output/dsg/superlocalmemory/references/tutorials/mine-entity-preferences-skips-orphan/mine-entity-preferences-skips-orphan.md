# How To: Mine Entity Preferences Skips Orphan

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: If an entity_id in ``canonical_entities_json`` has no row in
``canonical_entities``, the miner produces no pattern for it.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `tempfile`
- `pathlib`
- `pytest`
- `superlocalmemory.learning.behavioral`
- `superlocalmemory.learning.behavioral`
- `superlocalmemory.learning`
- `superlocalmemory.learning.behavioral`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'If an entity_id in ``canonical_entities_json`` has no row in\n    ``canonical_entities``, the miner produces no pattern for it.'

```python
'If an entity_id in ``canonical_entities_json`` has no row in\n    ``canonical_entities``, the miner produces no pattern for it.'
```

**Verification:**
```python
assert 'Qualixar' in values, f'real entity missing from output: {values!r}'
```

### Step 2: Assign db_path = value

```python
db_path = tmp_path / 'memory.db'
```

**Verification:**
```python
assert orphan_id not in values, f'orphan id leaked into patterns: {values!r}'
```

### Step 3: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

### Step 4: Assign conn.row_factory = value

```python
conn.row_factory = sqlite3.Row
```

### Step 5: Call conn.execute()

```python
conn.execute('\n        CREATE TABLE canonical_entities (\n            entity_id TEXT PRIMARY KEY,\n            canonical_name TEXT,\n            entity_type TEXT\n        )\n    ')
```

### Step 6: Call conn.execute()

```python
conn.execute('INSERT INTO canonical_entities VALUES (?, ?, ?)', ('aaaa0000bbbb1111', 'Qualixar', 'company'))
```

### Step 7: Call conn.commit()

```python
conn.commit()
```

### Step 8: Assign orphan_id = 'ea701bf01f1ff4df8'

```python
orphan_id = 'ea701bf01f1ff4df8'
```

### Step 9: Assign real_id = 'aaaa0000bbbb1111'

```python
real_id = 'aaaa0000bbbb1111'
```

### Step 10: Assign facts = value

```python
facts = []
```

### Step 11: Assign store = BehavioralPatternStore(...)

```python
store = BehavioralPatternStore(str(tmp_path / 'learning.db'))
```

### Step 12: Assign gen = pattern_miner._mine_entity_preferences(...)

```python
gen = pattern_miner._mine_entity_preferences(store, conn, facts, profile_id='p', dry_run=False)
```

### Step 13: Assign out = store.get_patterns(...)

```python
out = store.get_patterns(profile_id='p')
```

### Step 14: Assign values = value

```python
values = [(p.get('metadata') or {}).get('value') for p in out]
```

**Verification:**
```python
assert 'Qualixar' in values, f'real entity missing from output: {values!r}'
```

### Step 15: Call conn.close()

```python
conn.close()
```

### Step 16: Call facts.append()

```python
facts.append({'canonical_entities_json': f'["{real_id}","{orphan_id}"]'})
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'If an entity_id in ``canonical_entities_json`` has no row in\n    ``canonical_entities``, the miner produces no pattern for it.'
from superlocalmemory.learning import pattern_miner
from superlocalmemory.learning.behavioral import BehavioralPatternStore
db_path = tmp_path / 'memory.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
conn.execute('\n        CREATE TABLE canonical_entities (\n            entity_id TEXT PRIMARY KEY,\n            canonical_name TEXT,\n            entity_type TEXT\n        )\n    ')
conn.execute('INSERT INTO canonical_entities VALUES (?, ?, ?)', ('aaaa0000bbbb1111', 'Qualixar', 'company'))
conn.commit()
orphan_id = 'ea701bf01f1ff4df8'
real_id = 'aaaa0000bbbb1111'
facts = []
for i in range(5):
    facts.append({'canonical_entities_json': f'["{real_id}","{orphan_id}"]'})
store = BehavioralPatternStore(str(tmp_path / 'learning.db'))
gen = pattern_miner._mine_entity_preferences(store, conn, facts, profile_id='p', dry_run=False)
out = store.get_patterns(profile_id='p')
values = [(p.get('metadata') or {}).get('value') for p in out]
assert 'Qualixar' in values, f'real entity missing from output: {values!r}'
assert orphan_id not in values, f'orphan id leaked into patterns: {values!r}'
conn.close()
```

## Next Steps


---

*Source: test_s9_dash_orphan_entity.py:92 | Complexity: Advanced | Last updated: 2026-05-05*