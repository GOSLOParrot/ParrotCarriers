# How To: Correct Successful Path

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test correct successful path

## Prerequisites

**Required Modules:**
- `unittest`
- `numpy`
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
graph.add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (1, 4), (4, 5), (2, 5), (5, 6)])
```

### Step 4: Assign positions = value

```python
positions = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [2.5, 0.0], [1.0, 1.0], [2.0, 1.0], [3.0, 1.0]]
```

### Step 5: Assign unknown = rx.hyperbolic_greedy_routing(...)

```python
path, dist = rx.hyperbolic_greedy_routing(graph, positions, 0, 3)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(path, [0, 1, 2, 3])
```

### Step 7: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(dist, total_length(path))
```

### Step 8: Assign unknown = rx.hyperbolic_greedy_routing(...)

```python
path, dist = rx.hyperbolic_greedy_routing(graph, positions, 0, 6)
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(path, [0, 1, 2, 5, 6])
```

### Step 10: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(dist, total_length(path))
```

### Step 11: Assign x_array = np.asarray(...)

```python
x_array = np.asarray(x)
```

### Step 12: Assign y_array = np.asarray(...)

```python
y_array = np.asarray(y)
```

### Step 13: Assign dot = np.sum(...)

```python
dot = np.sum(x_array * y_array)
```

### Step 14: Assign arg = value

```python
arg = np.sqrt(1 + np.sum(x_array * x_array)) * np.sqrt(1 + np.sum(y_array * y_array)) - dot
```


## Complete Example

```python
# Workflow
graph = rx.PyGraph()
graph.add_nodes_from(range(7))
graph.add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (1, 4), (4, 5), (2, 5), (5, 6)])
positions = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [2.5, 0.0], [1.0, 1.0], [2.0, 1.0], [3.0, 1.0]]
path, dist = rx.hyperbolic_greedy_routing(graph, positions, 0, 3)

def hyperbolic_dist(x, y):
    x_array = np.asarray(x)
    y_array = np.asarray(y)
    dot = np.sum(x_array * y_array)
    arg = np.sqrt(1 + np.sum(x_array * x_array)) * np.sqrt(1 + np.sum(y_array * y_array)) - dot
    return 0 if arg < 0 else np.arccosh(arg)

def total_length(path):
    return sum((hyperbolic_dist(positions[i], positions[j]) for i, j in zip(path[:-1], np.roll(path, -1)[:-1])))
self.assertEqual(path, [0, 1, 2, 3])
self.assertAlmostEqual(dist, total_length(path))
path, dist = rx.hyperbolic_greedy_routing(graph, positions, 0, 6)
self.assertEqual(path, [0, 1, 2, 5, 6])
self.assertAlmostEqual(dist, total_length(path))
```

## Next Steps


---

*Source: test_geometry.py:80 | Complexity: Advanced | Last updated: 2026-05-05*