# How To: Tr1

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test tr1

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyDiGraph(...)

```python
graph = rustworkx.PyDiGraph()
```

### Step 2: Assign a = graph.add_node(...)

```python
a = graph.add_node('a')
```

### Step 3: Assign b = graph.add_node(...)

```python
b = graph.add_node('b')
```

### Step 4: Assign c = graph.add_node(...)

```python
c = graph.add_node('c')
```

### Step 5: Assign d = graph.add_node(...)

```python
d = graph.add_node('d')
```

### Step 6: Assign e = graph.add_node(...)

```python
e = graph.add_node('e')
```

### Step 7: Call graph.add_edges_from()

```python
graph.add_edges_from([(a, b, 1), (a, d, 1), (a, c, 1), (a, e, 1), (b, d, 1), (c, d, 1), (c, e, 1), (d, e, 1)])
```

### Step 8: Assign unknown = rustworkx.transitive_reduction(...)

```python
tr, _ = rustworkx.transitive_reduction(graph)
```

### Step 9: Call self.assertCountEqual()

```python
self.assertCountEqual(list(tr.edge_list()), [(0, 2), (0, 1), (1, 3), (2, 3), (3, 4)])
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyDiGraph()
a = graph.add_node('a')
b = graph.add_node('b')
c = graph.add_node('c')
d = graph.add_node('d')
e = graph.add_node('e')
graph.add_edges_from([(a, b, 1), (a, d, 1), (a, c, 1), (a, e, 1), (b, d, 1), (c, d, 1), (c, e, 1), (d, e, 1)])
tr, _ = rustworkx.transitive_reduction(graph)
self.assertCountEqual(list(tr.edge_list()), [(0, 2), (0, 1), (1, 3), (2, 3), (3, 4)])
```

## Next Steps


---

*Source: test_transitive_reduction.py:19 | Complexity: Advanced | Last updated: 2026-05-05*