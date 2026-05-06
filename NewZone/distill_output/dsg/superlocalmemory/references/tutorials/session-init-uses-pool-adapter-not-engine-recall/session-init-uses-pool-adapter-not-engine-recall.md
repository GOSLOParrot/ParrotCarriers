# How To: Session Init Uses Pool Adapter Not Engine Recall

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test session init uses pool adapter not engine recall

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pytest`
- `types`
- `superlocalmemory.mcp`
- `superlocalmemory.mcp`
- `superlocalmemory.mcp`
- `superlocalmemory.mcp`
- `superlocalmemory.mcp._pool_adapter`
- `superlocalmemory.mcp`
- `superlocalmemory.mcp._pool_adapter`
- `superlocalmemory.mcp`
- `superlocalmemory.mcp._pool_adapter`
- `superlocalmemory.mcp`
- `superlocalmemory.hooks.auto_recall`
- `asyncio`
- `superlocalmemory.mcp`
- `asyncio`
- `superlocalmemory.mcp`

**Setup Required:**
```python
# Fixtures: monkeypatch
```

## Step-by-Step Guide

### Step 1: Assign fake_pool = _FakePool(...)

```python
fake_pool = _FakePool()
```

**Verification:**
```python
assert result['success'] is True
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr(_pool_adapter, '_pool', lambda: fake_pool)
```

**Verification:**
```python
assert fake_pool.recall_calls, 'session_init did not route through pool_recall'
```

### Step 3: Call tools_active.register_active_tools()

```python
tools_active.register_active_tools(_Server(), lambda: _LightEngine())
```

### Step 4: Assign result = asyncio.run(...)

```python
result = asyncio.run(registered['session_init'](project_path='/tmp/p'))
```

**Verification:**
```python
assert result['success'] is True
```

### Step 5: Assign profile_id = 'p'

```python
profile_id = 'p'
```

### Step 6: Assign _config = SimpleNamespace(...)

```python
_config = SimpleNamespace(mode=SimpleNamespace(value='a'))
```

### Step 7: Assign _adaptive_learner = None

```python
_adaptive_learner = None
```

### Step 8: Assign unknown = fn

```python
registered[fn.__name__] = fn
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch

# Workflow
import asyncio
from superlocalmemory.mcp import tools_active, _pool_adapter
fake_pool = _FakePool()
monkeypatch.setattr(_pool_adapter, '_pool', lambda: fake_pool)

class _LightEngine:
    profile_id = 'p'
    _config = SimpleNamespace(mode=SimpleNamespace(value='a'))
    _adaptive_learner = None

    def recall(self, *a, **kw):
        raise AssertionError('tools_active must not call engine.recall; route via pool_recall')
registered: dict = {}

class _Server:

    def tool(self):

        def _wrap(fn):
            registered[fn.__name__] = fn
            return fn
        return _wrap
tools_active.register_active_tools(_Server(), lambda: _LightEngine())
result = asyncio.run(registered['session_init'](project_path='/tmp/p'))
assert result['success'] is True
assert fake_pool.recall_calls, 'session_init did not route through pool_recall'
```

## Next Steps


---

*Source: test_mcp_pool_adapter.py:139 | Complexity: Advanced | Last updated: 2026-05-05*