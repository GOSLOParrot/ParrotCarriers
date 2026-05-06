# How To: Returns Zone Distribution

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: get_retention_stats returns zone counts and averages.

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

### Step 1: 'get_retention_stats returns zone counts and averages.'

```python
'get_retention_stats returns zone counts and averages.'
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
assert result['total'] == 88
```

### Step 3: Assign mock_rows = value

```python
mock_rows = [{'lifecycle_zone': 'active', 'cnt': 50, 'avg_score': 0.92}, {'lifecycle_zone': 'warm', 'cnt': 20, 'avg_score': 0.65}, {'lifecycle_zone': 'cold', 'cnt': 10, 'avg_score': 0.35}, {'lifecycle_zone': 'archive', 'cnt': 5, 'avg_score': 0.12}, {'lifecycle_zone': 'forgotten', 'cnt': 3, 'avg_score': 0.02}]
```

**Verification:**
```python
assert result['active'] == 50
```

### Step 4: Assign engine._db.execute.return_value = mock_rows

```python
engine._db.execute.return_value = mock_rows
```

**Verification:**
```python
assert result['warm'] == 20
```

### Step 5: Assign result = _run(...)

```python
result = _run(tool())
```

**Verification:**
```python
assert result['cold'] == 10
```


## Complete Example

```python
# Workflow
'get_retention_stats returns zone counts and averages.'
tool, engine = self._get_tool()
mock_rows = [{'lifecycle_zone': 'active', 'cnt': 50, 'avg_score': 0.92}, {'lifecycle_zone': 'warm', 'cnt': 20, 'avg_score': 0.65}, {'lifecycle_zone': 'cold', 'cnt': 10, 'avg_score': 0.35}, {'lifecycle_zone': 'archive', 'cnt': 5, 'avg_score': 0.12}, {'lifecycle_zone': 'forgotten', 'cnt': 3, 'avg_score': 0.02}]
engine._db.execute.return_value = mock_rows
result = _run(tool())
assert result['success'] is True
assert result['total'] == 88
assert result['active'] == 50
assert result['warm'] == 20
assert result['cold'] == 10
assert result['archive'] == 5
assert result['forgotten'] == 3
```

## Next Steps


---

*Source: test_mcp_v33_tools.py:554 | Complexity: Intermediate | Last updated: 2026-05-05*