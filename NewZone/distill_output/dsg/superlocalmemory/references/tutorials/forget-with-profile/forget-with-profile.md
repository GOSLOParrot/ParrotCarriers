# How To: Forget With Profile

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: forget tool uses provided profile_id.

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

### Step 1: 'forget tool uses provided profile_id.'

```python
'forget tool uses provided profile_id.'
```

**Verification:**
```python
assert result['success'] is True
```

### Step 2: Assign unknown = self._get_tool(...)

```python
tool, engine = self._get_tool()
```

### Step 3: Assign mock_result = value

```python
mock_result = {'total': 0, 'active': 0, 'warm': 0, 'cold': 0, 'archive': 0, 'forgotten': 0, 'transitions': 0}
```

**Verification:**
```python
assert result['success'] is True
```

### Step 4: Call MockSched.return_value.run_decay_cycle.assert_called_once_with()

```python
MockSched.return_value.run_decay_cycle.assert_called_once_with('custom-profile', force=True)
```

### Step 5: Assign MockSched.return_value.run_decay_cycle.return_value = mock_result

```python
MockSched.return_value.run_decay_cycle.return_value = mock_result
```

### Step 6: Assign result = _run(...)

```python
result = _run(tool(profile_id='custom-profile', dry_run=False))
```


## Complete Example

```python
# Workflow
'forget tool uses provided profile_id.'
tool, engine = self._get_tool()
mock_result = {'total': 0, 'active': 0, 'warm': 0, 'cold': 0, 'archive': 0, 'forgotten': 0, 'transitions': 0}
with patch('superlocalmemory.learning.forgetting_scheduler.ForgettingScheduler') as MockSched, patch('superlocalmemory.math.ebbinghaus.EbbinghausCurve'):
    MockSched.return_value.run_decay_cycle.return_value = mock_result
    result = _run(tool(profile_id='custom-profile', dry_run=False))
assert result['success'] is True
MockSched.return_value.run_decay_cycle.assert_called_once_with('custom-profile', force=True)
```

## Next Steps


---

*Source: test_mcp_v33_tools.py:227 | Complexity: Intermediate | Last updated: 2026-05-05*