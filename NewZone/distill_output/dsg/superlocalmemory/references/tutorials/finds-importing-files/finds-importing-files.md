# How To: Finds Importing Files

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test finds importing files

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

### Step 1: Assign n_a = _make_node(...)

```python
n_a = _make_node('n_a', 'func_a', 'a.func_a', 'src/a.py')
```

**Verification:**
```python
assert 'src/b.py' in deps
```

### Step 2: Assign n_b = _make_node(...)

```python
n_b = _make_node('n_b', 'func_b', 'b.func_b', 'src/b.py')
```

### Step 3: Assign edge = _make_edge(...)

```python
edge = _make_edge('e1', EdgeKind.IMPORTS, 'n_b', 'n_a', 'src/b.py')
```

### Step 4: Assign fr_a = _make_file_record(...)

```python
fr_a = _make_file_record('src/a.py', 'h1', 1, 0)
```

### Step 5: Assign fr_b = _make_file_record(...)

```python
fr_b = _make_file_record('src/b.py', 'h2', 1, 1)
```

### Step 6: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('src/a.py', [n_a], [], fr_a)
```

### Step 7: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('src/b.py', [n_b], [edge], fr_b)
```

### Step 8: Assign deps = store.find_dependents(...)

```python
deps = store.find_dependents('src/a.py')
```

**Verification:**
```python
assert 'src/b.py' in deps
```


## Complete Example

```python
# Setup
# Fixtures: store

# Workflow
n_a = _make_node('n_a', 'func_a', 'a.func_a', 'src/a.py')
n_b = _make_node('n_b', 'func_b', 'b.func_b', 'src/b.py')
edge = _make_edge('e1', EdgeKind.IMPORTS, 'n_b', 'n_a', 'src/b.py')
fr_a = _make_file_record('src/a.py', 'h1', 1, 0)
fr_b = _make_file_record('src/b.py', 'h2', 1, 1)
store.store_file_nodes_edges('src/a.py', [n_a], [], fr_a)
store.store_file_nodes_edges('src/b.py', [n_b], [edge], fr_b)
deps = store.find_dependents('src/a.py')
assert 'src/b.py' in deps
```

## Next Steps


---

*Source: test_graph_store.py:219 | Complexity: Advanced | Last updated: 2026-05-05*