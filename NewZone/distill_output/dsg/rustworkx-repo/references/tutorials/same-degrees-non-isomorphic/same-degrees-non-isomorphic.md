# How To: Same Degrees Non Isomorphic

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test same degrees non isomorphic

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
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4', 'b_1', 'b_2', 'b_3', 'b_4'])
```

### Step 4: Call g_a.add_edges_from()

```python
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[2], nodes[3], 'a_3'), (nodes[3], nodes[0], 'a_4'), (nodes[4], nodes[5], 'b_1'), (nodes[5], nodes[6], 'b_2'), (nodes[6], nodes[7], 'b_3'), (nodes[7], nodes[4], 'b_4'), (nodes[0], nodes[4], 'e_1'), (nodes[1], nodes[5], 'e_2')])
```

### Step 5: Assign nodes = g_b.add_nodes_from(...)

```python
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4', 'b_1', 'b_2', 'b_3', 'b_4'])
```

### Step 6: Call g_b.add_edges_from()

```python
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[2], nodes[3], 'a_3'), (nodes[3], nodes[0], 'a_4'), (nodes[4], nodes[5], 'b_1'), (nodes[5], nodes[6], 'b_2'), (nodes[6], nodes[7], 'b_3'), (nodes[7], nodes[4], 'b_4'), (nodes[0], nodes[4], 'e_1'), (nodes[2], nodes[6], 'e_2')])
```

### Step 7: Call self.assertFalse()

```python
self.assertFalse(rustworkx.is_isomorphic(g_a, g_b, id_order=id_order))
```


## Complete Example

```python
# Workflow
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4', 'b_1', 'b_2', 'b_3', 'b_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[2], nodes[3], 'a_3'), (nodes[3], nodes[0], 'a_4'), (nodes[4], nodes[5], 'b_1'), (nodes[5], nodes[6], 'b_2'), (nodes[6], nodes[7], 'b_3'), (nodes[7], nodes[4], 'b_4'), (nodes[0], nodes[4], 'e_1'), (nodes[1], nodes[5], 'e_2')])
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4', 'b_1', 'b_2', 'b_3', 'b_4'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[2], nodes[3], 'a_3'), (nodes[3], nodes[0], 'a_4'), (nodes[4], nodes[5], 'b_1'), (nodes[5], nodes[6], 'b_2'), (nodes[6], nodes[7], 'b_3'), (nodes[7], nodes[4], 'b_4'), (nodes[0], nodes[4], 'e_1'), (nodes[2], nodes[6], 'e_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertFalse(rustworkx.is_isomorphic(g_a, g_b, id_order=id_order))
```

## Next Steps


---

*Source: test_isomorphic.py:170 | Complexity: Intermediate | Last updated: 2026-05-05*