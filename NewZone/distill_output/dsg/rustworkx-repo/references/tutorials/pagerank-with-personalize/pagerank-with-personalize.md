# How To: Pagerank With Personalize

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test pagerank with personalize

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: Assign rx_graph = rustworkx.generators.directed_complete_graph(...)

```python
rx_graph = rustworkx.generators.directed_complete_graph(4)
```

### Step 2: Assign personalize = value

```python
personalize = {0: 0, 1: 0, 2: 0, 3: 1}
```

### Step 3: Assign alpha = 0.85

```python
alpha = 0.85
```

### Step 4: Assign rx_ranks = rustworkx.pagerank(...)

```python
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha, personalization=personalize)
```

### Step 5: Assign nx_graph = nx.DiGraph(...)

```python
nx_graph = nx.DiGraph(list(rx_graph.edge_list()))
```

### Step 6: Assign nx_ranks = pagerank_python(...)

```python
nx_ranks = pagerank_python(nx_graph, alpha=alpha, personalization=personalize)
```

### Step 7: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```


## Complete Example

```python
# Workflow
rx_graph = rustworkx.generators.directed_complete_graph(4)
personalize = {0: 0, 1: 0, 2: 0, 3: 1}
alpha = 0.85
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha, personalization=personalize)
nx_graph = nx.DiGraph(list(rx_graph.edge_list()))
nx_ranks = pagerank_python(nx_graph, alpha=alpha, personalization=personalize)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```

## Next Steps


---

*Source: test_pagerank.py:236 | Complexity: Intermediate | Last updated: 2026-05-05*