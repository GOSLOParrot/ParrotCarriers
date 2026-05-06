# How To: Complete Graph

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test complete graph

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

### Step 2: Assign centrality = rustworkx.digraph_katz_centrality(...)

```python
centrality = rustworkx.digraph_katz_centrality(graph)
```

### Step 3: Assign expected_value = math.sqrt(...)

```python
expected_value = math.sqrt(1.0 / 5.0)
```

### Step 4: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(value, expected_value, delta=0.0001)
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.directed_complete_graph(5)
centrality = rustworkx.digraph_katz_centrality(graph)
expected_value = math.sqrt(1.0 / 5.0)
for value in centrality.values():
    self.assertAlmostEqual(value, expected_value, delta=0.0001)
```

## Next Steps


---

*Source: test_centrality.py:183 | Complexity: Intermediate | Last updated: 2026-05-05*