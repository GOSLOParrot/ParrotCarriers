# How To: Recall Success Returns Results

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: mock

## Overview

Configuration example: Successful recall returns success=True with results list.

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
pool.recall.return_value = {'ok': True, 'results': [{'fact_id': 'f-1', 'content': 'Python is great', 'score': 0.9}], 'result_count': 1, 'query_type': 'semantic'}
```


## Complete Example

```python
# Setup
# Fixtures: mock_emit, mock_record

# Workflow
pool.recall.return_value = {'ok': True, 'results': [{'fact_id': 'f-1', 'content': 'Python is great', 'score': 0.9}], 'result_count': 1, 'query_type': 'semantic'}
```

## Next Steps


---

*Source: test_mcp_recall_tool.py:68 | Complexity: Beginner | Last updated: 2026-05-05*