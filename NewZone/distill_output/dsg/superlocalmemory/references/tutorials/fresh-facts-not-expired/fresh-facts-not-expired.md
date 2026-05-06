# How To: Fresh Facts Not Expired

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test fresh facts not expired

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
assert len(expired) == 0
```

### Step 2: Assign engine = RetentionEngine(...)

```python
engine = RetentionEngine(db)
```

### Step 3: Call db.execute()

```python
db.execute('CREATE TABLE atomic_facts (  id INTEGER PRIMARY KEY, profile_id TEXT,   created_at TEXT)')
```

### Step 4: Assign now = datetime.now.isoformat(...)

```python
now = datetime.now(timezone.utc).isoformat()
```

### Step 5: Call db.execute()

```python
db.execute("INSERT INTO atomic_facts (profile_id, created_at) VALUES ('p1', ?)", (now,))
```

### Step 6: Call db.commit()

```python
db.commit()
```

### Step 7: Call engine.add_rule()

```python
engine.add_rule('p1', 'GDPR-30d', 30)
```

### Step 8: Assign expired = engine.get_expired_facts(...)

```python
expired = engine.get_expired_facts('p1')
```

**Verification:**
```python
assert len(expired) == 0
```


## Complete Example

```python
# Workflow
from datetime import datetime, timezone
db = sqlite3.connect(':memory:')
engine = RetentionEngine(db)
db.execute('CREATE TABLE atomic_facts (  id INTEGER PRIMARY KEY, profile_id TEXT,   created_at TEXT)')
now = datetime.now(timezone.utc).isoformat()
db.execute("INSERT INTO atomic_facts (profile_id, created_at) VALUES ('p1', ?)", (now,))
db.commit()
engine.add_rule('p1', 'GDPR-30d', 30)
expired = engine.get_expired_facts('p1')
assert len(expired) == 0
```

## Next Steps


---

*Source: test_compliance_full.py:350 | Complexity: Advanced | Last updated: 2026-05-05*