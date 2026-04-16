# How To: Build Directed Uuid Map Chain

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: test build directed uuid map chain

## Prerequisites

**Required Modules:**
- `collections`
- `unittest.mock`
- `pytest`
- `graphiti_core.edges`
- `graphiti_core.graphiti_types`
- `graphiti_core.nodes`
- `graphiti_core.utils`
- `graphiti_core.utils.bulk_utils`
- `graphiti_core.utils.datetime_utils`


## Step-by-Step Guide

### Step 1: Assign mapping = bulk_utils._build_directed_uuid_map(...)

```python
mapping = bulk_utils._build_directed_uuid_map([('a', 'b'), ('b', 'c')])
```

**Verification:**
```python
assert mapping['a'] == 'c'
```


## Complete Example

```python
# Workflow
mapping = bulk_utils._build_directed_uuid_map([('a', 'b'), ('b', 'c')])
assert mapping['a'] == 'c'
assert mapping['b'] == 'c'
assert mapping['c'] == 'c'
```

## Next Steps


---

*Source: test_bulk_utils.py:194 | Complexity: Beginner | Last updated: 2026-04-12*