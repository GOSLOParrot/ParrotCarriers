# How To: Tr2

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test tr2

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph2 = rustworkx.PyDiGraph(...)

```python
graph2 = rustworkx.PyDiGraph()
```

### Step 2: Assign a = graph2.add_node(...)

```python
a = graph2.add_node('a')
```

### Step 3: Assign b = graph2.add_node(...)

```python
b = graph2.add_node('b')
```

### Step 4: Assign c = graph2.add_node(...)

```python
c = graph2.add_node('c')
```

### Step 5: Call graph2.add_edges_from()

```python
graph2.add_edges_from([(a, b, 1), (b, c, 1), (a, c, 1)])
```

### Step 6: Assign unknown = rustworkx.transitive_reduction(...)

```python
tr2, _ = rustworkx.transitive_reduction(graph2)
```

### Step 7: Call self.assertCountEqual()

```python
self.assertCountEqual(list(tr2.edge_list()), [(0, 1), (1, 2)])
```


## Complete Example

```python
# Workflow
graph2 = rustworkx.PyDiGraph()
a = graph2.add_node('a')
b = graph2.add_node('b')
c = graph2.add_node('c')
graph2.add_edges_from([(a, b, 1), (b, c, 1), (a, c, 1)])
tr2, _ = rustworkx.transitive_reduction(graph2)
self.assertCountEqual(list(tr2.edge_list()), [(0, 1), (1, 2)])
```

## Next Steps


---

*Source: test_transitive_reduction.py:32 | Complexity: Intermediate | Last updated: 2026-05-05*