# How To: Set Node Data Setitem Bad Index

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test set node data setitem bad index

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
graph[42] = 'Oh so cool'
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
with self.assertRaises(IndexError):
    graph[42] = 'Oh so cool'
```

## Next Steps


---

*Source: test_nodes.py:172 | Complexity: Intermediate | Last updated: 2026-05-05*