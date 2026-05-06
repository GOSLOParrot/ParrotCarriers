# How To: Store File Parse Results

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test store file parse results

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.code_graph.database`
- `superlocalmemory.code_graph.models`

**Setup Required:**
```python
# Fixtures: db
```

## Step-by-Step Guide

### Step 1: Assign n1 = _make_node(...)

```python
n1 = _make_node('n1', 'old_func', qualified_name='test.py::old_func', file_path='test.py')
```

**Verification:**
```python
assert db.get_node('n1') is None
```

### Step 2: Call db.upsert_node()

```python
db.upsert_node(n1)
```

**Verification:**
```python
assert db.get_node('n2') is not None
```

### Step 3: Assign new_nodes = value

```python
new_nodes = [_make_node('n2', 'new_func', qualified_name='test.py::new_func', file_path='test.py'), _make_node('n3', 'helper', qualified_name='test.py::helper', file_path='test.py')]
```

**Verification:**
```python
assert db.get_node('n3') is not None
```

### Step 4: Assign new_edges = value

```python
new_edges = [_make_edge('e1', 'n2', 'n3', file_path='test.py')]
```

**Verification:**
```python
assert db.get_edge_count() == 1
```

### Step 5: Assign file_rec = FileRecord(...)

```python
file_rec = FileRecord(file_path='test.py', content_hash='newhash', mtime=time.time(), language='python', node_count=2, edge_count=1)
```

**Verification:**
```python
assert rec is not None
```

### Step 6: Call db.store_file_parse_results()

```python
db.store_file_parse_results('test.py', new_nodes, new_edges, file_rec)
```

**Verification:**
```python
assert rec.content_hash == 'newhash'
```

### Step 7: Assign rec = db.get_file_record(...)

```python
rec = db.get_file_record('test.py')
```

**Verification:**
```python
assert rec is not None
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
n1 = _make_node('n1', 'old_func', qualified_name='test.py::old_func', file_path='test.py')
db.upsert_node(n1)
new_nodes = [_make_node('n2', 'new_func', qualified_name='test.py::new_func', file_path='test.py'), _make_node('n3', 'helper', qualified_name='test.py::helper', file_path='test.py')]
new_edges = [_make_edge('e1', 'n2', 'n3', file_path='test.py')]
file_rec = FileRecord(file_path='test.py', content_hash='newhash', mtime=time.time(), language='python', node_count=2, edge_count=1)
db.store_file_parse_results('test.py', new_nodes, new_edges, file_rec)
assert db.get_node('n1') is None
assert db.get_node('n2') is not None
assert db.get_node('n3') is not None
assert db.get_edge_count() == 1
rec = db.get_file_record('test.py')
assert rec is not None
assert rec.content_hash == 'newhash'
```

## Next Steps


---

*Source: test_database.py:228 | Complexity: Intermediate | Last updated: 2026-05-05*