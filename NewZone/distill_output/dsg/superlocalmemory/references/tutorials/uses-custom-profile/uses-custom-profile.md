# How To: Uses Custom Profile

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: get_retention_stats uses provided profile_id.

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

### Step 1: 'get_retention_stats uses provided profile_id.'

```python
'get_retention_stats uses provided profile_id.'
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
assert result['profile'] == 'custom'
```

### Step 3: Assign engine._db.execute.return_value = value

```python
engine._db.execute.return_value = []
```

**Verification:**
```python
assert call_args[0][1] == ('custom',)
```

### Step 4: Assign result = _run(...)

```python
result = _run(tool(profile_id='custom'))
```

**Verification:**
```python
assert result['success'] is True
```

### Step 5: Assign call_args = value

```python
call_args = engine._db.execute.call_args
```

**Verification:**
```python
assert call_args[0][1] == ('custom',)
```


## Complete Example

```python
# Workflow
'get_retention_stats uses provided profile_id.'
tool, engine = self._get_tool()
engine._db.execute.return_value = []
result = _run(tool(profile_id='custom'))
assert result['success'] is True
assert result['profile'] == 'custom'
call_args = engine._db.execute.call_args
assert call_args[0][1] == ('custom',)
```

## Next Steps


---

*Source: test_mcp_v33_tools.py:598 | Complexity: Intermediate | Last updated: 2026-05-05*