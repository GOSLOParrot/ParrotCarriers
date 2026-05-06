# How To: Steiner Graph Multigraph

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test steiner graph multigraph

## Prerequisites

**Required Modules:**
- `pprint`
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign edge_list = value

```python
edge_list = [(1, 2, 1), (2, 3, 999), (2, 3, 1), (3, 4, 1), (3, 5, 1)]
```

### Step 2: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 3: Call graph.extend_from_weighted_edge_list()

```python
graph.extend_from_weighted_edge_list(edge_list)
```

### Step 4: Call graph.remove_node()

```python
graph.remove_node(0)
```

### Step 5: Assign terminal_nodes = value

```python
terminal_nodes = [2, 4, 5]
```

### Step 6: Assign tree = rustworkx.steiner_tree(...)

```python
tree = rustworkx.steiner_tree(graph, terminal_nodes, weight_fn=float)
```

### Step 7: Assign expected_edges = value

```python
expected_edges = [(2, 3, 1), (3, 4, 1), (3, 5, 1)]
```

### Step 8: Assign steiner_tree_edge_list = tree.weighted_edge_list(...)

```python
steiner_tree_edge_list = tree.weighted_edge_list()
```

### Step 9: Call self.assertIn()

```python
self.assertIn(edge, steiner_tree_edge_list)
```


## Complete Example

```python
# Workflow
edge_list = [(1, 2, 1), (2, 3, 999), (2, 3, 1), (3, 4, 1), (3, 5, 1)]
graph = rustworkx.PyGraph()
graph.extend_from_weighted_edge_list(edge_list)
graph.remove_node(0)
terminal_nodes = [2, 4, 5]
tree = rustworkx.steiner_tree(graph, terminal_nodes, weight_fn=float)
expected_edges = [(2, 3, 1), (3, 4, 1), (3, 5, 1)]
steiner_tree_edge_list = tree.weighted_edge_list()
for edge in expected_edges:
    self.assertIn(edge, steiner_tree_edge_list)
```

## Next Steps


---

*Source: test_steiner_tree.py:128 | Complexity: Advanced | Last updated: 2026-05-05*