# How To: Deduplicates Other Ids

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test deduplicates other ids

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
assert db.execute.call_count == 1
```

### Step 2: Assign edge1 = GraphEdge(...)

```python
edge1 = GraphEdge(edge_id='e1', source_id='f1', target_id='f2', edge_type=EdgeType.ENTITY)
```

### Step 3: Assign edge2 = GraphEdge(...)

```python
edge2 = GraphEdge(edge_id='e2', source_id='f2', target_id='f1', edge_type=EdgeType.SEMANTIC)
```

### Step 4: Assign db.get_edges_for_node.return_value = value

```python
db.get_edges_for_node.return_value = [edge1, edge2]
```

### Step 5: Assign db.execute.return_value = value

```python
db.execute.return_value = []
```

### Step 6: Assign checker = SheafConsistencyChecker(...)

```python
checker = SheafConsistencyChecker(db)
```

### Step 7: Assign fact = _make_fact(...)

```python
fact = _make_fact()
```

### Step 8: Assign results = checker.check_consistency(...)

```python
results = checker.check_consistency(fact, 'default')
```

**Verification:**
```python
assert db.execute.call_count == 1
```


## Complete Example

```python
# Workflow
db = _make_mock_db()
edge1 = GraphEdge(edge_id='e1', source_id='f1', target_id='f2', edge_type=EdgeType.ENTITY)
edge2 = GraphEdge(edge_id='e2', source_id='f2', target_id='f1', edge_type=EdgeType.SEMANTIC)
db.get_edges_for_node.return_value = [edge1, edge2]
db.execute.return_value = []
checker = SheafConsistencyChecker(db)
fact = _make_fact()
results = checker.check_consistency(fact, 'default')
assert db.execute.call_count == 1
```

## Next Steps


---

*Source: test_sheaf.py:282 | Complexity: Advanced | Last updated: 2026-05-05*