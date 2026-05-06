# How To: Invalid Positions Error

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test invalid positions error

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
graph.add_nodes_from([0, 1])
```

### Step 3: Assign positions = value

```python
positions = [[0.0, 0.0]]
```

### Step 4: Assign positions = value

```python
positions = [[0.0, 0.0], [0.0, 0.0, 0.0]]
```

### Step 5: Assign positions = value

```python
positions = [[0.0, 0.0], [0.0]]
```

### Step 6: Call rx.hyperbolic_greedy_routing()

```python
rx.hyperbolic_greedy_routing(graph, positions, 0, 1)
```

### Step 7: Call rx.hyperbolic_greedy_success_rate()

```python
rx.hyperbolic_greedy_success_rate(graph, positions)
```

### Step 8: Call rx.hyperbolic_greedy_routing()

```python
rx.hyperbolic_greedy_routing(graph, positions, 0, 1)
```

### Step 9: Call rx.hyperbolic_greedy_success_rate()

```python
rx.hyperbolic_greedy_success_rate(graph, positions)
```

### Step 10: Call rx.hyperbolic_greedy_routing()

```python
rx.hyperbolic_greedy_routing(graph, positions, 0, 1)
```

### Step 11: Call rx.hyperbolic_greedy_success_rate()

```python
rx.hyperbolic_greedy_success_rate(graph, positions)
```


## Complete Example

```python
# Workflow
graph = rx.PyGraph()
graph.add_nodes_from([0, 1])
positions = [[0.0, 0.0]]
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_routing(graph, positions, 0, 1)
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_success_rate(graph, positions)
positions = [[0.0, 0.0], [0.0, 0.0, 0.0]]
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_routing(graph, positions, 0, 1)
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_success_rate(graph, positions)
positions = [[0.0, 0.0], [0.0]]
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_routing(graph, positions, 0, 1)
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_success_rate(graph, positions)
```

## Next Steps


---

*Source: test_geometry.py:41 | Complexity: Advanced | Last updated: 2026-05-05*