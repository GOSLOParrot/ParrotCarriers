# How To: Compiled Truth Under 2000 Chars

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test compiled truth under 2000 chars

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
assert row is not None
```

### Step 2: Assign compiler = EntityCompiler(...)

```python
compiler = EntityCompiler(str(db_path))
```

**Verification:**
```python
assert len(row[0]) <= 2000
```

### Step 3: Call compiler.compile_all()

```python
compiler.compile_all('default')
```

**Verification:**
```python
assert len(row[0]) > 0
```

### Step 4: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

### Step 5: Assign row = conn.execute.fetchone(...)

```python
row = conn.execute('SELECT compiled_truth FROM entity_profiles WHERE entity_id=?', (entity_id,)).fetchone()
```

### Step 6: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert row is not None
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
row = conn.execute('SELECT compiled_truth FROM entity_profiles WHERE entity_id=?', (entity_id,)).fetchone()
conn.close()
assert row is not None
assert len(row[0]) <= 2000
assert len(row[0]) > 0
```

## Next Steps


---

*Source: test_entity_compilation.py:87 | Complexity: Intermediate | Last updated: 2026-05-05*