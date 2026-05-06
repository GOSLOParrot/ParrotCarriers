# How To: Recall Records Implicit Feedback

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: mock

## Overview

Configuration example: _record_recall_hits is called with get_engine, query, and results.

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
# Fixtures: mock_emit
```

## Step-by-Step Guide

### Step 1: Assign pool.recall.return_value = value

```python
pool.recall.return_value = {'ok': True, 'results': results_data, 'result_count': 1, 'query_type': 'semantic'}
```


## Complete Example

```python
# Setup
# Fixtures: mock_emit

# Workflow
pool.recall.return_value = {'ok': True, 'results': results_data, 'result_count': 1, 'query_type': 'semantic'}
```

## Next Steps


---

*Source: test_mcp_recall_tool.py:155 | Complexity: Beginner | Last updated: 2026-05-05*