# How To: Tested By Edge

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test tested by edge

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
test = _node('t1', 'test_my_func', 'test.test_my_func', 'tests/test.py', is_test=True)
```

**Verification:**
```python
assert tests[0]['node_id'] == 't1'
```

### Step 3: Assign edge = _edge(...)

```python
edge = _edge('e1', EdgeKind.TESTED_BY, 'f1', 't1')
```

### Step 4: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('src/mod.py', [func], [], _fr())
```

### Step 5: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('tests/test.py', [test], [edge], _fr('tests/test.py'))
```

### Step 6: Assign tests = engine.get_tests_for(...)

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
test = _node('t1', 'test_my_func', 'test.test_my_func', 'tests/test.py', is_test=True)
edge = _edge('e1', EdgeKind.TESTED_BY, 'f1', 't1')
store.store_file_nodes_edges('src/mod.py', [func], [], _fr())
store.store_file_nodes_edges('tests/test.py', [test], [edge], _fr('tests/test.py'))
tests = engine.get_tests_for('f1')
assert len(tests) == 1
assert tests[0]['node_id'] == 't1'
```

## Next Steps


---

*Source: test_graph_engine.py:203 | Complexity: Intermediate | Last updated: 2026-05-05*