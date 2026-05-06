# How To: Origin Guard Allows Hook Request

**Difficulty**: Beginner
**Estimated Time**: 5 minutes

## Overview

Configuration example: test origin guard allows hook request

## Prerequisites

**Required Modules:**
- `__future__`
- `pathlib`
- `pytest`
- `superlocalmemory.core`
- `superlocalmemory.hooks`


## Step-by-Step Guide

### Step 1: Assign headers = value

```python
headers = {'Content-Type': 'application/json', 'X-SLM-Hook-Token': 'deadbeef'}
```


## Complete Example

```python
# Workflow
headers = {'Content-Type': 'application/json', 'X-SLM-Hook-Token': 'deadbeef'}
```

## Next Steps


---

*Source: test_prewarm_auth.py:76 | Complexity: Beginner | Last updated: 2026-05-05*