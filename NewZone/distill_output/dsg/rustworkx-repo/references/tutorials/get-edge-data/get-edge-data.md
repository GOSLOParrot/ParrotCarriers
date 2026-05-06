# How To: Get Edge Data

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test get edge data

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

### Step 4: Assign res = dag.get_edge_data(...)

```python
res = dag.get_edge_data(node_a, node_b)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual('Edgy', res)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'Edgy')
res = dag.get_edge_data(node_a, node_b)
self.assertEqual('Edgy', res)
```

## Next Steps


---

*Source: test_edges.py:19 | Complexity: Intermediate | Last updated: 2026-05-05*