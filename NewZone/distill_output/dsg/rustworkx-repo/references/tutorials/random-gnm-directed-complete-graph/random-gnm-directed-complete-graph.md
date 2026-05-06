# How To: Random Gnm Directed Complete Graph

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test random gnm directed complete graph

## Prerequisites

**Required Modules:**
- `unittest`
- `random`
- `math`
- `numpy`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign n = 20

```python
n = 20
```

### Step 2: Assign max_m = value

```python
max_m = n * (n - 1)
```

### Step 3: Assign graph = rustworkx.directed_gnm_random_graph(...)

```python
graph = rustworkx.directed_gnm_random_graph(n, max_m)
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(len(graph), n)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(len(graph.edges()), max_m)
```

### Step 6: Assign graph = rustworkx.directed_gnm_random_graph(...)

```python
graph = rustworkx.directed_gnm_random_graph(n, max_m + 1)
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(len(graph), n)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(len(graph.edges()), max_m)
```

### Step 9: Assign graph = rustworkx.directed_gnm_random_graph(...)

```python
graph = rustworkx.directed_gnm_random_graph(n, max_m, 55)
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(len(graph), n)
```

### Step 11: Call self.assertEqual()

```python
self.assertEqual(len(graph.edges()), max_m)
```


## Complete Example

```python
# Workflow
n = 20
max_m = n * (n - 1)
graph = rustworkx.directed_gnm_random_graph(n, max_m)
self.assertEqual(len(graph), n)
self.assertEqual(len(graph.edges()), max_m)
graph = rustworkx.directed_gnm_random_graph(n, max_m + 1)
self.assertEqual(len(graph), n)
self.assertEqual(len(graph.edges()), max_m)
graph = rustworkx.directed_gnm_random_graph(n, max_m, 55)
self.assertEqual(len(graph), n)
self.assertEqual(len(graph.edges()), max_m)
```

## Next Steps


---

*Source: test_random.py:106 | Complexity: Advanced | Last updated: 2026-05-05*