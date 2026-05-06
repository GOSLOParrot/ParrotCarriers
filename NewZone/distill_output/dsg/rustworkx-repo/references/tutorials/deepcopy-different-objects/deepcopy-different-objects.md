# How To: Deepcopy Different Objects

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test deepcopy different objects

## Prerequisites

**Required Modules:**
- `copy`
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph_a = rustworkx.PyDiGraph(...)

```python
graph_a = rustworkx.PyDiGraph(attrs=[1])
```

### Step 2: Assign node_a = graph_a.add_node(...)

```python
node_a = graph_a.add_node([2])
```

### Step 3: Assign node_b = graph_a.add_child(...)

```python
node_b = graph_a.add_child(node_a, [3], [4])
```

### Step 4: Assign graph_b = copy.deepcopy(...)

```python
graph_b = copy.deepcopy(graph_a)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(graph_a.attrs, graph_b.attrs)
```

### Step 6: Call self.assertIsNot()

```python
self.assertIsNot(graph_a.attrs, graph_b.attrs)
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(graph_a[node_a], graph_b[node_a])
```

### Step 8: Call self.assertIsNot()

```python
self.assertIsNot(graph_a[node_a], graph_b[node_a])
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))
```

### Step 10: Call self.assertIsNot()

```python
self.assertIsNot(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))
```


## Complete Example

```python
# Workflow
graph_a = rustworkx.PyDiGraph(attrs=[1])
node_a = graph_a.add_node([2])
node_b = graph_a.add_child(node_a, [3], [4])
graph_b = copy.deepcopy(graph_a)
self.assertEqual(graph_a.attrs, graph_b.attrs)
self.assertIsNot(graph_a.attrs, graph_b.attrs)
self.assertEqual(graph_a[node_a], graph_b[node_a])
self.assertIsNot(graph_a[node_a], graph_b[node_a])
self.assertEqual(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))
self.assertIsNot(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))
```

## Next Steps


---

*Source: test_deepcopy.py:58 | Complexity: Advanced | Last updated: 2026-05-05*