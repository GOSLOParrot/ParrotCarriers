# How To: Full Rary Tree Graph Weights

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test full rary tree graph weights

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.full_rary_tree(...)

```python
graph = rustworkx.generators.full_rary_tree(2, 4, weights=list(range(4)))
```

### Step 2: Assign expected_edges = value

```python
expected_edges = [(0, 1), (0, 2), (1, 3)]
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual(len(graph), 4)
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual([x for x in range(4)], graph.nodes())
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(len(graph.edges()), 3)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(list(graph.edge_list()), expected_edges)
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.full_rary_tree(2, 4, weights=list(range(4)))
expected_edges = [(0, 1), (0, 2), (1, 3)]
self.assertEqual(len(graph), 4)
self.assertEqual([x for x in range(4)], graph.nodes())
self.assertEqual(len(graph.edges()), 3)
self.assertEqual(list(graph.edge_list()), expected_edges)
```

## Next Steps


---

*Source: test_full_rary_tree.py:67 | Complexity: Intermediate | Last updated: 2026-05-05*