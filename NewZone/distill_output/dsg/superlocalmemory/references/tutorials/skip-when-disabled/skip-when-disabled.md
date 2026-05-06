# How To: Skip When Disabled

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test skip when disabled

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
assert result['reason'] == 'disabled'
```

### Step 2: Assign compiler = EntityCompiler(...)

```python
compiler = EntityCompiler(str(db_path), config=MockConfig())
```

### Step 3: Assign result = compiler.compile_all(...)

```python
result = compiler.compile_all('default')
```

**Verification:**
```python
assert result['reason'] == 'disabled'
```

### Step 4: Assign entity_compilation_enabled = False

```python
entity_compilation_enabled = False
```

### Step 5: Assign mode = type(...)

```python
mode = type('obj', (object,), {'value': 'a'})()
```


## Complete Example

```python
# Setup
# Fixtures: entity_db

# Workflow
db_path, entity_id = entity_db

class MockConfig:
    entity_compilation_enabled = False
    mode = type('obj', (object,), {'value': 'a'})()
from superlocalmemory.learning.entity_compiler import EntityCompiler
compiler = EntityCompiler(str(db_path), config=MockConfig())
result = compiler.compile_all('default')
assert result['reason'] == 'disabled'
```

## Next Steps


---

*Source: test_entity_compilation.py:171 | Complexity: Intermediate | Last updated: 2026-05-05*