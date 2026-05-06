# How To: Forest

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test forest

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign s = self.graph.add_node(...)

```python
s = self.graph.add_node('S')
```

### Step 2: Assign t = self.graph.add_node(...)

```python
t = self.graph.add_node('T')
```

### Step 3: Assign u = self.graph.add_node(...)

```python
u = self.graph.add_node('U')
```

### Step 4: Call self.graph.add_edges_from()

```python
self.graph.add_edges_from([(s, t, 10), (t, u, 9), (s, u, 8)])
```

### Step 5: Assign forest_expected_edges = value

```python
forest_expected_edges = self.expected_edges + [(s, u, 8), (t, u, 9)]
```

### Step 6: Assign msf_graph = rustworkx.minimum_spanning_tree(...)

```python
msf_graph = rustworkx.minimum_spanning_tree(self.graph, weight_fn=lambda x: x)
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(self.graph.nodes(), msf_graph.nodes())
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(len(self.graph.nodes()) - 2, len(msf_graph.edge_list()))
```

### Step 9: Call self.assertEqualEdgeList()

```python
self.assertEqualEdgeList(forest_expected_edges, msf_graph.weighted_edge_list())
```


## Complete Example

```python
# Workflow
s = self.graph.add_node('S')
t = self.graph.add_node('T')
u = self.graph.add_node('U')
self.graph.add_edges_from([(s, t, 10), (t, u, 9), (s, u, 8)])
forest_expected_edges = self.expected_edges + [(s, u, 8), (t, u, 9)]
msf_graph = rustworkx.minimum_spanning_tree(self.graph, weight_fn=lambda x: x)
self.assertEqual(self.graph.nodes(), msf_graph.nodes())
self.assertEqual(len(self.graph.nodes()) - 2, len(msf_graph.edge_list()))
self.assertEqualEdgeList(forest_expected_edges, msf_graph.weighted_edge_list())
```

## Next Steps


---

*Source: test_mst.py:65 | Complexity: Advanced | Last updated: 2026-05-05*