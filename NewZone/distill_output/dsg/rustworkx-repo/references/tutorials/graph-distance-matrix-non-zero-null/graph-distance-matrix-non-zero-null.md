# How To: Graph Distance Matrix Non Zero Null

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: unittest

## Overview

Instantiate array: test graph distance matrix non zero null

## Prerequisites

**Required Modules:**
- `unittest`
- `numpy`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign expected = np.array(...)

```python
expected = np.array([[0.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, np.nan], [1.0, 0.0, 1.0, 2.0, 3.0, 3.0, 2.0, np.nan], [2.0, 1.0, 0.0, 1.0, 2.0, 3.0, 3.0, np.nan], [3.0, 2.0, 1.0, 0.0, 1.0, 2.0, 3.0, np.nan], [3.0, 3.0, 2.0, 1.0, 0.0, 1.0, 2.0, np.nan], [2.0, 3.0, 3.0, 2.0, 1.0, 0.0, 1.0, np.nan], [1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 0.0, np.nan], [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 0.0]])
```


## Complete Example

```python
# Workflow
expected = np.array([[0.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, np.nan], [1.0, 0.0, 1.0, 2.0, 3.0, 3.0, 2.0, np.nan], [2.0, 1.0, 0.0, 1.0, 2.0, 3.0, 3.0, np.nan], [3.0, 2.0, 1.0, 0.0, 1.0, 2.0, 3.0, np.nan], [3.0, 3.0, 2.0, 1.0, 0.0, 1.0, 2.0, np.nan], [2.0, 3.0, 3.0, 2.0, 1.0, 0.0, 1.0, np.nan], [1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 0.0, np.nan], [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 0.0]])
```

## Next Steps


---

*Source: test_dist_matrix.py:63 | Complexity: Beginner | Last updated: 2026-05-05*