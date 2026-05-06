# How To: Random Geometric Complete

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test random geometric complete

## Prerequisites

**Required Modules:**
- `unittest`
- `random`
- `math`
- `numpy`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign r = 1.42

```python
r = 1.42
```

### Step 2: Assign graph = rustworkx.random_geometric_graph(...)

```python
graph = rustworkx.random_geometric_graph(10, r)
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual(len(graph), 10)
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(len(graph.edges()), 45)
```


## Complete Example

```python
# Workflow
r = 1.42
graph = rustworkx.random_geometric_graph(10, r)
self.assertEqual(len(graph), 10)
self.assertEqual(len(graph.edges()), 45)
```

## Next Steps


---

*Source: test_random.py:268 | Complexity: Intermediate | Last updated: 2026-05-05*