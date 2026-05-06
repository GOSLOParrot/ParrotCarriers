# How To: Betweenness Complete Digraph

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test betweenness complete digraph

## Prerequisites

**Required Modules:**
- `math`
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.directed_complete_graph(...)

```python
graph = rustworkx.generators.directed_complete_graph(5)
```

### Step 2: Assign cases = value

```python
cases = {(0,): 0.0, (0, 1): 0.0, (0, 2, 4): 0.0}
```

### Step 3: Assign result = rustworkx.digraph_group_betweenness_centrality(...)

```python
result = rustworkx.digraph_group_betweenness_centrality(graph, list(group), normalized=True)
```

### Step 4: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(result, expected, places=10)
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.directed_complete_graph(5)
cases = {(0,): 0.0, (0, 1): 0.0, (0, 2, 4): 0.0}
for group, expected in cases.items():
    result = rustworkx.digraph_group_betweenness_centrality(graph, list(group), normalized=True)
    self.assertAlmostEqual(result, expected, places=10)
```

## Next Steps


---

*Source: test_centrality.py:547 | Complexity: Intermediate | Last updated: 2026-05-05*