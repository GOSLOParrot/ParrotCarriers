# How To: Choose Converges To Rewarded Arm

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: With one arm always rewarding 1.0 and others 0.0, selection > 80 %.

To keep the test deterministic without mocking the RNG, we directly
seed bandit_arms rows with strong posteriors for the "winning" arm
and weak posteriors for all others, then verify choose() picks it
overwhelmingly.

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

### Step 1: 'With one arm always rewarding 1.0 and others 0.0, selection > 80 %.\n\n    To keep the test deterministic without mocking the RNG, we directly\n    seed bandit_arms rows with strong posteriors for the "winning" arm\n    and weak posteriors for all others, then verify choose() picks it\n    overwhelmingly.\n    '

```python
'With one arm always rewarding 1.0 and others 0.0, selection > 80 %.\n\n    To keep the test deterministic without mocking the RNG, we directly\n    seed bandit_arms rows with strong posteriors for the "winning" arm\n    and weak posteriors for all others, then verify choose() picks it\n    overwhelmingly.\n    '
```

**Verification:**
```python
assert hits / trials > 0.8, f'winning selected {hits}/{trials}'
```

### Step 2: Assign cache = _BanditCache(...)

```python
cache = _BanditCache(max_entries=16)
```

### Step 3: Assign b = ContextualBandit(...)

```python
b = ContextualBandit(bandit_db, profile_id='conv', cache=cache)
```

### Step 4: Assign stratum = compute_stratum(...)

```python
stratum = compute_stratum(_ctx())
```

### Step 5: Assign winning = 'semantic_heavy_2'

```python
winning = 'semantic_heavy_2'
```

### Step 6: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(bandit_db), isolation_level=None)
```

### Step 7: Call cache.clear()

```python
cache.clear()
```

### Step 8: Assign hits = 0

```python
hits = 0
```

### Step 9: Assign trials = 100

```python
trials = 100
```

**Verification:**
```python
assert hits / trials > 0.8, f'winning selected {hits}/{trials}'
```

### Step 10: Call conn.close()

```python
conn.close()
```

### Step 11: Assign ch = b.choose(...)

```python
ch = b.choose(_ctx(), query_id=f'c-{i}')
```

### Step 12: Call conn.execute()

```python
conn.execute("INSERT OR REPLACE INTO bandit_arms (profile_id, stratum, arm_id, alpha, beta, plays,  last_played_at) VALUES (?, ?, ?, ?, ?, 0, '2026-01-01T00:00:00')", ('conv', stratum, arm_id, alpha, beta))
```

### Step 13: Assign unknown = value

```python
alpha, beta = (500.0, 1.0)
```

### Step 14: Assign unknown = value

```python
alpha, beta = (1.0, 500.0)
```


## Complete Example

```python
# Setup
# Fixtures: bandit_db

# Workflow
'With one arm always rewarding 1.0 and others 0.0, selection > 80 %.\n\n    To keep the test deterministic without mocking the RNG, we directly\n    seed bandit_arms rows with strong posteriors for the "winning" arm\n    and weak posteriors for all others, then verify choose() picks it\n    overwhelmingly.\n    '
cache = _BanditCache(max_entries=16)
b = ContextualBandit(bandit_db, profile_id='conv', cache=cache)
stratum = compute_stratum(_ctx())
winning = 'semantic_heavy_2'
conn = sqlite3.connect(str(bandit_db), isolation_level=None)
try:
    for arm_id in ARM_CATALOG:
        if arm_id == winning:
            alpha, beta = (500.0, 1.0)
        else:
            alpha, beta = (1.0, 500.0)
        conn.execute("INSERT OR REPLACE INTO bandit_arms (profile_id, stratum, arm_id, alpha, beta, plays,  last_played_at) VALUES (?, ?, ?, ?, ?, 0, '2026-01-01T00:00:00')", ('conv', stratum, arm_id, alpha, beta))
finally:
    conn.close()
cache.clear()
hits = 0
trials = 100
for i in range(trials):
    ch = b.choose(_ctx(), query_id=f'c-{i}')
    if ch.arm_id == winning:
        hits += 1
assert hits / trials > 0.8, f'winning selected {hits}/{trials}'
```

## Next Steps


---

*Source: test_bandit_core.py:362 | Complexity: Advanced | Last updated: 2026-05-05*