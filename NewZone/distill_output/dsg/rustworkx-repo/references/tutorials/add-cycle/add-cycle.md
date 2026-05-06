# How To: Add Cycle

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test add cycle

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign dag = rustworkx.PyDAG(...)

```python
dag = rustworkx.PyDAG()
```

### Step 2: Assign dag.check_cycle = True

```python
dag.check_cycle = True
```

### Step 3: Assign node_a = dag.add_node(...)

```python
node_a = dag.add_node('a')
```

### Step 4: Assign node_b = dag.add_child(...)

```python
node_b = dag.add_child(node_a, 'b', {})
```

### Step 5: Call self.assertRaises()

```python
self.assertRaises(rustworkx.DAGWouldCycle, dag.add_edge, node_b, node_a, {})
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
dag.check_cycle = True
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {})
self.assertRaises(rustworkx.DAGWouldCycle, dag.add_edge, node_b, node_a, {})
```

## Next Steps


---

*Source: test_edges.py:200 | Complexity: Intermediate | Last updated: 2026-05-05*