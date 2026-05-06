# How To: Evolution Budget 30Min Wall Time

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: After wall-time elapses, ``check_time()`` raises ``BudgetExhausted``.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.evolution.budget`

**Setup Required:**
```python
# Fixtures: learning_db, lock_dir, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'After wall-time elapses, ``check_time()`` raises ``BudgetExhausted``.'

```python
'After wall-time elapses, ``check_time()`` raises ``BudgetExhausted``.'
```

**Verification:**
```python
assert MAX_WALL_TIME_SEC == 1800
```

### Step 2: Assign t = value

```python
t = [1000000.0]
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr('superlocalmemory.evolution.budget.time.monotonic', _fake_monotonic)
```

### Step 4: Assign budget = EvolutionBudget(...)

```python
budget = EvolutionBudget(profile_id='default', learning_db=learning_db, lock_dir=lock_dir)
```

### Step 5: Call budget.check_time()

```python
budget.check_time()
```

### Step 6: Call budget.check_time()

```python
budget.check_time()
```


## Complete Example

```python
# Setup
# Fixtures: learning_db, lock_dir, monkeypatch

# Workflow
'After wall-time elapses, ``check_time()`` raises ``BudgetExhausted``.'
assert MAX_WALL_TIME_SEC == 1800
t = [1000000.0]

def _fake_monotonic() -> float:
    return t[0]
monkeypatch.setattr('superlocalmemory.evolution.budget.time.monotonic', _fake_monotonic)
budget = EvolutionBudget(profile_id='default', learning_db=learning_db, lock_dir=lock_dir)
with budget.cycle():
    t[0] += MAX_WALL_TIME_SEC - 1
    budget.check_time()
    t[0] += 2
    with pytest.raises(BudgetExhausted, match='wall_time'):
        budget.check_time()
```

## Next Steps


---

*Source: test_evolution_budget.py:127 | Complexity: Intermediate | Last updated: 2026-05-05*