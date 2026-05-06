# How To: Condensation

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test condensation

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign condensed_graph = rustworkx.condensation(...)

```python
condensed_graph = rustworkx.condensation(self.graph)
```

### Step 2: Call self.assertEqual()

```python
self.assertEqual(len(condensed_graph.node_indices()), 2)
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual(len(condensed_graph.edge_indices()), 1)
```

### Step 4: Assign nodes = list(...)

```python
nodes = list(condensed_graph.nodes())
```

### Step 5: Assign scc1 = value

```python
scc1 = nodes[0]
```

### Step 6: Assign scc2 = value

```python
scc2 = nodes[1]
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(set(scc1) == {'a', 'b', 'c', 'd'} or set(scc2) == {'a', 'b', 'c', 'd'})
```

### Step 8: Call self.assertTrue()

```python
self.assertTrue(set(scc1) == {'e', 'f', 'g', 'h'} or set(scc2) == {'e', 'f', 'g', 'h'})
```

### Step 9: Assign weight = value

```python
weight = condensed_graph.edges()[0]
```

### Step 10: Call self.assertIn()

```python
self.assertIn('b->e', weight)
```


## Complete Example

```python
# Workflow
condensed_graph = rustworkx.condensation(self.graph)
self.assertEqual(len(condensed_graph.node_indices()), 2)
self.assertEqual(len(condensed_graph.edge_indices()), 1)
nodes = list(condensed_graph.nodes())
scc1 = nodes[0]
scc2 = nodes[1]
self.assertTrue(set(scc1) == {'a', 'b', 'c', 'd'} or set(scc2) == {'a', 'b', 'c', 'd'})
self.assertTrue(set(scc1) == {'e', 'f', 'g', 'h'} or set(scc2) == {'e', 'f', 'g', 'h'})
weight = condensed_graph.edges()[0]
self.assertIn('b->e', weight)
```

## Next Steps


---

*Source: test_strongly_connected.py:131 | Complexity: Advanced | Last updated: 2026-05-05*