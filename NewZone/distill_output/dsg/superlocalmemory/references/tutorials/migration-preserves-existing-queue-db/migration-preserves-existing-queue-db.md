# How To: Migration Preserves Existing Queue Db

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test migration preserves existing queue db

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `superlocalmemory.migrations`
- `superlocalmemory.core.recall_queue`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign mig = _imports(...)

```python
mig = _imports()
```

**Verification:**
```python
assert q2._get_row(rid) is not None
```

### Step 2: Call mig.migrate()

```python
mig.migrate(tmp_path)
```

### Step 3: Assign q = RecallQueue(...)

```python
q = RecallQueue(db_path=tmp_path / 'recall_queue.db')
```

### Step 4: Assign rid = q.enqueue(...)

```python
rid = q.enqueue(query='preserved', limit_n=10, mode='B', agent_id='a', session_id='s')
```

### Step 5: Call q.close()

```python
q.close()
```

### Step 6: Call mig.migrate()

```python
mig.migrate(tmp_path)
```

### Step 7: Assign q2 = RecallQueue(...)

```python
q2 = RecallQueue(db_path=tmp_path / 'recall_queue.db')
```

**Verification:**
```python
assert q2._get_row(rid) is not None
```

### Step 8: Call q2.close()

```python
q2.close()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
mig = _imports()
mig.migrate(tmp_path)
from superlocalmemory.core.recall_queue import RecallQueue
q = RecallQueue(db_path=tmp_path / 'recall_queue.db')
rid = q.enqueue(query='preserved', limit_n=10, mode='B', agent_id='a', session_id='s')
q.close()
mig.migrate(tmp_path)
q2 = RecallQueue(db_path=tmp_path / 'recall_queue.db')
assert q2._get_row(rid) is not None
q2.close()
```

## Next Steps


---

*Source: test_migration_v3_4_26.py:44 | Complexity: Advanced | Last updated: 2026-05-05*