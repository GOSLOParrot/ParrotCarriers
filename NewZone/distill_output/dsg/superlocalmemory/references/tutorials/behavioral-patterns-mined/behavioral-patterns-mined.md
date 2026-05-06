# How To: Behavioral Patterns Mined

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: run_maintenance behavioral section uses correct ConsolidationWorker args.

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

### Step 1: 'run_maintenance behavioral section uses correct ConsolidationWorker args.'

```python
'run_maintenance behavioral section uses correct ConsolidationWorker args.'
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
assert result['behavioral']['patterns_mined'] == 7
```

### Step 3: Assign init_args = value

```python
init_args = MockCW.call_args[0]
```

### Step 4: Assign expected_memory = value

```python
expected_memory = engine._db.db_path
```

### Step 5: Assign expected_learning = value

```python
expected_learning = engine._db.db_path.parent / 'learning.db'
```

### Step 6: Call MockCW.assert_called_once_with()

```python
MockCW.assert_called_once_with(expected_memory, expected_learning)
```

### Step 7: Assign MockSched.return_value.run_decay_cycle.return_value = value

```python
MockSched.return_value.run_decay_cycle.return_value = {'total': 0, 'active': 0, 'warm': 0, 'cold': 0, 'archive': 0, 'forgotten': 0, 'transitions': 0}
```

### Step 8: Assign MockCW.return_value._generate_patterns.return_value = 7

```python
MockCW.return_value._generate_patterns.return_value = 7
```

### Step 9: Assign result = _run(...)

```python
result = _run(tool())
```


## Complete Example

```python
# Workflow
'run_maintenance behavioral section uses correct ConsolidationWorker args.'
tool, engine = self._get_tool()
with patch('superlocalmemory.mcp.tools_v33._try_daemon_post', return_value=None), patch('superlocalmemory.learning.consolidation_worker.ConsolidationWorker', autospec=True) as MockCW, patch('superlocalmemory.core.maintenance.run_maintenance', return_value={'updated': 0}), patch('superlocalmemory.learning.forgetting_scheduler.ForgettingScheduler') as MockSched, patch('superlocalmemory.math.ebbinghaus.EbbinghausCurve'):
    MockSched.return_value.run_decay_cycle.return_value = {'total': 0, 'active': 0, 'warm': 0, 'cold': 0, 'archive': 0, 'forgotten': 0, 'transitions': 0}
    MockCW.return_value._generate_patterns.return_value = 7
    result = _run(tool())
assert result['success'] is True
assert result['behavioral']['patterns_mined'] == 7
init_args = MockCW.call_args[0]
expected_memory = engine._db.db_path
expected_learning = engine._db.db_path.parent / 'learning.db'
MockCW.assert_called_once_with(expected_memory, expected_learning)
```

## Next Steps


---

*Source: test_mcp_v33_tools.py:629 | Complexity: Advanced | Last updated: 2026-05-05*