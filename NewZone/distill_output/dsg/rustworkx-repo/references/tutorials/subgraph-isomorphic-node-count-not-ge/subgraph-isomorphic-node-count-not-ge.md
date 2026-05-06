# How To: Subgraph Isomorphic Node Count Not Ge

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test subgraph isomorphic node count not ge

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
nodes = g_a.add_nodes_from(['a_1', 'a_2'])
```

### Step 4: Call g_a.add_edges_from()

```python
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1')])
```

### Step 5: Assign nodes = g_b.add_nodes_from(...)

```python
nodes = g_b.add_nodes_from(['a_0', 'a_1', 'a_3'])
```

### Step 6: Call g_b.add_edges_from()

```python
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1')])
```

### Step 7: Call self.assertFalse()

```python
self.assertFalse(rustworkx.is_subgraph_isomorphic(g_a, g_b, id_order=id_order))
```


## Complete Example

```python
# Workflow
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1')])
nodes = g_b.add_nodes_from(['a_0', 'a_1', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertFalse(rustworkx.is_subgraph_isomorphic(g_a, g_b, id_order=id_order))
```

## Next Steps


---

*Source: test_subgraph_isomorphic.py:156 | Complexity: Intermediate | Last updated: 2026-05-05*