# How To: Iso Full

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: test iso full

## Prerequisites

**Required Modules:**
- `__future__`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.encoding.graph_builder`
- `superlocalmemory.storage`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign dt = _parse_date(...)

```python
dt = _parse_date('2026-03-11T10:30:00')
```

**Verification:**
```python
assert dt is not None
```


## Complete Example

```python
# Workflow
dt = _parse_date('2026-03-11T10:30:00')
assert dt is not None
assert dt.year == 2026
```

## Next Steps


---

*Source: test_graph_builder.py:72 | Complexity: Beginner | Last updated: 2026-05-05*