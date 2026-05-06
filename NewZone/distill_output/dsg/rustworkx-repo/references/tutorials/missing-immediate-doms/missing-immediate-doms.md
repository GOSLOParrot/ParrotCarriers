# How To: Missing Immediate Doms

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that the `dominance_frontiers` function doesn't regress on
https://github.com/networkx/networkx/issues/2070

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: "\n        Test that the `dominance_frontiers` function doesn't regress on\n        https://github.com/networkx/networkx/issues/2070\n        "

```python
"\n        Test that the `dominance_frontiers` function doesn't regress on\n        https://github.com/networkx/networkx/issues/2070\n        "
```

### Step 2: Assign edges = value

```python
edges = [(0, 1), (1, 2), (2, 3), (3, 4), (5, 3)]
```

### Step 3: Assign graph = rx.PyDiGraph(...)

```python
graph = rx.PyDiGraph()
```

### Step 4: Call graph.extend_from_edge_list()

```python
graph.extend_from_edge_list(edges)
```

### Step 5: Assign idom = rx.immediate_dominators(...)

```python
idom = rx.immediate_dominators(graph, 0)
```

### Step 6: Call self.assertNotIn()

```python
self.assertNotIn(5, idom)
```

### Step 7: Assign result = rx.dominance_frontiers(...)

```python
result = rx.dominance_frontiers(graph, 0)
```

### Step 8: Call self.assertDictEqual()

```python
self.assertDictEqual(result, {0: set(), 1: set(), 2: set(), 3: set(), 4: set(), 5: {3}})
```


## Complete Example

```python
# Workflow
"\n        Test that the `dominance_frontiers` function doesn't regress on\n        https://github.com/networkx/networkx/issues/2070\n        "
edges = [(0, 1), (1, 2), (2, 3), (3, 4), (5, 3)]
graph = rx.PyDiGraph()
graph.extend_from_edge_list(edges)
idom = rx.immediate_dominators(graph, 0)
self.assertNotIn(5, idom)
result = rx.dominance_frontiers(graph, 0)
self.assertDictEqual(result, {0: set(), 1: set(), 2: set(), 3: set(), 4: set(), 5: {3}})
```

## Next Steps


---

*Source: test_dominance.py:331 | Complexity: Advanced | Last updated: 2026-05-05*