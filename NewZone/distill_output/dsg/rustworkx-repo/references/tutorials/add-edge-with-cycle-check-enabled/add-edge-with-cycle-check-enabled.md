# How To: Add Edge With Cycle Check Enabled

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test add edge with cycle check enabled

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign dag = rustworkx.PyDAG(...)

```python
dag = rustworkx.PyDAG(True)
```

### Step 2: Assign node_a = dag.add_node(...)

```python
node_a = dag.add_node('a')
```

### Step 3: Assign node_c = dag.add_node(...)

```python
node_c = dag.add_node('c')
```

### Step 4: Assign node_b = dag.add_child(...)

```python
node_b = dag.add_child(node_a, 'b', {})
```

### Step 5: Call dag.add_edge()

```python
dag.add_edge(node_c, node_b, {})
```

### Step 6: Call self.assertTrue()

```python
self.assertTrue(dag.has_edge(node_c, node_b))
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG(True)
node_a = dag.add_node('a')
node_c = dag.add_node('c')
node_b = dag.add_child(node_a, 'b', {})
dag.add_edge(node_c, node_b, {})
self.assertTrue(dag.has_edge(node_c, node_b))
```

## Next Steps


---

*Source: test_edges.py:207 | Complexity: Intermediate | Last updated: 2026-05-05*