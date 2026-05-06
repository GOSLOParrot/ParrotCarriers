# How To: Isomorphic Removed Nodes In Second Graph

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test isomorphic removed nodes in second graph

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
nodes = g_b.add_nodes_from(['a_0', 'a_2', 'a_1', 'a_3'])
```

### Step 6: Call g_b.add_edges_from()

```python
g_b.add_edges_from([(nodes[0], nodes[1], 'e_01'), (nodes[0], nodes[3], 'e_03'), (nodes[2], nodes[1], 'a_1'), (nodes[1], nodes[3], 'a_2')])
```

### Step 7: Call g_b.remove_node()

```python
g_b.remove_node(nodes[0])
```

### Step 8: Call self.assertTrue()

```python
self.assertTrue(rustworkx.is_isomorphic(g_a, g_b, lambda x, y: x == y, id_order=id_order))
```


## Complete Example

```python
# Workflow
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
nodes = g_b.add_nodes_from(['a_0', 'a_2', 'a_1', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'e_01'), (nodes[0], nodes[3], 'e_03'), (nodes[2], nodes[1], 'a_1'), (nodes[1], nodes[3], 'a_2')])
g_b.remove_node(nodes[0])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_isomorphic(g_a, g_b, lambda x, y: x == y, id_order=id_order))
```

## Next Steps


---

*Source: test_isomorphic.py:133 | Complexity: Advanced | Last updated: 2026-05-05*