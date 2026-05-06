# How To: Full Engine Loads Embedder

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: test full engine loads embedder

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
assert engine._embedder is not None
```

### Step 2: Call engine.initialize()

```python
engine.initialize()
```

**Verification:**
```python
assert engine._retrieval_engine is not None
```


## Complete Example

```python
# Setup
# Fixtures: mode_a_config

# Workflow
engine = MemoryEngine(mode_a_config, capabilities=Capabilities.FULL)
engine.initialize()
assert engine._embedder is not None
assert engine._retrieval_engine is not None
```

## Next Steps


---

*Source: test_engine_capabilities.py:87 | Complexity: Beginner | Last updated: 2026-05-05*