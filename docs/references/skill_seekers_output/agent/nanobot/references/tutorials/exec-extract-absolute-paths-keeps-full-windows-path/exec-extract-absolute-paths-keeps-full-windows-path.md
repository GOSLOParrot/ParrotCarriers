# How To: Exec Extract Absolute Paths Keeps Full Windows Path

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: test exec extract absolute paths keeps full windows path

## Prerequisites

**Required Modules:**
- `typing`
- `nanobot.agent.tools.base`
- `nanobot.agent.tools.registry`
- `nanobot.agent.tools.shell`


## Step-by-Step Guide

### Step 1: Assign cmd = 'type C:\\user\\workspace\\txt'

```python
cmd = 'type C:\\user\\workspace\\txt'
```

**Verification:**
```python
assert paths == ['C:\\user\\workspace\\txt']
```

### Step 2: Assign paths = ExecTool._extract_absolute_paths(...)

```python
paths = ExecTool._extract_absolute_paths(cmd)
```

**Verification:**
```python
assert paths == ['C:\\user\\workspace\\txt']
```


## Complete Example

```python
# Workflow
cmd = 'type C:\\user\\workspace\\txt'
paths = ExecTool._extract_absolute_paths(cmd)
assert paths == ['C:\\user\\workspace\\txt']
```

## Next Steps


---

*Source: test_tool_validation.py:92 | Complexity: Beginner | Last updated: 2026-04-12*