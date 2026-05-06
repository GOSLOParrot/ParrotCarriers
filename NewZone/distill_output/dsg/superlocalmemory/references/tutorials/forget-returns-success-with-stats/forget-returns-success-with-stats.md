# How To: Forget Returns Success With Stats

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: forget dry_run=False returns zone counts from fact_retention.

## Prerequisites

**Required Modules:**
- `__future__`
- `asyncio`
- `dataclasses`
- `unittest.mock`
- `pytest`
- `superlocalmemory.mcp.tools_v33`
- `superlocalmemory.mcp.tools_v33`
- `superlocalmemory.mcp.tools_v33`
- `superlocalmemory.mcp.tools_core`
- `superlocalmemory.mcp.tools_v33`
- `superlocalmemory.mcp.tools_active`
- `superlocalmemory.mcp.tools_v33`
- `superlocalmemory.mcp.tools_v28`
- `superlocalmemory.mcp.tools_v33`
- `superlocalmemory.mcp.tools_v33`
- `superlocalmemory.mcp.tools_v33`
- `superlocalmemory.mcp.tools_v33`
- `superlocalmemory.mcp.tools_v33`
- `superlocalmemory.mcp.tools_v33`
- `superlocalmemory.mcp.tools_v33`


## Step-by-Step Guide

### Step 1: 'forget dry_run=False returns zone counts from fact_retention.'

```python
'forget dry_run=False returns zone counts from fact_retention.'
```

**Verification:**
```python
assert result['success'] is True
```

### Step 2: Assign unknown = self._get_tool(...)

```python
tool, engine = self._get_tool()
```

**Verification:**
```python
assert result['total'] == 100
```

### Step 3: Assign mock_result = value

```python
mock_result = {'total': 100, 'active': 50, 'warm': 20, 'cold': 15, 'archive': 10, 'forgotten': 5, 'transitions': 8}
```

**Verification:**
```python
assert result['transitions'] == 8
```

### Step 4: Assign MockSched.return_value.run_decay_cycle.return_value = mock_result

```python
MockSched.return_value.run_decay_cycle.return_value = mock_result
```

**Verification:**
```python
assert result['dry_run'] is False
```

### Step 5: Assign result = _run(...)

```python
result = _run(tool(dry_run=False))
```


## Complete Example

```python
# Workflow
'forget dry_run=False returns zone counts from fact_retention.'
tool, engine = self._get_tool()
mock_result = {'total': 100, 'active': 50, 'warm': 20, 'cold': 15, 'archive': 10, 'forgotten': 5, 'transitions': 8}
with patch('superlocalmemory.learning.forgetting_scheduler.ForgettingScheduler') as MockSched, patch('superlocalmemory.math.ebbinghaus.EbbinghausCurve'):
    MockSched.return_value.run_decay_cycle.return_value = mock_result
    result = _run(tool(dry_run=False))
assert result['success'] is True
assert result['total'] == 100
assert result['transitions'] == 8
assert result['dry_run'] is False
```

## Next Steps


---

*Source: test_mcp_v33_tools.py:178 | Complexity: Intermediate | Last updated: 2026-05-05*