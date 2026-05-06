# How To: Explicit Full Equals Default

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: test explicit full equals default

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

### Step 1: Assign engine_default = MemoryEngine(...)

```python
engine_default = MemoryEngine(mode_a_config)
```

**Verification:**
```python
assert engine_default.capabilities is engine_explicit.capabilities
```

### Step 2: Assign engine_explicit = MemoryEngine(...)

```python
engine_explicit = MemoryEngine(mode_a_config, capabilities=Capabilities.FULL)
```

**Verification:**
```python
assert engine_default.capabilities is engine_explicit.capabilities
```


## Complete Example

```python
# Setup
# Fixtures: mode_a_config

# Workflow
engine_default = MemoryEngine(mode_a_config)
engine_explicit = MemoryEngine(mode_a_config, capabilities=Capabilities.FULL)
assert engine_default.capabilities is engine_explicit.capabilities
```

## Next Steps


---

*Source: test_engine_capabilities.py:82 | Complexity: Beginner | Last updated: 2026-05-05*