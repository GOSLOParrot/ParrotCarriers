# How To: Deduplicates

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test deduplicates

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pytest`
- `superlocalmemory.code_graph.database`
- `superlocalmemory.code_graph.graph_engine`
- `superlocalmemory.code_graph.graph_store`
- `superlocalmemory.code_graph.models`
- `rustworkx`

**Setup Required:**
```python
# Fixtures: store, engine
```

## Step-by-Step Guide

### Step 1: Assign func = _node(...)

```python
func = _node('f1', 'my_func', 'mod.my_func')
```

**Verification:**
```python
assert len(tests) == 1
```

### Step 2: Assign test = _node(...)

```python
test = _node('t1', 'test_it', 'test.test_it', 'tests/test.py', is_test=True)
```

### Step 3: Assign e1 = _edge(...)

```python
e1 = _edge('e1', EdgeKind.TESTED_BY, 'f1', 't1')
```

### Step 4: Assign e2 = _edge(...)

```python
e2 = _edge('e2', EdgeKind.CALLS, 't1', 'f1', 'tests/test.py')
```

### Step 5: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('src/mod.py', [func], [], _fr())
```

### Step 6: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('tests/test.py', [test], [e1, e2], _fr('tests/test.py'))
```

### Step 7: Assign tests = engine.get_tests_for(...)

```python
tests = engine.get_tests_for('f1')
```

**Verification:**
```python
assert len(tests) == 1
```


## Complete Example

```python
# Setup
# Fixtures: store, engine

# Workflow
func = _node('f1', 'my_func', 'mod.my_func')
test = _node('t1', 'test_it', 'test.test_it', 'tests/test.py', is_test=True)
e1 = _edge('e1', EdgeKind.TESTED_BY, 'f1', 't1')
e2 = _edge('e2', EdgeKind.CALLS, 't1', 'f1', 'tests/test.py')
store.store_file_nodes_edges('src/mod.py', [func], [], _fr())
store.store_file_nodes_edges('tests/test.py', [test], [e1, e2], _fr('tests/test.py'))
tests = engine.get_tests_for('f1')
assert len(tests) == 1
```

## Next Steps


---

*Source: test_graph_engine.py:236 | Complexity: Intermediate | Last updated: 2026-05-05*