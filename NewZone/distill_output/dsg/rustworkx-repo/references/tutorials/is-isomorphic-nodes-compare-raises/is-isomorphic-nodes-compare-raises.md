# How To: Is Isomorphic Nodes Compare Raises

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test is isomorphic nodes compare raises

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign g_a = rustworkx.PyGraph(...)

```python
g_a = rustworkx.PyGraph()
```

### Step 2: Assign g_b = rustworkx.PyGraph(...)

```python
g_b = rustworkx.PyGraph()
```

### Step 3: Assign nodes = g_a.add_nodes_from(...)

```python
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3'])
```

### Step 4: Call g_a.add_edges_from()

```python
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
```

### Step 5: Assign nodes = g_b.add_nodes_from(...)

```python
nodes = g_b.add_nodes_from(['b_1', 'b_2', 'b_3'])
```

### Step 6: Call g_b.add_edges_from()

```python
g_b.add_edges_from([(nodes[0], nodes[1], 'b_1'), (nodes[1], nodes[2], 'b_2')])
```

### Step 7: Call self.assertRaises()

```python
self.assertRaises(TypeError, rustworkx.is_isomorphic, (g_a, g_b, compare_nodes))
```


## Complete Example

```python
# Workflow
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
nodes = g_b.add_nodes_from(['b_1', 'b_2', 'b_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'b_1'), (nodes[1], nodes[2], 'b_2')])

def compare_nodes(a, b):
    raise TypeError('Failure')
self.assertRaises(TypeError, rustworkx.is_isomorphic, (g_a, g_b, compare_nodes))
```

## Next Steps


---

*Source: test_isomorphic.py:83 | Complexity: Intermediate | Last updated: 2026-05-05*