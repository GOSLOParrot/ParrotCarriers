# How To: No Self Reference

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test no self reference

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pytest`
- `superlocalmemory.code_graph.database`
- `superlocalmemory.code_graph.graph_store`
- `superlocalmemory.code_graph.models`

**Setup Required:**
```python
# Fixtures: store
```

## Step-by-Step Guide

### Step 1: Assign n1 = _make_node(...)

```python
n1 = _make_node('n1', 'foo', 'a.foo', 'src/a.py')
```

**Verification:**
```python
assert 'src/a.py' not in deps
```

### Step 2: Assign n2 = _make_node(...)

```python
n2 = _make_node('n2', 'bar', 'a.bar', 'src/a.py')
```

### Step 3: Assign edge = _make_edge(...)

```python
edge = _make_edge('e1', EdgeKind.CALLS, 'n1', 'n2', 'src/a.py')
```

### Step 4: Assign fr = _make_file_record(...)

```python
fr = _make_file_record('src/a.py', 'h1', 2, 1)
```

### Step 5: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('src/a.py', [n1, n2], [edge], fr)
```

### Step 6: Assign deps = store.find_dependents(...)

```python
deps = store.find_dependents('src/a.py')
```

**Verification:**
```python
assert 'src/a.py' not in deps
```


## Complete Example

```python
# Setup
# Fixtures: store

# Workflow
n1 = _make_node('n1', 'foo', 'a.foo', 'src/a.py')
n2 = _make_node('n2', 'bar', 'a.bar', 'src/a.py')
edge = _make_edge('e1', EdgeKind.CALLS, 'n1', 'n2', 'src/a.py')
fr = _make_file_record('src/a.py', 'h1', 2, 1)
store.store_file_nodes_edges('src/a.py', [n1, n2], [edge], fr)
deps = store.find_dependents('src/a.py')
assert 'src/a.py' not in deps
```

## Next Steps


---

*Source: test_graph_store.py:236 | Complexity: Intermediate | Last updated: 2026-05-05*