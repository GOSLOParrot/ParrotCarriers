# How To: Remember Success Returns Fact Ids

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: mock

## Overview

Configuration example: Successful store returns success=True with fact_ids list.

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
# Fixtures: mock_wp_mod, _wp_create, mock_emit
```

## Step-by-Step Guide

### Step 1: Assign pool.store.return_value = value

```python
pool.store.return_value = {'ok': True, 'fact_ids': ['f-001', 'f-002'], 'count': 2}
```


## Complete Example

```python
# Setup
# Fixtures: mock_wp_mod, _wp_create, mock_emit

# Workflow
pool.store.return_value = {'ok': True, 'fact_ids': ['f-001', 'f-002'], 'count': 2}
```

## Next Steps


---

*Source: test_mcp_remember_tool.py:74 | Complexity: Beginner | Last updated: 2026-05-05*