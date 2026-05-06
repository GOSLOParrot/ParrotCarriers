# How To: Remove Edges From Gen

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test remove edges from gen

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

### Step 4: Assign node_c = graph.add_node(...)

```python
node_c = graph.add_node('c')
```

### Step 5: Call graph.add_edge()

```python
graph.add_edge(node_a, node_b, 'edgy')
```

### Step 6: Call graph.add_edge()

```python
graph.add_edge(node_a, node_c, 'super_edgy')
```

### Step 7: Call graph.remove_edges_from()

```python
graph.remove_edges_from(((node_a, n) for n in (node_b, node_c)))
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual([], graph.edges())
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyDiGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
graph.add_edge(node_a, node_b, 'edgy')
graph.add_edge(node_a, node_c, 'super_edgy')
graph.remove_edges_from(((node_a, n) for n in (node_b, node_c)))
self.assertEqual([], graph.edges())
```

## Next Steps


---

*Source: test_edges.py:167 | Complexity: Advanced | Last updated: 2026-05-05*