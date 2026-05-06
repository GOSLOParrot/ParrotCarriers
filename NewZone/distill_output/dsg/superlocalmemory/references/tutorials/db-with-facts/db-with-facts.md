# How To: Db With Facts

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: Create a real DB with schema and seed 10 test facts.

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
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Create a real DB with schema and seed 10 test facts.'

```python
'Create a real DB with schema and seed 10 test facts.'
```

### Step 2: Assign db_path = value

```python
db_path = tmp_path / 'test.db'
```

### Step 3: Assign db = DatabaseManager(...)

```python
db = DatabaseManager(db_path)
```

### Step 4: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

### Step 5: Assign conn.row_factory = value

```python
conn.row_factory = sqlite3.Row
```

### Step 6: Call schema.create_all_tables()

```python
schema.create_all_tables(conn)
```

### Step 7: Call conn.commit()

```python
conn.commit()
```

### Step 8: Call conn.commit()

```python
conn.commit()
```

### Step 9: Call conn.execute()

```python
conn.execute('INSERT INTO profiles (profile_id, name) VALUES (?, ?)', ('test_profile', 'Test Profile'))
```

### Step 10: Assign now = datetime.now(...)

```python
now = datetime.now(UTC)
```

### Step 11: Call conn.commit()

```python
conn.commit()
```

### Step 12: Call conn.close()

```python
conn.close()
```

### Step 13: Call conn.executescript()

```python
conn.executescript(ddl)
```

### Step 14: Assign fact_id = value

```python
fact_id = f'fact_{i:03d}'
```

### Step 15: Assign hours_ago = value

```python
hours_ago = i * 24
```

### Step 16: Assign created = unknown.isoformat(...)

```python
created = (now - timedelta(hours=hours_ago)).isoformat()
```

### Step 17: Call conn.execute()

```python
conn.execute('INSERT INTO memories (memory_id, profile_id, content, session_id, speaker, role,  created_at, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (f'mem_{i}', 'test_profile', f'Memory {i}', 'sess1', 'user', 'user', created, '{}'))
```

### Step 18: Call conn.execute()

```python
conn.execute('INSERT INTO atomic_facts (fact_id, memory_id, profile_id, content, fact_type,  entities_json, canonical_entities_json, confidence, importance,  evidence_count, access_count, source_turn_ids_json,  lifecycle, emotional_valence, emotional_arousal, signal_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (fact_id, f'mem_{i}', 'test_profile', f'Test fact {i}', 'semantic', '[]', '[]', 1.0, 0.5 - i * 0.05, max(1, 5 - i), 0, '[]', 'active', 0.0, 0.0, 'factual', created))
```

### Step 19: Call conn.execute()

```python
conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, computed_at) VALUES (?, ?, ?, datetime('now'))", (fact_id, 'test_profile', max(0.0, 0.5 - i * 0.05)))
```

### Step 20: Assign access_time = unknown.isoformat(...)

```python
access_time = (now - timedelta(hours=hours_ago - j)).isoformat()
```

### Step 21: Call conn.execute()

```python
conn.execute('INSERT INTO fact_access_log (log_id, fact_id, profile_id, access_type, session_id, accessed_at) VALUES (?, ?, ?, ?, ?, ?)', (f'log_{i}_{j}', fact_id, 'test_profile', 'recall', 'sess1', access_time))
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Create a real DB with schema and seed 10 test facts.'
from superlocalmemory.storage import schema
from superlocalmemory.storage.schema_v32 import V32_DDL
db_path = tmp_path / 'test.db'
db = DatabaseManager(db_path)
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
schema.create_all_tables(conn)
conn.commit()
for ddl in V32_DDL:
    conn.executescript(ddl)
conn.commit()
conn.execute('INSERT INTO profiles (profile_id, name) VALUES (?, ?)', ('test_profile', 'Test Profile'))
now = datetime.now(UTC)
for i in range(10):
    fact_id = f'fact_{i:03d}'
    hours_ago = i * 24
    created = (now - timedelta(hours=hours_ago)).isoformat()
    conn.execute('INSERT INTO memories (memory_id, profile_id, content, session_id, speaker, role,  created_at, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (f'mem_{i}', 'test_profile', f'Memory {i}', 'sess1', 'user', 'user', created, '{}'))
    conn.execute('INSERT INTO atomic_facts (fact_id, memory_id, profile_id, content, fact_type,  entities_json, canonical_entities_json, confidence, importance,  evidence_count, access_count, source_turn_ids_json,  lifecycle, emotional_valence, emotional_arousal, signal_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (fact_id, f'mem_{i}', 'test_profile', f'Test fact {i}', 'semantic', '[]', '[]', 1.0, 0.5 - i * 0.05, max(1, 5 - i), 0, '[]', 'active', 0.0, 0.0, 'factual', created))
    for j in range(max(1, 10 - i)):
        access_time = (now - timedelta(hours=hours_ago - j)).isoformat()
        conn.execute('INSERT INTO fact_access_log (log_id, fact_id, profile_id, access_type, session_id, accessed_at) VALUES (?, ?, ?, ?, ?, ?)', (f'log_{i}_{j}', fact_id, 'test_profile', 'recall', 'sess1', access_time))
    conn.execute("INSERT INTO fact_importance (fact_id, profile_id, pagerank_score, computed_at) VALUES (?, ?, ?, datetime('now'))", (fact_id, 'test_profile', max(0.0, 0.5 - i * 0.05)))
conn.commit()
conn.close()
return db
```

## Next Steps


---

*Source: test_forgetting_scheduler.py:38 | Complexity: Advanced | Last updated: 2026-05-05*