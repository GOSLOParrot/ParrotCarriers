# How To: Returns Prompts From Db

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: get_soft_prompts returns formatted prompts from DB.

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

### Step 1: 'get_soft_prompts returns formatted prompts from DB.'

```python
'get_soft_prompts returns formatted prompts from DB.'
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
assert result['count'] == 1
```

### Step 3: Assign mock_row = value

```python
mock_row = {'prompt_id': 'sp-001', 'category': 'tech_preference', 'content': 'User prefers Python 3.13', 'confidence': 0.85, 'effectiveness': 0.72, 'token_count': 12, 'version': 1, 'created_at': '2026-03-30 10:00:00'}
```

**Verification:**
```python
assert result['prompts'][0]['prompt_id'] == 'sp-001'
```

### Step 4: Assign engine._db.execute.return_value = value

```python
engine._db.execute.return_value = [mock_row]
```

**Verification:**
```python
assert result['prompts'][0]['confidence'] == 0.85
```

### Step 5: Assign result = _run(...)

```python
result = _run(tool())
```

**Verification:**
```python
assert result['success'] is True
```


## Complete Example

```python
# Workflow
'get_soft_prompts returns formatted prompts from DB.'
tool, engine = self._get_tool()
mock_row = {'prompt_id': 'sp-001', 'category': 'tech_preference', 'content': 'User prefers Python 3.13', 'confidence': 0.85, 'effectiveness': 0.72, 'token_count': 12, 'version': 1, 'created_at': '2026-03-30 10:00:00'}
engine._db.execute.return_value = [mock_row]
result = _run(tool())
assert result['success'] is True
assert result['count'] == 1
assert result['prompts'][0]['prompt_id'] == 'sp-001'
assert result['prompts'][0]['confidence'] == 0.85
```

## Next Steps


---

*Source: test_mcp_v33_tools.py:424 | Complexity: Intermediate | Last updated: 2026-05-05*