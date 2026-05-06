# How To: Close Session Creates Temporal Events

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: close_session() creates temporal_events rows grouped by entity.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.core.modes`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: engine_with_mock_deps
```

## Step-by-Step Guide

### Step 1: 'close_session() creates temporal_events rows grouped by entity.'

```python
'close_session() creates temporal_events rows grouped by entity.'
```

**Verification:**
```python
assert count >= 1
```

### Step 2: Assign db = value

```python
db = engine_with_mock_deps._db
```

### Step 3: Assign pid = value

```python
pid = engine_with_mock_deps._profile_id
```

### Step 4: Call db.execute()

```python
db.execute('INSERT OR IGNORE INTO profiles (profile_id, name) VALUES (?, ?)', (pid, pid))
```

### Step 5: Call db.execute()

```python
db.execute('INSERT OR IGNORE INTO canonical_entities (entity_id, profile_id, canonical_name) VALUES (?, ?, ?)', ('ent-alice', pid, 'Alice'))
```

### Step 6: Assign record = MemoryRecord(...)

```python
record = MemoryRecord(memory_id='m-sess1', profile_id=pid, content='Alice went to Paris', session_id='sess-1')
```

### Step 7: Call db.store_memory()

```python
db.store_memory(record)
```

### Step 8: Assign fact = _make_fact(...)

```python
fact = _make_fact('f1', session_id='sess-1', content='Alice went to Paris', canonical_entities=['ent-alice'], observation_date='2026-03-01')
```

### Step 9: Assign fact.memory_id = 'm-sess1'

```python
fact.memory_id = 'm-sess1'
```

### Step 10: Assign fact.profile_id = pid

```python
fact.profile_id = pid
```

### Step 11: Call db.store_fact()

```python
db.store_fact(fact)
```

### Step 12: Assign count = engine_with_mock_deps.close_session(...)

```python
count = engine_with_mock_deps.close_session('sess-1')
```

**Verification:**
```python
assert count >= 1
```


## Complete Example

```python
# Setup
# Fixtures: engine_with_mock_deps

# Workflow
'close_session() creates temporal_events rows grouped by entity.'
from superlocalmemory.storage.models import MemoryRecord
db = engine_with_mock_deps._db
pid = engine_with_mock_deps._profile_id
db.execute('INSERT OR IGNORE INTO profiles (profile_id, name) VALUES (?, ?)', (pid, pid))
db.execute('INSERT OR IGNORE INTO canonical_entities (entity_id, profile_id, canonical_name) VALUES (?, ?, ?)', ('ent-alice', pid, 'Alice'))
record = MemoryRecord(memory_id='m-sess1', profile_id=pid, content='Alice went to Paris', session_id='sess-1')
db.store_memory(record)
fact = _make_fact('f1', session_id='sess-1', content='Alice went to Paris', canonical_entities=['ent-alice'], observation_date='2026-03-01')
fact.memory_id = 'm-sess1'
fact.profile_id = pid
db.store_fact(fact)
count = engine_with_mock_deps.close_session('sess-1')
assert count >= 1
```

## Next Steps


---

*Source: test_engine_session_lifecycle.py:106 | Complexity: Advanced | Last updated: 2026-05-05*