# How To: Redacts Inside Nested Lists And Dicts

**Difficulty**: Beginner
**Estimated Time**: 5 minutes

## Overview

Configuration example: test redacts inside nested lists and dicts

## Prerequisites

**Required Modules:**
- `__future__`
- `pytest`
- `superlocalmemory.server.routes.brain`
- `json`
- `json`
- `json`
- `json`


## Step-by-Step Guide

### Step 1: Assign payload = value

```python
payload = {'topics': [{'name': 'safe', 'nested': {'token': 'AKIAIOSFODNN7EXAMPLE'}}], 'entities': ['AKIAABCDEFGHIJKLMNOP', 'Qualixar']}
```


## Complete Example

```python
# Workflow
payload = {'topics': [{'name': 'safe', 'nested': {'token': 'AKIAIOSFODNN7EXAMPLE'}}], 'entities': ['AKIAABCDEFGHIJKLMNOP', 'Qualixar']}
```

## Next Steps


---

*Source: test_preference_redaction.py:68 | Complexity: Beginner | Last updated: 2026-05-05*