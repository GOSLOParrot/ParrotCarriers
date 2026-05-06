# How To: Copy Shared Ref

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test copy shared ref

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph_a = rustworkx.PyGraph(...)

```python
graph_a = rustworkx.PyGraph()
```

### Step 2: Assign node_a = graph_a.add_node(...)

```python
node_a = graph_a.add_node({'a': 1})
```

### Step 3: Assign node_b = graph_a.add_node(...)

```python
node_b = graph_a.add_node({'b': 2})
```

### Step 4: Call graph_a.add_edge()

```python
graph_a.add_edge(node_a, node_b, {'edge': 1})
```

### Step 5: Assign graph_b = graph_a.copy(...)

```python
graph_b = graph_a.copy()
```

### Step 6: Assign unknown = 42

```python
graph_a[0]['a'] = 42
```

### Step 7: Assign unknown = 162

```python
graph_b.get_edge_data(0, 1)['edge'] = 162
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(graph_b[0]['a'], 42)
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})
```


## Complete Example

```python
# Workflow
graph_a = rustworkx.PyGraph()
node_a = graph_a.add_node({'a': 1})
node_b = graph_a.add_node({'b': 2})
graph_a.add_edge(node_a, node_b, {'edge': 1})
graph_b = graph_a.copy()
graph_a[0]['a'] = 42
graph_b.get_edge_data(0, 1)['edge'] = 162
self.assertEqual(graph_b[0]['a'], 42)
self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})
```

## Next Steps


---

*Source: test_copy.py:46 | Complexity: Advanced | Last updated: 2026-05-05*