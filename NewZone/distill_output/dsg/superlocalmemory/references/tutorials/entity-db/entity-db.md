# How To: Entity Db

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: Create a temp DB with required tables + sample entities.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `uuid`
- `datetime`
- `pytest`
- `superlocalmemory.learning.entity_compiler`
- `superlocalmemory.learning.entity_compiler`
- `superlocalmemory.learning.entity_compiler`
- `superlocalmemory.learning.entity_compiler`
- `superlocalmemory.learning.entity_compiler`
- `superlocalmemory.learning.entity_compiler`
- `superlocalmemory.learning.entity_compiler`
- `superlocalmemory.learning.entity_compiler`
- `superlocalmemory.learning.entity_compiler`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Create a temp DB with required tables + sample entities.'

```python
'Create a temp DB with required tables + sample entities.'
```

### Step 2: Assign db_path = value

```python
db_path = tmp_path / 'entity_test.db'
```

### Step 3: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

### Step 4: Call conn.executescript()

```python
conn.executescript("\n        CREATE TABLE IF NOT EXISTS atomic_facts (\n            fact_id TEXT PRIMARY KEY, memory_id TEXT DEFAULT '',\n            content TEXT, confidence REAL DEFAULT 0.8,\n            created_at TEXT, profile_id TEXT DEFAULT 'default',\n            canonical_entities_json TEXT DEFAULT '[]',\n            fact_type TEXT DEFAULT 'fact'\n        );\n        CREATE TABLE IF NOT EXISTS canonical_entities (\n            entity_id TEXT PRIMARY KEY, profile_id TEXT DEFAULT 'default',\n            canonical_name TEXT, entity_type TEXT DEFAULT 'person',\n            first_seen TEXT, last_seen TEXT, fact_count INTEGER DEFAULT 0\n        );\n        CREATE TABLE IF NOT EXISTS fact_importance (\n            fact_id TEXT PRIMARY KEY, profile_id TEXT,\n            pagerank_score REAL, community_id INTEGER,\n            degree_centrality REAL, computed_at TEXT\n        );\n        CREATE TABLE IF NOT EXISTS entity_profiles (\n            profile_entry_id TEXT PRIMARY KEY,\n            entity_id TEXT, profile_id TEXT DEFAULT 'default',\n            knowledge_summary TEXT DEFAULT '', fact_ids_json TEXT DEFAULT '[]',\n            last_updated TEXT DEFAULT '',\n            project_name TEXT DEFAULT '',\n            compiled_truth TEXT DEFAULT '',\n            timeline TEXT DEFAULT '[]',\n            compilation_confidence REAL DEFAULT 0.5,\n            last_compiled_at TEXT DEFAULT NULL\n        );\n    ")
```

### Step 5: Assign entity_id = 'ent-alice-001'

```python
entity_id = 'ent-alice-001'
```

### Step 6: Call conn.execute()

```python
conn.execute("INSERT INTO canonical_entities VALUES (?, 'default', 'Alice', 'person', ?, ?, 5)", (entity_id, datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()))
```

### Step 7: Call conn.commit()

```python
conn.commit()
```

### Step 8: Call conn.close()

```python
conn.close()
```

### Step 9: Assign fid = value

```python
fid = f'fact-{uuid.uuid4().hex[:8]}'
```

### Step 10: Call conn.execute()

```python
conn.execute("INSERT INTO atomic_facts (fact_id, content, confidence, created_at, profile_id, canonical_entities_json) VALUES (?, ?, ?, ?, 'default', ?)", (fid, f'Alice fact {i}: she works on AI project {i} at Qualixar', 0.8 + i * 0.02, datetime.now(timezone.utc).isoformat(), json.dumps([entity_id])))
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Create a temp DB with required tables + sample entities.'
db_path = tmp_path / 'entity_test.db'
conn = sqlite3.connect(str(db_path))
conn.executescript("\n        CREATE TABLE IF NOT EXISTS atomic_facts (\n            fact_id TEXT PRIMARY KEY, memory_id TEXT DEFAULT '',\n            content TEXT, confidence REAL DEFAULT 0.8,\n            created_at TEXT, profile_id TEXT DEFAULT 'default',\n            canonical_entities_json TEXT DEFAULT '[]',\n            fact_type TEXT DEFAULT 'fact'\n        );\n        CREATE TABLE IF NOT EXISTS canonical_entities (\n            entity_id TEXT PRIMARY KEY, profile_id TEXT DEFAULT 'default',\n            canonical_name TEXT, entity_type TEXT DEFAULT 'person',\n            first_seen TEXT, last_seen TEXT, fact_count INTEGER DEFAULT 0\n        );\n        CREATE TABLE IF NOT EXISTS fact_importance (\n            fact_id TEXT PRIMARY KEY, profile_id TEXT,\n            pagerank_score REAL, community_id INTEGER,\n            degree_centrality REAL, computed_at TEXT\n        );\n        CREATE TABLE IF NOT EXISTS entity_profiles (\n            profile_entry_id TEXT PRIMARY KEY,\n            entity_id TEXT, profile_id TEXT DEFAULT 'default',\n            knowledge_summary TEXT DEFAULT '', fact_ids_json TEXT DEFAULT '[]',\n            last_updated TEXT DEFAULT '',\n            project_name TEXT DEFAULT '',\n            compiled_truth TEXT DEFAULT '',\n            timeline TEXT DEFAULT '[]',\n            compilation_confidence REAL DEFAULT 0.5,\n            last_compiled_at TEXT DEFAULT NULL\n        );\n    ")
entity_id = 'ent-alice-001'
conn.execute("INSERT INTO canonical_entities VALUES (?, 'default', 'Alice', 'person', ?, ?, 5)", (entity_id, datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()))
for i in range(5):
    fid = f'fact-{uuid.uuid4().hex[:8]}'
    conn.execute("INSERT INTO atomic_facts (fact_id, content, confidence, created_at, profile_id, canonical_entities_json) VALUES (?, ?, ?, ?, 'default', ?)", (fid, f'Alice fact {i}: she works on AI project {i} at Qualixar', 0.8 + i * 0.02, datetime.now(timezone.utc).isoformat(), json.dumps([entity_id])))
conn.commit()
conn.close()
return (db_path, entity_id)
```

## Next Steps


---

*Source: test_entity_compilation.py:19 | Complexity: Advanced | Last updated: 2026-05-05*