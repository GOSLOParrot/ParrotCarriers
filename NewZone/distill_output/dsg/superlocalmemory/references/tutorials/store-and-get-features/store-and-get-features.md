# How To: Store And Get Features

**Difficulty**: Beginner
**Estimated Time**: 5 minutes

## Overview

Configuration example: test store and get features

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pytest`
- `pathlib`
- `superlocalmemory.learning.database`

**Setup Required:**
```python
# Fixtures: db
```

## Step-by-Step Guide

### Step 1: Assign features = value

```python
features = {'semantic_score': 0.8, 'bm25_score': 0.3, 'fisher_distance': 0.2}
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
features = {'semantic_score': 0.8, 'bm25_score': 0.3, 'fisher_distance': 0.2}
```

## Next Steps


---

*Source: test_learning_db.py:24 | Complexity: Beginner | Last updated: 2026-05-05*