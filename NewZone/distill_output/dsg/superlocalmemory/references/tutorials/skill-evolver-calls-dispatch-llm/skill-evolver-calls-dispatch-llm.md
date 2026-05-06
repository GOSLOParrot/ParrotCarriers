# How To: Skill Evolver Calls Dispatch Llm

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: _llm_call must delegate to evolution.llm_dispatch._dispatch_llm.

Records the call and asserts kwargs carry model/learning_db/profile_id
so SB-2 wiring is observable.

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

### Step 1: '_llm_call must delegate to evolution.llm_dispatch._dispatch_llm.\n\n    Records the call and asserts kwargs carry model/learning_db/profile_id\n    so SB-2 wiring is observable.\n    '

```python
'_llm_call must delegate to evolution.llm_dispatch._dispatch_llm.\n\n    Records the call and asserts kwargs carry model/learning_db/profile_id\n    so SB-2 wiring is observable.\n    '
```

**Verification:**
```python
assert out == 'DISPATCHED'
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr(se_mod, '_dispatch_llm', _fake_dispatch, raising=False)
```

**Verification:**
```python
assert len(captured) == 1
```

### Step 3: Assign cfg = _enabled_config(...)

```python
cfg = _enabled_config()
```

**Verification:**
```python
assert call['model'] in {'claude-haiku-4-5', 'claude-sonnet-4-6', 'ollama:llama3', 'ollama:qwen2.5'}
```

### Step 4: Assign evolver = SkillEvolver(...)

```python
evolver = SkillEvolver(db_path=str(tmp_path / 'x.db'), config=cfg)
```

**Verification:**
```python
assert call['profile_id']
```

### Step 5: Assign evolver._backend = 'claude'

```python
evolver._backend = 'claude'
```

**Verification:**
```python
assert call['max_tokens'] == 100
```

### Step 6: Assign out = evolver._llm_call(...)

```python
out = evolver._llm_call('prompt body', max_tokens=100, model='haiku')
```

**Verification:**
```python
assert out == 'DISPATCHED'
```

### Step 7: Assign call = value

```python
call = captured[0]
```

**Verification:**
```python
assert call['model'] in {'claude-haiku-4-5', 'claude-sonnet-4-6', 'ollama:llama3', 'ollama:qwen2.5'}
```

### Step 8: Call captured.append()

```python
captured.append({'prompt': prompt, 'model': model, 'learning_db': str(learning_db), 'profile_id': profile_id, 'max_tokens': max_tokens, 'cycle_id': cycle_id})
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'_llm_call must delegate to evolution.llm_dispatch._dispatch_llm.\n\n    Records the call and asserts kwargs carry model/learning_db/profile_id\n    so SB-2 wiring is observable.\n    '
from superlocalmemory.evolution import skill_evolver as se_mod
captured: list[dict[str, Any]] = []

def _fake_dispatch(prompt: str, *, model: str, learning_db, profile_id: str, max_tokens: int=500, cycle_id: str | None=None) -> str:
    captured.append({'prompt': prompt, 'model': model, 'learning_db': str(learning_db), 'profile_id': profile_id, 'max_tokens': max_tokens, 'cycle_id': cycle_id})
    return 'DISPATCHED'
monkeypatch.setattr(se_mod, '_dispatch_llm', _fake_dispatch, raising=False)
cfg = _enabled_config()
evolver = SkillEvolver(db_path=str(tmp_path / 'x.db'), config=cfg)
evolver._backend = 'claude'
out = evolver._llm_call('prompt body', max_tokens=100, model='haiku')
assert out == 'DISPATCHED'
assert len(captured) == 1
call = captured[0]
assert call['model'] in {'claude-haiku-4-5', 'claude-sonnet-4-6', 'ollama:llama3', 'ollama:qwen2.5'}
assert call['profile_id']
assert call['max_tokens'] == 100
```

## Next Steps


---

*Source: test_skill_evolver_firing.py:194 | Complexity: Advanced | Last updated: 2026-05-05*