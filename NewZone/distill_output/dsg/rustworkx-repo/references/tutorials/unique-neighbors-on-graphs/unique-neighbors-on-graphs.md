# How To: Unique Neighbors On Graphs

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test unique neighbors on graphs

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign dag = rustworkx.PyGraph(...)

```python
dag = rustworkx.PyGraph()
```

### Step 2: Assign node_a = dag.add_node(...)

```python
node_a = dag.add_node('a')
```

### Step 3: Assign node_b = dag.add_node(...)

```python
node_b = dag.add_node('b')
```

### Step 4: Assign node_c = dag.add_node(...)

```python
node_c = dag.add_node('c')
```

### Step 5: Call dag.add_edge()

```python
dag.add_edge(node_a, node_b, ['edge a->b'])
```

### Step 6: Call dag.add_edge()

```python
dag.add_edge(node_a, node_b, ['edge a->b bis'])
```

### Step 7: Call dag.add_edge()

```python
dag.add_edge(node_a, node_c, ['edge a->c'])
```

### Step 8: Assign res = dag.neighbors(...)

```python
res = dag.neighbors(node_a)
```

### Step 9: Call self.assertCountEqual()

```python
self.assertCountEqual([node_c, node_b], res)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyGraph()
node_a = dag.add_node('a')
node_b = dag.add_node('b')
node_c = dag.add_node('c')
dag.add_edge(node_a, node_b, ['edge a->b'])
dag.add_edge(node_a, node_b, ['edge a->b bis'])
dag.add_edge(node_a, node_c, ['edge a->c'])
res = dag.neighbors(node_a)
self.assertCountEqual([node_c, node_b], res)
```

## Next Steps


---

*Source: test_neighbors.py:29 | Complexity: Advanced | Last updated: 2026-05-05*