# How To: Recall Emits Memory Recalled Event

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: mock

## Overview

Configuration example: On success, _emit_event('memory.recalled', ...) is called.

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
pool.recall.return_value = {'ok': True, 'results': [], 'result_count': 0, 'query_type': 'fts'}
```


## Complete Example

```python
# Setup
# Fixtures: mock_emit, mock_record

# Workflow
pool.recall.return_value = {'ok': True, 'results': [], 'result_count': 0, 'query_type': 'fts'}
```

## Next Steps


---

*Source: test_mcp_recall_tool.py:133 | Complexity: Beginner | Last updated: 2026-05-05*