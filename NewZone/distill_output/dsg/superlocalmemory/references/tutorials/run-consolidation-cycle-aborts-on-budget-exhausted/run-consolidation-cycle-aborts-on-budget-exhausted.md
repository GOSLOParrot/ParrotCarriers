# How To: Run Consolidation Cycle Aborts On Budget Exhausted

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: If budget.cycle() raises BudgetExhausted, the evolver must return
cleanly (no exception propagated to the caller).

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `os`
- `dataclasses`
- `pathlib`
- `typing`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.evolution.skill_evolver`
- `superlocalmemory.hooks`
- `sqlite3`
- `superlocalmemory.evolution`
- `superlocalmemory.evolution`
- `types`
- `superlocalmemory.evolution`
- `subprocess`
- `superlocalmemory.evolution.budget`
- `superlocalmemory.evolution`
- `contextlib`
- `superlocalmemory.evolution`
- `superlocalmemory.core`
- `superlocalmemory.evolution`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'If budget.cycle() raises BudgetExhausted, the evolver must return\n    cleanly (no exception propagated to the caller).'

```python
'If budget.cycle() raises BudgetExhausted, the evolver must return\n    cleanly (no exception propagated to the caller).'
```

**Verification:**
```python
assert isinstance(result, dict)
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr(budget_mod.EvolutionBudget, 'cycle', _raise)
```

**Verification:**
```python
assert result.get('aborted') is True or result.get('budget_exhausted') is True
```

### Step 3: Assign cfg = _enabled_config(...)

```python
cfg = _enabled_config()
```

### Step 4: Assign evolver = SkillEvolver(...)

```python
evolver = SkillEvolver(db_path=str(tmp_path / 'x.db'), config=cfg)
```

### Step 5: Assign evolver._backend = 'claude'

```python
evolver._backend = 'claude'
```

### Step 6: Assign result = evolver.run_consolidation_cycle(...)

```python
result = evolver.run_consolidation_cycle(profile_id='default')
```

**Verification:**
```python
assert isinstance(result, dict)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'If budget.cycle() raises BudgetExhausted, the evolver must return\n    cleanly (no exception propagated to the caller).'
from superlocalmemory.evolution import budget as budget_mod

def _raise(self, cycle_id=None):
    raise budget_mod.BudgetExhausted('cycles_per_day', 'test')
monkeypatch.setattr(budget_mod.EvolutionBudget, 'cycle', _raise)
cfg = _enabled_config()
evolver = SkillEvolver(db_path=str(tmp_path / 'x.db'), config=cfg)
evolver._backend = 'claude'
result = evolver.run_consolidation_cycle(profile_id='default')
assert isinstance(result, dict)
assert result.get('aborted') is True or result.get('budget_exhausted') is True
```

## Next Steps


---

*Source: test_skill_evolver_firing.py:371 | Complexity: Advanced | Last updated: 2026-05-05*