# How To: Node Frequency

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test node frequency

## Prerequisites

**Required Modules:**
- `collections`
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rx.PyGraph(...)

```python
graph = rx.PyGraph()
```

### Step 2: Call graph.add_nodes_from()

```python
graph.add_nodes_from(range(7))
```

### Step 3: Call graph.add_edges_from_no_data()

```python
graph.add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (4, 5), (2, 4), (2, 5), (5, 6)])
```

### Step 4: Assign path_length = 5000

```python
path_length = 5000
```

### Step 5: Assign path = rx.generate_random_path(...)

```python
path = rx.generate_random_path(graph, 0, path_length, 5)
```

### Step 6: Assign counts = collections.Counter(...)

```python
counts = collections.Counter(path)
```

### Step 7: Assign tol = 0.01

```python
tol = 0.01
```

### Step 8: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(counts[0] / (path_length + 1), 1 / 14, delta=tol)
```

### Step 9: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(counts[1] / (path_length + 1), 2 / 14, delta=tol)
```

### Step 10: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(counts[2] / (path_length + 1), 4 / 14, delta=tol)
```

### Step 11: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(counts[3] / (path_length + 1), 1 / 14, delta=tol)
```

### Step 12: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(counts[4] / (path_length + 1), 2 / 14, delta=tol)
```

### Step 13: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(counts[5] / (path_length + 1), 3 / 14, delta=tol)
```

### Step 14: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(counts[6] / (path_length + 1), 1 / 14, delta=tol)
```


## Complete Example

```python
# Workflow
graph = rx.PyGraph()
graph.add_nodes_from(range(7))
graph.add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (4, 5), (2, 4), (2, 5), (5, 6)])
path_length = 5000
path = rx.generate_random_path(graph, 0, path_length, 5)
counts = collections.Counter(path)
tol = 0.01
self.assertAlmostEqual(counts[0] / (path_length + 1), 1 / 14, delta=tol)
self.assertAlmostEqual(counts[1] / (path_length + 1), 2 / 14, delta=tol)
self.assertAlmostEqual(counts[2] / (path_length + 1), 4 / 14, delta=tol)
self.assertAlmostEqual(counts[3] / (path_length + 1), 1 / 14, delta=tol)
self.assertAlmostEqual(counts[4] / (path_length + 1), 2 / 14, delta=tol)
self.assertAlmostEqual(counts[5] / (path_length + 1), 3 / 14, delta=tol)
self.assertAlmostEqual(counts[6] / (path_length + 1), 1 / 14, delta=tol)
```

## Next Steps


---

*Source: test_random_walk.py:31 | Complexity: Advanced | Last updated: 2026-05-05*