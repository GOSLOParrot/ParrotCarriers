# How To: Forgotten Soft Delete

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Facts with retention < forget_threshold get lifecycle_zone='forgotten'
in fact_retention AND lifecycle='archived' in atomic_facts.
Verify they are NOT physically deleted.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `time`
- `datetime`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.learning.forgetting_scheduler`
- `superlocalmemory.math.ebbinghaus`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage`
- `superlocalmemory.storage.schema_v32`
- `superlocalmemory.storage`
- `superlocalmemory.storage.schema_v32`

**Setup Required:**
```python
# Fixtures: tmp_path, ebbinghaus
```

## Step-by-Step Guide

### Step 1: "Facts with retention < forget_threshold get lifecycle_zone='forgotten'\n    in fact_retention AND lifecycle='archived' in atomic_facts.\n    Verify they are NOT physically deleted."

```python
"Facts with retention < forget_threshold get lifecycle_zone='forgotten'\n    in fact_retention AND lifecycle='archived' in atomic_facts.\n    Verify they are NOT physically deleted."
```

**Verification:**
```python
assert stats['forgotten'] > 0, 'At least one fact should be forgotten'
```

### Step 2: Assign config = ForgettingConfig(...)

```python
config = ForgettingConfig(forget_threshold=0.99, archive_threshold=0.999)
```

**Verification:**
```python
assert len(rows) > 0, 'Fact must NOT be physically deleted'
```

### Step 3: Assign ebbinghaus_aggressive = EbbinghausCurve(...)

```python
ebbinghaus_aggressive = EbbinghausCurve(config)
```

**Verification:**
```python
assert dict(rows[0])['lifecycle'] == 'archived', "atomic_facts.lifecycle should be 'archived' (valid enum value)"
```

### Step 4: Assign db_path = value

```python
db_path = tmp_path / 'soft_delete.db'
```

**Verification:**
```python
assert len(ret_rows) > 0
```

### Step 5: Assign db = DatabaseManager(...)

```python
db = DatabaseManager(db_path)
```

**Verification:**
```python
assert dict(ret_rows[0])['lifecycle_zone'] == 'forgotten'
```

### Step 6: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

### Step 7: Assign conn.row_factory = value

```python
conn.row_factory = sqlite3.Row
```

### Step 8: Call schema.create_all_tables()

```python
schema.create_all_tables(conn)
```

### Step 9: Call conn.commit()

```python
conn.commit()
```

### Step 10: Call conn.execute()

```python
conn.execute('INSERT INTO profiles (profile_id, name) VALUES (?, ?)', ('test_profile', 'Test'))
```

### Step 11: Assign old_time = unknown.isoformat(...)

```python
old_time = (datetime.now(UTC) - timedelta(days=365)).isoformat()
```

### Step 12: Call conn.execute()

```python
conn.execute('INSERT INTO memories (memory_id, profile_id, content, session_id, speaker, role,  created_at, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', ('mem_old', 'test_profile', 'Old memory', 'sess1', 'user', 'user', old_time, '{}'))
```

### Step 13: Call conn.execute()

```python
conn.execute('INSERT INTO atomic_facts (fact_id, memory_id, profile_id, content, fact_type,  entities_json, canonical_entities_json, confidence, importance,  evidence_count, access_count, source_turn_ids_json,  lifecycle, emotional_valence, emotional_arousal, signal_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', ('fact_old', 'mem_old', 'test_profile', 'Old fact', 'semantic', '[]', '[]', 1.0, 0.0, 0, 0, '[]', 'active', 0.0, 0.0, 'factual', old_time))
```

### Step 14: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, computed_at) VALUES (?, ?, ?, datetime('now'))", ('fact_old', 'test_profile', 0.0))
```

### Step 15: Call conn.commit()

```python
conn.commit()
```

### Step 16: Call conn.close()

```python
conn.close()
```

### Step 17: Assign scheduler = ForgettingScheduler(...)

```python
scheduler = ForgettingScheduler(db, ebbinghaus_aggressive, config)
```

### Step 18: Assign stats = scheduler.run_decay_cycle(...)

```python
stats = scheduler.run_decay_cycle('test_profile')
```

**Verification:**
```python
assert stats['forgotten'] > 0, 'At least one fact should be forgotten'
```

### Step 19: Assign rows = db.execute(...)

```python
rows = db.execute('SELECT lifecycle FROM atomic_facts WHERE fact_id = ?', ('fact_old',))
```

**Verification:**
```python
assert len(rows) > 0, 'Fact must NOT be physically deleted'
```

### Step 20: Assign ret_rows = db.execute(...)

```python
ret_rows = db.execute('SELECT lifecycle_zone FROM fact_retention WHERE fact_id = ?', ('fact_old',))
```

**Verification:**
```python
assert len(ret_rows) > 0
```

### Step 21: Call conn.executescript()

```python
conn.executescript(ddl)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, ebbinghaus

# Workflow
"Facts with retention < forget_threshold get lifecycle_zone='forgotten'\n    in fact_retention AND lifecycle='archived' in atomic_facts.\n    Verify they are NOT physically deleted."
from superlocalmemory.storage import schema
from superlocalmemory.storage.schema_v32 import V32_DDL
config = ForgettingConfig(forget_threshold=0.99, archive_threshold=0.999)
ebbinghaus_aggressive = EbbinghausCurve(config)
db_path = tmp_path / 'soft_delete.db'
db = DatabaseManager(db_path)
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
schema.create_all_tables(conn)
for ddl in V32_DDL:
    conn.executescript(ddl)
conn.commit()
conn.execute('INSERT INTO profiles (profile_id, name) VALUES (?, ?)', ('test_profile', 'Test'))
old_time = (datetime.now(UTC) - timedelta(days=365)).isoformat()
conn.execute('INSERT INTO memories (memory_id, profile_id, content, session_id, speaker, role,  created_at, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', ('mem_old', 'test_profile', 'Old memory', 'sess1', 'user', 'user', old_time, '{}'))
conn.execute('INSERT INTO atomic_facts (fact_id, memory_id, profile_id, content, fact_type,  entities_json, canonical_entities_json, confidence, importance,  evidence_count, access_count, source_turn_ids_json,  lifecycle, emotional_valence, emotional_arousal, signal_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', ('fact_old', 'mem_old', 'test_profile', 'Old fact', 'semantic', '[]', '[]', 1.0, 0.0, 0, 0, '[]', 'active', 0.0, 0.0, 'factual', old_time))
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, computed_at) VALUES (?, ?, ?, datetime('now'))", ('fact_old', 'test_profile', 0.0))
conn.commit()
conn.close()
scheduler = ForgettingScheduler(db, ebbinghaus_aggressive, config)
stats = scheduler.run_decay_cycle('test_profile')
assert stats['forgotten'] > 0, 'At least one fact should be forgotten'
rows = db.execute('SELECT lifecycle FROM atomic_facts WHERE fact_id = ?', ('fact_old',))
assert len(rows) > 0, 'Fact must NOT be physically deleted'
assert dict(rows[0])['lifecycle'] == 'archived', "atomic_facts.lifecycle should be 'archived' (valid enum value)"
ret_rows = db.execute('SELECT lifecycle_zone FROM fact_retention WHERE fact_id = ?', ('fact_old',))
assert len(ret_rows) > 0
assert dict(ret_rows[0])['lifecycle_zone'] == 'forgotten'
```

## Next Steps


---

*Source: test_forgetting_scheduler.py:167 | Complexity: Advanced | Last updated: 2026-05-05*