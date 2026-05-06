# How To: Skill Evolver Does Not Call Subprocess Directly Outside Safe Wrapper

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: SkillEvolver must not call subprocess.run directly. When the claude
CLI backend is exercised via _dispatch_llm, the call must go through
run_subprocess_safe.

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

### Step 1: 'SkillEvolver must not call subprocess.run directly. When the claude\n    CLI backend is exercised via _dispatch_llm, the call must go through\n    run_subprocess_safe.\n    '

```python
'SkillEvolver must not call subprocess.run directly. When the claude\n    CLI backend is exercised via _dispatch_llm, the call must go through\n    run_subprocess_safe.\n    '
```

**Verification:**
```python
assert direct_subproc_calls == [], f'SkillEvolver called subprocess.run directly: {direct_subproc_calls}'
```

### Step 2: Assign real_run = value

```python
real_run = real_subprocess.run
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr(real_subprocess, 'run', _trap_run)
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr(se_mod, '_dispatch_llm', lambda prompt, *, model, learning_db, profile_id, max_tokens=500, cycle_id=None: 'ok', raising=False)
```

### Step 5: Assign cfg = _enabled_config(...)

```python
cfg = _enabled_config()
```

### Step 6: Assign evolver = SkillEvolver(...)

```python
evolver = SkillEvolver(db_path=str(tmp_path / 'x.db'), config=cfg)
```

### Step 7: Assign evolver._backend = 'claude'

```python
evolver._backend = 'claude'
```

### Step 8: Call evolver._llm_call()

```python
evolver._llm_call('prompt', max_tokens=50, model='haiku')
```

**Verification:**
```python
assert direct_subproc_calls == [], f'SkillEvolver called subprocess.run directly: {direct_subproc_calls}'
```

### Step 9: Call direct_subproc_calls.append()

```python
direct_subproc_calls.append(repr(args))
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'SkillEvolver must not call subprocess.run directly. When the claude\n    CLI backend is exercised via _dispatch_llm, the call must go through\n    run_subprocess_safe.\n    '
from superlocalmemory.evolution import skill_evolver as se_mod
direct_subproc_calls: list[str] = []
import subprocess as real_subprocess
real_run = real_subprocess.run

def _trap_run(*args, **kw):
    direct_subproc_calls.append(repr(args))
    return real_run(*args, **kw)
monkeypatch.setattr(real_subprocess, 'run', _trap_run)
monkeypatch.setattr(se_mod, '_dispatch_llm', lambda prompt, *, model, learning_db, profile_id, max_tokens=500, cycle_id=None: 'ok', raising=False)
cfg = _enabled_config()
evolver = SkillEvolver(db_path=str(tmp_path / 'x.db'), config=cfg)
evolver._backend = 'claude'
evolver._llm_call('prompt', max_tokens=50, model='haiku')
assert direct_subproc_calls == [], f'SkillEvolver called subprocess.run directly: {direct_subproc_calls}'
```

## Next Steps


---

*Source: test_skill_evolver_firing.py:277 | Complexity: Advanced | Last updated: 2026-05-05*