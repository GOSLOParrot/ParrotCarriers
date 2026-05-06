# How To: Quantize Returns Success With Stats

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: quantize tool (dry_run=False) returns EAP cycle stats.

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

### Step 1: 'quantize tool (dry_run=False) returns EAP cycle stats.'

```python
'quantize tool (dry_run=False) returns EAP cycle stats.'
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
assert result['downgrades'] == 10
```

### Step 3: Assign mock_result = value

```python
mock_result = {'total': 50, 'downgrades': 10, 'upgrades': 3, 'skipped': 35, 'deleted': 2, 'errors': 0}
```

**Verification:**
```python
assert result['upgrades'] == 3
```

### Step 4: Assign MockEAP.return_value.run_eap_cycle.return_value = mock_result

```python
MockEAP.return_value.run_eap_cycle.return_value = mock_result
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
'quantize tool (dry_run=False) returns EAP cycle stats.'
tool, engine = self._get_tool()
mock_result = {'total': 50, 'downgrades': 10, 'upgrades': 3, 'skipped': 35, 'deleted': 2, 'errors': 0}
with patch('superlocalmemory.dynamics.eap_scheduler.EAPScheduler') as MockEAP, patch('superlocalmemory.math.ebbinghaus.EbbinghausCurve'), patch('superlocalmemory.storage.quantized_store.QuantizedEmbeddingStore'), patch('superlocalmemory.math.polar_quant.PolarQuantEncoder'), patch('superlocalmemory.math.qjl.QJLEncoder'):
    MockEAP.return_value.run_eap_cycle.return_value = mock_result
    result = _run(tool(dry_run=False))
assert result['success'] is True
assert result['downgrades'] == 10
assert result['upgrades'] == 3
assert result['dry_run'] is False
```

## Next Steps


---

*Source: test_mcp_v33_tools.py:287 | Complexity: Intermediate | Last updated: 2026-05-05*