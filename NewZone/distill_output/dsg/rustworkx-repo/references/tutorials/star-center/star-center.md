# How To: Star Center

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test star center

## Prerequisites

**Required Modules:**
- `math`
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 2: Assign center = graph.add_node(...)

```python
center = graph.add_node('center')
```

### Step 3: Assign result = rustworkx.graph_group_betweenness_centrality(...)

```python
result = rustworkx.graph_group_betweenness_centrality(graph, [center], normalized=False)
```

### Step 4: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(result, 6.0)
```

### Step 5: Assign leaf = graph.add_node(...)

```python
leaf = graph.add_node('leaf')
```

### Step 6: Call graph.add_edge()

```python
graph.add_edge(center, leaf, None)
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
center = graph.add_node('center')
for _ in range(4):
    leaf = graph.add_node('leaf')
    graph.add_edge(center, leaf, None)
result = rustworkx.graph_group_betweenness_centrality(graph, [center], normalized=False)
self.assertAlmostEqual(result, 6.0)
```

## Next Steps


---

*Source: test_centrality.py:385 | Complexity: Intermediate | Last updated: 2026-05-05*