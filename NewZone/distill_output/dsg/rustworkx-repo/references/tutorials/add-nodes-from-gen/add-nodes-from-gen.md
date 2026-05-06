# How To: Add Nodes From Gen

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test add nodes from gen

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 2: Assign nodes = list(...)

```python
nodes = list(range(100))
```

### Step 3: Assign node_gen = value

```python
node_gen = (i ** 2 for i in nodes)
```

### Step 4: Assign res = graph.add_nodes_from(...)

```python
res = graph.add_nodes_from(node_gen)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(len(res), 100)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(res, nodes)
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
nodes = list(range(100))
node_gen = (i ** 2 for i in nodes)
res = graph.add_nodes_from(node_gen)
self.assertEqual(len(res), 100)
self.assertEqual(res, nodes)
```

## Next Steps


---

*Source: test_nodes.py:136 | Complexity: Intermediate | Last updated: 2026-05-05*