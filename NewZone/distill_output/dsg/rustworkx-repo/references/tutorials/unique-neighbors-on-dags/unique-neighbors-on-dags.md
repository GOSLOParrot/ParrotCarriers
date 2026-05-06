# How To: Unique Neighbors On Dags

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test unique neighbors on dags

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
node_b = dag.add_child(node_a, 'b', ['edge a->b'])
```

### Step 4: Assign node_c = dag.add_child(...)

```python
node_c = dag.add_child(node_a, 'c', ['edge a->c'])
```

### Step 5: Call dag.add_edge()

```python
dag.add_edge(node_a, node_b, ['edge a->b bis'])
```

### Step 6: Assign res = dag.neighbors(...)

```python
res = dag.neighbors(node_a)
```

### Step 7: Call self.assertCountEqual()

```python
self.assertCountEqual([node_c, node_b], res)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', ['edge a->b'])
node_c = dag.add_child(node_a, 'c', ['edge a->c'])
dag.add_edge(node_a, node_b, ['edge a->b bis'])
res = dag.neighbors(node_a)
self.assertCountEqual([node_c, node_b], res)
```

## Next Steps


---

*Source: test_neighbors.py:28 | Complexity: Intermediate | Last updated: 2026-05-05*