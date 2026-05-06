# How To: Degree Complete Graph

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test degree complete graph

## Prerequisites

**Required Modules:**
- `math`
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.complete_graph(...)

```python
graph = rustworkx.generators.complete_graph(6)
```

### Step 2: Assign cases = value

```python
cases = {(0,): 1.0, (0, 1): 1.0, (0, 2, 4): 1.0}
```

### Step 3: Assign result = rustworkx.graph_group_degree_centrality(...)

```python
result = rustworkx.graph_group_degree_centrality(graph, list(group))
```

### Step 4: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(result, expected, places=10)
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.complete_graph(6)
cases = {(0,): 1.0, (0, 1): 1.0, (0, 2, 4): 1.0}
for group, expected in cases.items():
    result = rustworkx.graph_group_degree_centrality(graph, list(group))
    self.assertAlmostEqual(result, expected, places=10)
```

## Next Steps


---

*Source: test_centrality.py:439 | Complexity: Intermediate | Last updated: 2026-05-05*