# How To: Set Node Data Setitem

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test set node data setitem

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

### Step 5: Assign unknown = 'Oh so cool'

```python
graph[node_b] = 'Oh so cool'
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual('Oh so cool', graph[node_b])
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
graph[node_b] = 'Oh so cool'
self.assertEqual('Oh so cool', graph[node_b])
```

## Next Steps


---

*Source: test_nodes.py:164 | Complexity: Intermediate | Last updated: 2026-05-05*