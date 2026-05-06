# How To: Single Neighbor Dir Out Edges

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test single neighbor dir out edges

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


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

### Step 4: Assign node_c = dag.add_child(...)

```python
node_c = dag.add_child(node_a, 'c', {'a': 2})
```

### Step 5: Assign res = dag.out_edges(...)

```python
res = dag.out_edges(node_a)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual([(node_a, node_c, {'a': 2}), (node_a, node_b, {'a': 1})], res)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res = dag.out_edges(node_a)
self.assertEqual([(node_a, node_c, {'a': 2}), (node_a, node_b, {'a': 1})], res)
```

## Next Steps


---

*Source: test_adj.py:53 | Complexity: Intermediate | Last updated: 2026-05-05*