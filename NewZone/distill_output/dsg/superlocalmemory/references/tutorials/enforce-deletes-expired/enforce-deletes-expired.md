# How To: Enforce Deletes Expired

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test enforce deletes expired

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
assert result['deleted_count'] == 1
```

### Step 2: Assign engine = RetentionEngine(...)

```python
engine = RetentionEngine(db)
```

**Verification:**
```python
assert row[0] == 0
```

### Step 3: Call db.execute()

```python
db.execute('CREATE TABLE atomic_facts (  id INTEGER PRIMARY KEY, profile_id TEXT,   created_at TEXT)')
```

### Step 4: Call db.execute()

```python
db.execute("INSERT INTO atomic_facts (profile_id, created_at) VALUES ('p1', '2020-01-01T00:00:00+00:00')")
```

### Step 5: Call db.commit()

```python
db.commit()
```

### Step 6: Call engine.add_rule()

```python
engine.add_rule('p1', 'GDPR-30d', 30)
```

### Step 7: Assign result = engine.enforce(...)

```python
result = engine.enforce('p1')
```

**Verification:**
```python
assert result['deleted_count'] == 1
```

### Step 8: Assign row = db.execute.fetchone(...)

```python
row = db.execute("SELECT COUNT(*) FROM atomic_facts WHERE profile_id='p1'").fetchone()
```

**Verification:**
```python
assert row[0] == 0
```


## Complete Example

```python
# Workflow
db = sqlite3.connect(':memory:')
engine = RetentionEngine(db)
db.execute('CREATE TABLE atomic_facts (  id INTEGER PRIMARY KEY, profile_id TEXT,   created_at TEXT)')
db.execute("INSERT INTO atomic_facts (profile_id, created_at) VALUES ('p1', '2020-01-01T00:00:00+00:00')")
db.commit()
engine.add_rule('p1', 'GDPR-30d', 30)
result = engine.enforce('p1')
assert result['deleted_count'] == 1
row = db.execute("SELECT COUNT(*) FROM atomic_facts WHERE profile_id='p1'").fetchone()
assert row[0] == 0
```

## Next Steps


---

*Source: test_compliance_full.py:373 | Complexity: Advanced | Last updated: 2026-05-05*