# How To: Enable Cycle Checking After Edge

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test enable cycle checking after edge

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
node_b = dag.add_child(node_a, 'b', {})
```

### Step 4: Call dag.add_edge()

```python
dag.add_edge(node_b, node_a, {})
```

### Step 5: Assign dag.check_cycle = True

```python
dag.check_cycle = True
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {})
dag.add_edge(node_b, node_a, {})
with self.assertRaises(rustworkx.DAGHasCycle):
    dag.check_cycle = True
```

## Next Steps


---

*Source: test_edges.py:215 | Complexity: Intermediate | Last updated: 2026-05-05*