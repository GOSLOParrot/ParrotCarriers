# How To: Get All Edge Data

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test get all edge data

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
node_b = dag.add_child(node_a, 'b', 'Edgy')
```

### Step 4: Call dag.add_edge()

```python
dag.add_edge(node_a, node_b, 'b')
```

### Step 5: Assign res = dag.get_all_edge_data(...)

```python
res = dag.get_all_edge_data(node_a, node_b)
```

### Step 6: Call self.assertIn()

```python
self.assertIn('b', res)
```

### Step 7: Call self.assertIn()

```python
self.assertIn('Edgy', res)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'Edgy')
dag.add_edge(node_a, node_b, 'b')
res = dag.get_all_edge_data(node_a, node_b)
self.assertIn('b', res)
self.assertIn('Edgy', res)
```

## Next Steps


---

*Source: test_edges.py:26 | Complexity: Intermediate | Last updated: 2026-05-05*