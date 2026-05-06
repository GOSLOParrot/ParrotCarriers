# How To: Update Edge Parallel Edges

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test update edge parallel edges

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyDiGraph(...)

```python
graph = rustworkx.PyDiGraph()
```

### Step 2: Assign node_a = graph.add_node(...)

```python
node_a = graph.add_node('a')
```

### Step 3: Assign node_b = graph.add_node(...)

```python
node_b = graph.add_node('b')
```

### Step 4: Call graph.add_edge()

```python
graph.add_edge(node_a, node_b, 'not edgy')
```

### Step 5: Assign edge_index = graph.add_edge(...)

```python
edge_index = graph.add_edge(node_a, node_b, 'not edgy')
```

### Step 6: Call graph.update_edge_by_index()

```python
graph.update_edge_by_index(edge_index, 'Edgy')
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual([(0, 1, 'not edgy'), (0, 1, 'Edgy')], list(graph.weighted_edge_list()))
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyDiGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'not edgy')
edge_index = graph.add_edge(node_a, node_b, 'not edgy')
graph.update_edge_by_index(edge_index, 'Edgy')
self.assertEqual([(0, 1, 'not edgy'), (0, 1, 'Edgy')], list(graph.weighted_edge_list()))
```

## Next Steps


---

*Source: test_edges.py:81 | Complexity: Intermediate | Last updated: 2026-05-05*