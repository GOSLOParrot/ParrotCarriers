# How To: Skips Contradiction Edges

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test skips contradiction edges

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
assert results == []
```

### Step 2: Assign edge = GraphEdge(...)

```python
edge = GraphEdge(edge_id='e1', source_id='f1', target_id='f2', edge_type=EdgeType.CONTRADICTION)
```

### Step 3: Assign db.get_edges_for_node.return_value = value

```python
db.get_edges_for_node.return_value = [edge]
```

### Step 4: Assign checker = SheafConsistencyChecker(...)

```python
checker = SheafConsistencyChecker(db)
```

### Step 5: Assign fact = _make_fact(...)

```python
fact = _make_fact()
```

### Step 6: Assign results = checker.check_consistency(...)

```python
results = checker.check_consistency(fact, 'default')
```

**Verification:**
```python
assert results == []
```


## Complete Example

```python
# Workflow
db = _make_mock_db()
edge = GraphEdge(edge_id='e1', source_id='f1', target_id='f2', edge_type=EdgeType.CONTRADICTION)
db.get_edges_for_node.return_value = [edge]
checker = SheafConsistencyChecker(db)
fact = _make_fact()
results = checker.check_consistency(fact, 'default')
assert results == []
```

## Next Steps


---

*Source: test_sheaf.py:217 | Complexity: Intermediate | Last updated: 2026-05-05*