# How To: Forget Dry Run Returns Zone Distribution

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: forget dry_run=True returns zone counts from fact_retention.

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

### Step 1: 'forget dry_run=True returns zone counts from fact_retention.'

```python
'forget dry_run=True returns zone counts from fact_retention.'
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
mock_rows = [{'lifecycle_zone': 'active', 'cnt': 50}, {'lifecycle_zone': 'warm', 'cnt': 20}, {'lifecycle_zone': 'cold', 'cnt': 10}, {'lifecycle_zone': 'archive', 'cnt': 5}, {'lifecycle_zone': 'forgotten', 'cnt': 3}]
```

**Verification:**
```python
assert result['dry_run_zones']['active'] == 50
```

### Step 4: Assign engine._db.execute.return_value = mock_rows

```python
engine._db.execute.return_value = mock_rows
```

**Verification:**
```python
assert result['dry_run_zones']['warm'] == 20
```

### Step 5: Assign result = _run(...)

```python
result = _run(tool())
```

**Verification:**
```python
assert result['dry_run_zones']['cold'] == 10
```


## Complete Example

```python
# Workflow
'forget dry_run=True returns zone counts from fact_retention.'
tool, engine = self._get_tool()
mock_rows = [{'lifecycle_zone': 'active', 'cnt': 50}, {'lifecycle_zone': 'warm', 'cnt': 20}, {'lifecycle_zone': 'cold', 'cnt': 10}, {'lifecycle_zone': 'archive', 'cnt': 5}, {'lifecycle_zone': 'forgotten', 'cnt': 3}]
engine._db.execute.return_value = mock_rows
result = _run(tool())
assert result['success'] is True
assert result['total'] == 88
assert result['dry_run_zones']['active'] == 50
assert result['dry_run_zones']['warm'] == 20
assert result['dry_run_zones']['cold'] == 10
```

## Next Steps


---

*Source: test_mcp_v33_tools.py:206 | Complexity: Intermediate | Last updated: 2026-05-05*