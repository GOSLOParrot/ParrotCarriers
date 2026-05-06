# How To: Run Once

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test run once

## Prerequisites

**Required Modules:**
- `__future__`
- `sqlite3`
- `tempfile`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.compliance.abac`
- `superlocalmemory.compliance.audit`
- `superlocalmemory.compliance.retention`
- `superlocalmemory.compliance.scheduler`
- `datetime`


## Step-by-Step Guide

### Step 1: Assign db = sqlite3.connect(...)

```python
db = sqlite3.connect(':memory:')
```

**Verification:**
```python
assert 'profiles_processed' in result
```

### Step 2: Assign engine = RetentionEngine(...)

```python
engine = RetentionEngine(db)
```

**Verification:**
```python
assert 'results' in result
```

### Step 3: Assign scheduler = RetentionScheduler(...)

```python
scheduler = RetentionScheduler(engine, interval_seconds=3600)
```

**Verification:**
```python
assert result['profiles_processed'] == 0
```

### Step 4: Assign result = scheduler.run_once(...)

```python
result = scheduler.run_once()
```

**Verification:**
```python
assert 'profiles_processed' in result
```


## Complete Example

```python
# Workflow
db = sqlite3.connect(':memory:')
engine = RetentionEngine(db)
scheduler = RetentionScheduler(engine, interval_seconds=3600)
result = scheduler.run_once()
assert 'profiles_processed' in result
assert 'results' in result
assert result['profiles_processed'] == 0
```

## Next Steps


---

*Source: test_compliance_full.py:436 | Complexity: Intermediate | Last updated: 2026-05-05*