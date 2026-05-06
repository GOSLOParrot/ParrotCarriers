# How To: Observe Uses Pool Adapter Not Engine Store

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test observe uses pool adapter not engine store

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
assert result is not None
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr(_pool_adapter, '_pool', lambda: fake_pool)
```

**Verification:**
```python
assert fake_pool.store_calls, 'observe captured but did not go through pool_store'
```

### Step 3: Call tools_active.register_active_tools()

```python
tools_active.register_active_tools(_Server(), lambda: _LightEngine())
```

### Step 4: Assign content = 'We decided to use Postgres because the write pattern is transactional and we prefer strong consistency.'

```python
content = 'We decided to use Postgres because the write pattern is transactional and we prefer strong consistency.'
```

### Step 5: Assign result = asyncio.run(...)

```python
result = asyncio.run(registered['observe'](content=content))
```

**Verification:**
```python
assert result is not None
```

### Step 6: Assign profile_id = 'p'

```python
profile_id = 'p'
```

### Step 7: Assign _config = SimpleNamespace(...)

```python
_config = SimpleNamespace(mode=SimpleNamespace(value='a'))
```

**Verification:**
```python
assert fake_pool.store_calls, 'observe captured but did not go through pool_store'
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

    def store(self, *a, **kw):
        raise AssertionError('tools_active must not call engine.store; route via pool_store')
registered: dict = {}

class _Server:

    def tool(self):

        def _wrap(fn):
            registered[fn.__name__] = fn
            return fn
        return _wrap
tools_active.register_active_tools(_Server(), lambda: _LightEngine())
content = 'We decided to use Postgres because the write pattern is transactional and we prefer strong consistency.'
result = asyncio.run(registered['observe'](content=content))
assert result is not None
if result.get('captured'):
    assert fake_pool.store_calls, 'observe captured but did not go through pool_store'
```

## Next Steps


---

*Source: test_mcp_pool_adapter.py:177 | Complexity: Advanced | Last updated: 2026-05-05*