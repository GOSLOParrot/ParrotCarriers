# How To: Different Profiles Isolated

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test different profiles isolated

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `pytest`
- `superlocalmemory.storage`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.access_log`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: db, access_log
```

## Step-by-Step Guide

### Step 1: Call db.execute()

```python
db.execute('INSERT OR IGNORE INTO profiles (profile_id, name) VALUES (?, ?)', ('p2', 'Profile 2'))
```

**Verification:**
```python
assert len(default_times) == 1
```

### Step 2: Assign default_times = access_log.get_all_access_times(...)

```python
default_times = access_log.get_all_access_times('default')
```

**Verification:**
```python
assert len(p2_times) == 1
```

### Step 3: Assign p2_times = access_log.get_all_access_times(...)

```python
p2_times = access_log.get_all_access_times('p2')
```

**Verification:**
```python
assert set(default_times.keys()) != set(p2_times.keys())
```

### Step 4: Assign record = MemoryRecord(...)

```python
record = MemoryRecord(profile_id=pid, content='content', session_id='s1')
```

### Step 5: Call db.store_memory()

```python
db.store_memory(record)
```

### Step 6: Assign fact = AtomicFact(...)

```python
fact = AtomicFact(profile_id=pid, memory_id=record.memory_id, content=f'Fact for {pid}')
```

### Step 7: Call db.store_fact()

```python
db.store_fact(fact)
```

### Step 8: Call access_log.store_access()

```python
access_log.store_access(fact.fact_id, pid)
```


## Complete Example

```python
# Setup
# Fixtures: db, access_log

# Workflow
db.execute('INSERT OR IGNORE INTO profiles (profile_id, name) VALUES (?, ?)', ('p2', 'Profile 2'))
for pid in ('default', 'p2'):
    record = MemoryRecord(profile_id=pid, content='content', session_id='s1')
    db.store_memory(record)
    fact = AtomicFact(profile_id=pid, memory_id=record.memory_id, content=f'Fact for {pid}')
    db.store_fact(fact)
    access_log.store_access(fact.fact_id, pid)
default_times = access_log.get_all_access_times('default')
p2_times = access_log.get_all_access_times('p2')
assert len(default_times) == 1
assert len(p2_times) == 1
assert set(default_times.keys()) != set(p2_times.keys())
```

## Next Steps


---

*Source: test_access_log.py:179 | Complexity: Advanced | Last updated: 2026-05-05*