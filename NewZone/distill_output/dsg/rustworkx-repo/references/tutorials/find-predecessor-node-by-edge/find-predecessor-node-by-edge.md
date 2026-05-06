# How To: Find Predecessor Node By Edge

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test find predecessor node by edge

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign dag = rustworkx.PyDAG(...)

```python
dag = rustworkx.PyDAG()
```

### Step 2: Assign node_a = dag.add_node(...)

```python
node_a = dag.add_node('a')
```

### Step 3: Assign node_b = dag.add_child(...)

```python
node_b = dag.add_child(node_a, 'b', 'a to b')
```

### Step 4: Assign node_c = dag.add_child(...)

```python
node_c = dag.add_child(node_b, 'c', 'b to c')
```

### Step 5: Call dag.add_child()

```python
dag.add_child(node_c, 'd', 'c to d')
```

### Step 6: Assign res = dag.find_predecessor_node_by_edge(...)

```python
res = dag.find_predecessor_node_by_edge(node_b, compare_edges)
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual('a', res)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'a to b')
node_c = dag.add_child(node_b, 'c', 'b to c')
dag.add_child(node_c, 'd', 'c to d')

def compare_edges(edge):
    return 'a to b' == edge
res = dag.find_predecessor_node_by_edge(node_b, compare_edges)
self.assertEqual('a', res)
```

## Next Steps


---

*Source: test_edges.py:254 | Complexity: Intermediate | Last updated: 2026-05-05*