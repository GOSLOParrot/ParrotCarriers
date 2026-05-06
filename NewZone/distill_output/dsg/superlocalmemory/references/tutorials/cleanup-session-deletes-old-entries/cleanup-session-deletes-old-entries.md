# How To: Cleanup Session Deletes Old Entries

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test cleanup session deletes old entries

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `hmac`
- `json`
- `os`
- `sqlite3`
- `stat`
- `sys`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core`
- `superlocalmemory.core`

**Setup Required:**
```python
# Fixtures: home, cache
```

## Step-by-Step Guide

### Step 1: Assign old = _make_entry(...)

```python
old = _make_entry(computed_at=int(time.time()) - cc.CLEANUP_HORIZON_SECONDS - 100)
```

**Verification:**
```python
assert deleted == 1
```

### Step 2: Assign fresh = _make_entry(...)

```python
fresh = _make_entry(topic_sig='ffffffffffffffff', computed_at=int(time.time()))
```

**Verification:**
```python
assert got is not None
```

### Step 3: Call cache.upsert()

```python
cache.upsert(old)
```

### Step 4: Call cache.upsert()

```python
cache.upsert(fresh)
```

### Step 5: Assign deleted = cache.cleanup_session(...)

```python
deleted = cache.cleanup_session('sess-1')
```

**Verification:**
```python
assert deleted == 1
```

### Step 6: Assign got = cc.read_entry_fast(...)

```python
got = cc.read_entry_fast('sess-1', 'ffffffffffffffff', db_path=home / 'active_brain_cache.db', home_dir=home)
```

**Verification:**
```python
assert got is not None
```


## Complete Example

```python
# Setup
# Fixtures: home, cache

# Workflow
old = _make_entry(computed_at=int(time.time()) - cc.CLEANUP_HORIZON_SECONDS - 100)
fresh = _make_entry(topic_sig='ffffffffffffffff', computed_at=int(time.time()))
cache.upsert(old)
cache.upsert(fresh)
deleted = cache.cleanup_session('sess-1')
assert deleted == 1
got = cc.read_entry_fast('sess-1', 'ffffffffffffffff', db_path=home / 'active_brain_cache.db', home_dir=home)
assert got is not None
```

## Next Steps


---

*Source: test_context_cache.py:248 | Complexity: Advanced | Last updated: 2026-05-05*