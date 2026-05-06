# How To: Random Gnp Undirected Complete Graph

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test random gnp undirected complete graph

## Prerequisites

**Required Modules:**
- `unittest`
- `random`
- `math`
- `numpy`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.undirected_gnp_random_graph(...)

```python
graph = rustworkx.undirected_gnp_random_graph(20, 1)
```

### Step 2: Call self.assertEqual()

```python
self.assertEqual(len(graph), 20)
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual(len(graph.edges()), 20 * (20 - 1) / 2)
```


## Complete Example

```python
# Workflow
graph = rustworkx.undirected_gnp_random_graph(20, 1)
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 20 * (20 - 1) / 2)
```

## Next Steps


---

*Source: test_random.py:69 | Complexity: Beginner | Last updated: 2026-05-05*