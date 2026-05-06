# How To: Cx H H Cx

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test cx h h cx

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign dag = rustworkx.PyDiGraph(...)

```python
dag = rustworkx.PyDiGraph()
```

### Step 2: Assign unknown = dag.add_nodes_from(...)

```python
q0, q1 = dag.add_nodes_from(['q0', 'q1'])
```

### Step 3: Assign cx_1 = dag.add_child(...)

```python
cx_1 = dag.add_child(q0, 'cx', 'q0')
```

### Step 4: Call dag.add_edge()

```python
dag.add_edge(q1, cx_1, 'q1')
```

### Step 5: Assign h_1 = dag.add_child(...)

```python
h_1 = dag.add_child(cx_1, 'h', 'q0')
```

### Step 6: Assign h_2 = dag.add_child(...)

```python
h_2 = dag.add_child(cx_1, 'h', 'q1')
```

### Step 7: Assign cx_2 = dag.add_child(...)

```python
cx_2 = dag.add_child(h_1, 'cx', 'q0')
```

### Step 8: Call dag.add_edge()

```python
dag.add_edge(h_2, cx_2, 'q1')
```

### Step 9: Assign res = rustworkx.collect_runs(...)

```python
res = rustworkx.collect_runs(dag, filter_function)
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual([['cx'], ['h', 'cx'], ['h']], res)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDiGraph()
q0, q1 = dag.add_nodes_from(['q0', 'q1'])
cx_1 = dag.add_child(q0, 'cx', 'q0')
dag.add_edge(q1, cx_1, 'q1')
h_1 = dag.add_child(cx_1, 'h', 'q0')
h_2 = dag.add_child(cx_1, 'h', 'q1')
cx_2 = dag.add_child(h_1, 'cx', 'q0')
dag.add_edge(h_2, cx_2, 'q1')

def filter_function(node):
    return node in ['cx', 'h']
res = rustworkx.collect_runs(dag, filter_function)
self.assertEqual([['cx'], ['h', 'cx'], ['h']], res)
```

## Next Steps


---

*Source: test_collect_runs.py:109 | Complexity: Advanced | Last updated: 2026-05-05*