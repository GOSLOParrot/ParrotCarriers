# How To: Metric Closure

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test metric closure

## Prerequisites

**Required Modules:**
- `pprint`
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign closure_graph = rustworkx.metric_closure(...)

```python
closure_graph = rustworkx.metric_closure(self.graph, weight_fn=float)
```

### Step 2: Assign expected_edges = value

```python
expected_edges = [(1, 2, (10.0, [1, 2])), (1, 3, (20.0, [1, 2, 3])), (1, 4, (22.0, [1, 2, 7, 5, 4])), (1, 5, (12.0, [1, 2, 7, 5])), (1, 6, (22.0, [1, 2, 7, 5, 6])), (1, 7, (11.0, [1, 2, 7])), (2, 3, (10.0, [2, 3])), (2, 4, (12.0, [2, 7, 5, 4])), (2, 5, (2.0, [2, 7, 5])), (2, 6, (12, [2, 7, 5, 6])), (2, 7, (1.0, [2, 7])), (3, 4, (10.0, [3, 4])), (3, 5, (12.0, [3, 2, 7, 5])), (3, 6, (22.0, [3, 2, 7, 5, 6])), (3, 7, (11.0, [3, 2, 7])), (4, 5, (10.0, [4, 5])), (4, 6, (20.0, [4, 5, 6])), (4, 7, (11.0, [4, 5, 7])), (5, 6, (10.0, [5, 6])), (5, 7, (1.0, [5, 7])), (6, 7, (11.0, [6, 5, 7]))]
```

### Step 3: Assign edges = list(...)

```python
edges = list(closure_graph.weighted_edge_list())
```

### Step 4: Assign found = False

```python
found = False
```

### Step 5: Assign found = True

```python
found = True
```

### Step 6: Call self.fail()

```python
self.fail(f'edge: {edge} nor its reverse not found in metric closure output:\n{pprint.pformat(edges)}')
```

### Step 7: Assign found = True

```python
found = True
```


## Complete Example

```python
# Workflow
closure_graph = rustworkx.metric_closure(self.graph, weight_fn=float)
expected_edges = [(1, 2, (10.0, [1, 2])), (1, 3, (20.0, [1, 2, 3])), (1, 4, (22.0, [1, 2, 7, 5, 4])), (1, 5, (12.0, [1, 2, 7, 5])), (1, 6, (22.0, [1, 2, 7, 5, 6])), (1, 7, (11.0, [1, 2, 7])), (2, 3, (10.0, [2, 3])), (2, 4, (12.0, [2, 7, 5, 4])), (2, 5, (2.0, [2, 7, 5])), (2, 6, (12, [2, 7, 5, 6])), (2, 7, (1.0, [2, 7])), (3, 4, (10.0, [3, 4])), (3, 5, (12.0, [3, 2, 7, 5])), (3, 6, (22.0, [3, 2, 7, 5, 6])), (3, 7, (11.0, [3, 2, 7])), (4, 5, (10.0, [4, 5])), (4, 6, (20.0, [4, 5, 6])), (4, 7, (11.0, [4, 5, 7])), (5, 6, (10.0, [5, 6])), (5, 7, (1.0, [5, 7])), (6, 7, (11.0, [6, 5, 7]))]
edges = list(closure_graph.weighted_edge_list())
for edge in expected_edges:
    found = False
    if edge in edges:
        found = True
    if not found:
        if (edge[1], edge[0], (edge[2][0], list(reversed(edge[2][1])))) in edges:
            found = True
    if not found:
        self.fail(f'edge: {edge} nor its reverse not found in metric closure output:\n{pprint.pformat(edges)}')
```

## Next Steps


---

*Source: test_steiner_tree.py:36 | Complexity: Intermediate | Last updated: 2026-05-05*