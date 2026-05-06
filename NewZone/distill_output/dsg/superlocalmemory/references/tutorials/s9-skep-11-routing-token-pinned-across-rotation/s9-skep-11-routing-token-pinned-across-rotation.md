# How To: S9 Skep 11 Routing Token Pinned Across Rotation

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: ShadowRouter.route_query uses the token SNAPSHOT from __init__,
so a mid-test rotate does not flip arm assignments for in-flight qids.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `time`
- `pytest`
- `superlocalmemory.learning`
- `superlocalmemory.learning.shadow_test`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.core`
- `superlocalmemory.core.security_primitives`
- `superlocalmemory.core.security_primitives`
- `superlocalmemory.core.security_primitives`
- `superlocalmemory.core.security_primitives`
- `superlocalmemory.evolution.llm_dispatch`
- `superlocalmemory.hooks.user_prompt_rehash_hook`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'ShadowRouter.route_query uses the token SNAPSHOT from __init__,\n    so a mid-test rotate does not flip arm assignments for in-flight qids.\n    '

```python
'ShadowRouter.route_query uses the token SNAPSHOT from __init__,\n    so a mid-test rotate does not flip arm assignments for in-flight qids.\n    '
```

**Verification:**
```python
assert arms_before == arms_after, f'route_query must be stable across install_token rotation; before={arms_before} after={arms_after}'
```

### Step 2: Assign tok1 = value

```python
tok1 = 'a' * 64
```

### Step 3: Assign tok2 = value

```python
tok2 = 'b' * 64
```

### Step 4: Assign tokens = iter(...)

```python
tokens = iter([tok1])
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr(sr, 'ensure_install_token', lambda: next(tokens, tok2))
```

### Step 6: Assign router = sr.ShadowRouter(...)

```python
router = sr.ShadowRouter(memory_db=str(tmp_path / 'm.db'), learning_db=str(tmp_path / 'l.db'), profile_id='p')
```

### Step 7: Assign arms_before = value

```python
arms_before = [router.route_query(f'q{i}') for i in range(20)]
```

### Step 8: Assign arms_after = value

```python
arms_after = [router.route_query(f'q{i}') for i in range(20)]
```

**Verification:**
```python
assert arms_before == arms_after, f'route_query must be stable across install_token rotation; before={arms_before} after={arms_after}'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'ShadowRouter.route_query uses the token SNAPSHOT from __init__,\n    so a mid-test rotate does not flip arm assignments for in-flight qids.\n    '
from superlocalmemory.core import shadow_router as sr
tok1 = 'a' * 64
tok2 = 'b' * 64
tokens = iter([tok1])
monkeypatch.setattr(sr, 'ensure_install_token', lambda: next(tokens, tok2))
router = sr.ShadowRouter(memory_db=str(tmp_path / 'm.db'), learning_db=str(tmp_path / 'l.db'), profile_id='p')
arms_before = [router.route_query(f'q{i}') for i in range(20)]
arms_after = [router.route_query(f'q{i}') for i in range(20)]
assert arms_before == arms_after, f'route_query must be stable across install_token rotation; before={arms_before} after={arms_after}'
```

## Next Steps


---

*Source: test_s9_w6_skeptic.py:100 | Complexity: Advanced | Last updated: 2026-05-05*