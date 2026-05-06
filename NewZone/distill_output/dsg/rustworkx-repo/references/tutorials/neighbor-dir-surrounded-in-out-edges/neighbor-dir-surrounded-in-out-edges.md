# How To: Neighbor Dir Surrounded In Out Edges

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test neighbor dir surrounded in out edges

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
node_c = dag.add_child(node_b, 'c', {'a': 2})
```

### Step 5: Assign res = dag.out_edges(...)

```python
res = dag.out_edges(node_b)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual([(node_b, node_c, {'a': 2})], res)
```

### Step 7: Assign res = dag.in_edges(...)

```python
res = dag.in_edges(node_b)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual([(node_a, node_b, {'a': 1})], res)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
res = dag.out_edges(node_b)
self.assertEqual([(node_b, node_c, {'a': 2})], res)
res = dag.in_edges(node_b)
self.assertEqual([(node_a, node_b, {'a': 1})], res)
```

## Next Steps


---

*Source: test_adj.py:61 | Complexity: Advanced | Last updated: 2026-05-05*