# How To: Lifecycle Weight Mapping

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: lifecycle_weight should return correct weight for each zone.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `math`
- `random`
- `datetime`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.math.ebbinghaus`
- `statistics`
- `unittest.mock`

**Setup Required:**
```python
# Fixtures: curve
```

## Step-by-Step Guide

### Step 1: 'lifecycle_weight should return correct weight for each zone.'

```python
'lifecycle_weight should return correct weight for each zone.'
```

**Verification:**
```python
assert curve.lifecycle_weight('active') == 1.0
```


## Complete Example

```python
# Setup
# Fixtures: curve

# Workflow
'lifecycle_weight should return correct weight for each zone.'
assert curve.lifecycle_weight('active') == 1.0
assert curve.lifecycle_weight('warm') == 0.7
assert curve.lifecycle_weight('cold') == 0.3
assert curve.lifecycle_weight('archive') == 0.0
assert curve.lifecycle_weight('forgotten') == 0.0
assert curve.lifecycle_weight('unknown_zone') == 0.0
```

## Next Steps


---

*Source: test_ebbinghaus.py:238 | Complexity: Beginner | Last updated: 2026-05-05*