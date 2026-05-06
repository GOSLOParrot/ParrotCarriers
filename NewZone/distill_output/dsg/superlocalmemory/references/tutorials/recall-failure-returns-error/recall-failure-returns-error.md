# How To: Recall Failure Returns Error

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: mock

## Overview

Configuration example: When pool.recall returns ok=False, tool returns success=False.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `asyncio`
- `unittest.mock`
- `pytest`
- `superlocalmemory.mcp.tools_core`

**Setup Required:**
```python
# Fixtures: mock_emit, mock_record
```

## Step-by-Step Guide

### Step 1: Assign pool.recall.return_value = value

```python
pool.recall.return_value = {'ok': False, 'error': 'Index corrupted'}
```


## Complete Example

```python
# Setup
# Fixtures: mock_emit, mock_record

# Workflow
pool.recall.return_value = {'ok': False, 'error': 'Index corrupted'}
```

## Next Steps


---

*Source: test_mcp_recall_tool.py:92 | Complexity: Beginner | Last updated: 2026-05-05*