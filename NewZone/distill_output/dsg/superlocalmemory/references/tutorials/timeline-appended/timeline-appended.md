# How To: Timeline Appended

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: test timeline appended

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
assert len(timeline) >= 2
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

### Step 5: Call conn.execute()

```python
conn.execute("UPDATE entity_profiles SET last_compiled_at='1970-01-01'")
```

### Step 6: Call conn.commit()

```python
conn.commit()
```

### Step 7: Call conn.close()

```python
conn.close()
```

### Step 8: Call compiler.compile_all()

```python
compiler.compile_all('default')
```

### Step 9: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

### Step 10: Assign row = conn.execute.fetchone(...)

```python
row = conn.execute('SELECT timeline FROM entity_profiles WHERE entity_id=?', (entity_id,)).fetchone()
```

### Step 11: Call conn.close()

```python
conn.close()
```

### Step 12: Assign timeline = json.loads(...)

```python
timeline = json.loads(row[0])
```

**Verification:**
```python
assert len(timeline) >= 2
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
conn.execute("UPDATE entity_profiles SET last_compiled_at='1970-01-01'")
conn.commit()
conn.close()
compiler.compile_all('default')
conn = sqlite3.connect(str(db_path))
row = conn.execute('SELECT timeline FROM entity_profiles WHERE entity_id=?', (entity_id,)).fetchone()
conn.close()
timeline = json.loads(row[0])
assert len(timeline) >= 2
```

## Next Steps


---

*Source: test_entity_compilation.py:118 | Complexity: Advanced | Last updated: 2026-05-05*