# How To: No Edges Returns Empty

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test no edges returns empty

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `dataclasses`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.math.sheaf`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign db = _make_mock_db(...)

```python
db = _make_mock_db()
```

**Verification:**
```python
assert checker.check_consistency(fact, 'default') == []
```

### Step 2: Assign db.get_edges_for_node.return_value = value

```python
db.get_edges_for_node.return_value = []
```

### Step 3: Assign checker = SheafConsistencyChecker(...)

```python
checker = SheafConsistencyChecker(db)
```

### Step 4: Assign fact = _make_fact(...)

```python
fact = _make_fact()
```

**Verification:**
```python
assert checker.check_consistency(fact, 'default') == []
```


## Complete Example

```python
# Workflow
db = _make_mock_db()
db.get_edges_for_node.return_value = []
checker = SheafConsistencyChecker(db)
fact = _make_fact()
assert checker.check_consistency(fact, 'default') == []
```

## Next Steps


---

*Source: test_sheaf.py:210 | Complexity: Intermediate | Last updated: 2026-05-05*