# How To: Fact Ids Stored

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test fact ids stored

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
# Fixtures: entity_db
```

## Step-by-Step Guide

### Step 1: Assign unknown = entity_db

```python
db_path, entity_id = entity_db
```

**Verification:**
```python
assert len(fact_ids) >= 1
```

### Step 2: Assign compiler = EntityCompiler(...)

```python
compiler = EntityCompiler(str(db_path))
```

### Step 3: Call compiler.compile_all()

```python
compiler.compile_all('default')
```

### Step 4: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

### Step 5: Assign row = conn.execute.fetchone(...)

```python
row = conn.execute('SELECT fact_ids_json FROM entity_profiles WHERE entity_id=?', (entity_id,)).fetchone()
```

### Step 6: Call conn.close()

```python
conn.close()
```

### Step 7: Assign fact_ids = json.loads(...)

```python
fact_ids = json.loads(row[0])
```

**Verification:**
```python
assert len(fact_ids) >= 1
```


## Complete Example

```python
# Setup
# Fixtures: entity_db

# Workflow
db_path, entity_id = entity_db
from superlocalmemory.learning.entity_compiler import EntityCompiler
compiler = EntityCompiler(str(db_path))
compiler.compile_all('default')
conn = sqlite3.connect(str(db_path))
row = conn.execute('SELECT fact_ids_json FROM entity_profiles WHERE entity_id=?', (entity_id,)).fetchone()
conn.close()
fact_ids = json.loads(row[0])
assert len(fact_ids) >= 1
```

## Next Steps


---

*Source: test_entity_compilation.py:142 | Complexity: Intermediate | Last updated: 2026-05-05*