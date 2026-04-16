# How To: Validation Invalid Excluded Types

**Difficulty**: Beginner
**Estimated Time**: 5 minutes

## Overview

Configuration example: Test validation function with invalid excluded types.

## Prerequisites

**Required Modules:**
- `datetime`
- `pytest`
- `pydantic`
- `graphiti_core.graphiti`
- `graphiti_core.helpers`
- `tests.helpers_test`


## Step-by-Step Guide

### Step 1: Assign entity_types = value

```python
entity_types = {'Person': Person, 'Organization': Organization}
```


## Complete Example

```python
# Workflow
entity_types = {'Person': Person, 'Organization': Organization}
```

## Next Steps


---

*Source: test_entity_exclusion_int.py:296 | Complexity: Beginner | Last updated: 2026-04-12*