# How To: Full Engine No Capability Error

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: test full engine no capability error

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.core.engine_capabilities`
- `superlocalmemory.storage.models`
- `pickle`

**Setup Required:**
```python
# Fixtures: mode_a_config
```

## Step-by-Step Guide

### Step 1: Assign engine = MemoryEngine(...)

```python
engine = MemoryEngine(mode_a_config, capabilities=Capabilities.FULL)
```

**Verification:**
```python
assert response is not None
```

### Step 2: Call engine.initialize()

```python
engine.initialize()
```

### Step 3: Assign response = engine.recall(...)

```python
response = engine.recall('query on empty db')
```

**Verification:**
```python
assert response is not None
```


## Complete Example

```python
# Setup
# Fixtures: mode_a_config

# Workflow
engine = MemoryEngine(mode_a_config, capabilities=Capabilities.FULL)
engine.initialize()
response = engine.recall('query on empty db')
assert response is not None
```

## Next Steps


---

*Source: test_engine_capabilities.py:94 | Complexity: Beginner | Last updated: 2026-05-05*