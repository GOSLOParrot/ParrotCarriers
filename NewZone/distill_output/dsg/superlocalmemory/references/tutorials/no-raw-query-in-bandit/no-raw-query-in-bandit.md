# How To: No Raw Query In Bandit

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: B6: bandit_arms and bandit_plays must not have 'query' / 'query_text'.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `itertools`
- `secrets`
- `sqlite3`
- `pathlib`
- `pytest`
- `superlocalmemory.learning.arm_catalog`
- `superlocalmemory.learning.bandit`
- `superlocalmemory.learning.bandit_cache`
- `superlocalmemory.storage.migration_runner`
- `datetime`
- `datetime`
- `time`

**Setup Required:**
```python
# Fixtures: bandit_db
```

## Step-by-Step Guide

### Step 1: "B6: bandit_arms and bandit_plays must not have 'query' / 'query_text'."

```python
"B6: bandit_arms and bandit_plays must not have 'query' / 'query_text'."
```

**Verification:**
```python
assert arms_cols.isdisjoint(forbidden)
```

### Step 2: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(bandit_db))
```

**Verification:**
```python
assert plays_cols.isdisjoint(forbidden)
```

### Step 3: Assign forbidden = value

```python
forbidden = {'query', 'query_text', 'raw_query', 'prompt'}
```

**Verification:**
```python
assert arms_cols.isdisjoint(forbidden)
```

### Step 4: Assign arms_cols = value

```python
arms_cols = {r[1] for r in conn.execute('PRAGMA table_info(bandit_arms)').fetchall()}
```

### Step 5: Assign plays_cols = value

```python
plays_cols = {r[1] for r in conn.execute('PRAGMA table_info(bandit_plays)').fetchall()}
```

### Step 6: Call conn.close()

```python
conn.close()
```


## Complete Example

```python
# Setup
# Fixtures: bandit_db

# Workflow
"B6: bandit_arms and bandit_plays must not have 'query' / 'query_text'."
conn = sqlite3.connect(str(bandit_db))
try:
    arms_cols = {r[1] for r in conn.execute('PRAGMA table_info(bandit_arms)').fetchall()}
    plays_cols = {r[1] for r in conn.execute('PRAGMA table_info(bandit_plays)').fetchall()}
finally:
    conn.close()
forbidden = {'query', 'query_text', 'raw_query', 'prompt'}
assert arms_cols.isdisjoint(forbidden)
assert plays_cols.isdisjoint(forbidden)
```

## Next Steps


---

*Source: test_bandit_core.py:340 | Complexity: Advanced | Last updated: 2026-05-05*