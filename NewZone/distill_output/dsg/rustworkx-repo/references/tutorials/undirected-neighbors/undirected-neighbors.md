# How To: Undirected Neighbors

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test undirected neighbors

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `rustworkx.generators`


## Step-by-Step Guide

### Step 1: Assign dag = rustworkx.PyDAG(...)

```python
dag = rustworkx.PyDAG()
```

### Step 2: Assign node_a = dag.add_node(...)

```python
node_a = dag.add_node('a')
```

### Step 3: Assign node_b = dag.add_child(...)

```python
node_b = dag.add_child(node_a, 'b', {'a': 1})
```

### Step 4: Assign directed = dag.neighbors(...)

```python
directed = dag.neighbors(node_b)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual([], directed)
```

### Step 6: Assign undirected = dag.neighbors_undirected(...)

```python
undirected = dag.neighbors_undirected(node_b)
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual([node_a], undirected)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
directed = dag.neighbors(node_b)
self.assertEqual([], directed)
undirected = dag.neighbors_undirected(node_b)
self.assertEqual([node_a], undirected)
```

## Next Steps


---

*Source: test_neighbors.py:62 | Complexity: Intermediate | Last updated: 2026-05-05*