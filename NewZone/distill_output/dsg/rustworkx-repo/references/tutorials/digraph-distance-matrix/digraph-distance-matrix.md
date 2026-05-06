# How To: Digraph Distance Matrix

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: unittest

## Overview

Instantiate array: test digraph distance matrix

## Prerequisites

**Required Modules:**
- `unittest`
- `numpy`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign expected = np.array(...)

```python
expected = np.array([[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 1.0], [0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0], [0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0], [0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0], [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
```


## Complete Example

```python
# Workflow
expected = np.array([[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 1.0], [0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0], [0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0], [0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0], [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
```

## Next Steps


---

*Source: test_dist_matrix.py:26 | Complexity: Beginner | Last updated: 2026-05-05*