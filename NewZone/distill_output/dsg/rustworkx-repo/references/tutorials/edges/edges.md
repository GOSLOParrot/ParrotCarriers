# How To: Edges

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test edges

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
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
graph.add_edge(node_a, node_b, 'Edgy')
```

### Step 5: Assign node_c = graph.add_node(...)

```python
node_c = graph.add_node('c')
```

### Step 6: Call graph.add_edge()

```python
graph.add_edge(node_b, node_c, 'Super edgy')
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(['Edgy', 'Super edgy'], graph.edges())
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'Super edgy')
self.assertEqual(['Edgy', 'Super edgy'], graph.edges())
```

## Next Steps


---

*Source: test_edges.py:117 | Complexity: Intermediate | Last updated: 2026-05-05*