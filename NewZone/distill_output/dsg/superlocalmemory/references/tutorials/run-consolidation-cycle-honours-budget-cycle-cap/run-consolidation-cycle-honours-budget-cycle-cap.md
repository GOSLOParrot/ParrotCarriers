# How To: Run Consolidation Cycle Honours Budget Cycle Cap

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: run_consolidation_cycle must open a budget.cycle() context.

We observe this by patching EvolutionBudget.cycle to count entries.

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

### Step 1: 'run_consolidation_cycle must open a budget.cycle() context.\n\n    We observe this by patching EvolutionBudget.cycle to count entries.\n    '

```python
'run_consolidation_cycle must open a budget.cycle() context.\n\n    We observe this by patching EvolutionBudget.cycle to count entries.\n    '
```

**Verification:**
```python
assert len(cycle_entries) == 1, f'run_consolidation_cycle did not open a budget cycle: {cycle_entries}'
```

### Step 2: Assign real_cycle = value

```python
real_cycle = budget_mod.EvolutionBudget.cycle
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr(budget_mod.EvolutionBudget, 'cycle', _spy_cycle)
```

### Step 4: Assign cfg = _enabled_config(...)

```python
cfg = _enabled_config()
```

### Step 5: Assign db_path = value

```python
db_path = tmp_path / 'x.db'
```

### Step 6: Assign evolver = SkillEvolver(...)

```python
evolver = SkillEvolver(db_path=str(db_path), config=cfg)
```

### Step 7: Call _provision_cost_log()

```python
_provision_cost_log(db_path)
```

### Step 8: Assign evolver._backend = 'claude'

```python
evolver._backend = 'claude'
```

### Step 9: Assign evolver._degradation.scan = value

```python
evolver._degradation.scan = lambda _p: []
```

### Step 10: Assign evolver._degradation.get_active_degraded = value

```python
evolver._degradation.get_active_degraded = lambda _p: []
```

### Step 11: Assign evolver._health.scan = value

```python
evolver._health.scan = lambda _p: []
```

### Step 12: Call evolver.run_consolidation_cycle()

```python
evolver.run_consolidation_cycle(profile_id='default')
```

**Verification:**
```python
assert len(cycle_entries) == 1, f'run_consolidation_cycle did not open a budget cycle: {cycle_entries}'
```

### Step 13: Call cycle_entries.append()

```python
cycle_entries.append(cycle_id or 'auto')
```

### Step 14: yield b

```python
yield b
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'run_consolidation_cycle must open a budget.cycle() context.\n\n    We observe this by patching EvolutionBudget.cycle to count entries.\n    '
from superlocalmemory.evolution import budget as budget_mod
from contextlib import contextmanager
cycle_entries: list[str] = []
real_cycle = budget_mod.EvolutionBudget.cycle

@contextmanager
def _spy_cycle(self, cycle_id=None):
    cycle_entries.append(cycle_id or 'auto')
    with real_cycle(self, cycle_id=cycle_id) as b:
        yield b
monkeypatch.setattr(budget_mod.EvolutionBudget, 'cycle', _spy_cycle)
cfg = _enabled_config()
db_path = tmp_path / 'x.db'
evolver = SkillEvolver(db_path=str(db_path), config=cfg)
_provision_cost_log(db_path)
evolver._backend = 'claude'
evolver._degradation.scan = lambda _p: []
evolver._degradation.get_active_degraded = lambda _p: []
evolver._health.scan = lambda _p: []
evolver.run_consolidation_cycle(profile_id='default')
assert len(cycle_entries) == 1, f'run_consolidation_cycle did not open a budget cycle: {cycle_entries}'
```

## Next Steps


---

*Source: test_skill_evolver_firing.py:330 | Complexity: Advanced | Last updated: 2026-05-05*