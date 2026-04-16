# How To: Moondream Processor

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: Create and manage MoondreamLocalProcessor lifecycle.

## Prerequisites

**Required Modules:**
- `asyncio`
- `os`
- `pathlib`
- `typing`
- `numpy`
- `pytest`
- `torch`
- `PIL`
- `av`
- `vision_agents.plugins.moondream`
- `vision_agents.plugins.moondream.moondream_utils`
- `logging`


## Step-by-Step Guide

### Step 1: 'Create and manage MoondreamLocalProcessor lifecycle.'

```python
'Create and manage MoondreamLocalProcessor lifecycle.'
```

### Step 2: Assign processor = LocalDetectionProcessor(...)

```python
processor = LocalDetectionProcessor(force_cpu=True)
```

### Step 3: yield processor

```python
yield processor
```

### Step 4: Call processor.close()

```python
processor.close()
```


## Complete Example

```python
# Workflow
'Create and manage MoondreamLocalProcessor lifecycle.'
processor = LocalDetectionProcessor(force_cpu=True)
try:
    yield processor
finally:
    processor.close()
```

## Next Steps


---

*Source: test_moondream_local.py:44 | Complexity: Advanced | Last updated: 2026-04-12*