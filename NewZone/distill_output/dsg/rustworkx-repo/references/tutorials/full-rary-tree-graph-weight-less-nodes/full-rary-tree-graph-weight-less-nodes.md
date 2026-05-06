# How To: Full Rary Tree Graph Weight Less Nodes

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test full rary tree graph weight less nodes

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.full_rary_tree(...)

```python
graph = rustworkx.generators.full_rary_tree(2, 6, weights=list(range(4)))
```

### Step 2: Call self.assertEqual()

```python
self.assertEqual(len(graph), 6)
```

### Step 3: Assign expected_weights = value

```python
expected_weights = [x for x in range(4)]
```

### Step 4: Call expected_weights.extend()

```python
expected_weights.extend([None, None])
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(expected_weights, graph.nodes())
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(len(graph.edges()), 5)
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.full_rary_tree(2, 6, weights=list(range(4)))
self.assertEqual(len(graph), 6)
expected_weights = [x for x in range(4)]
expected_weights.extend([None, None])
self.assertEqual(expected_weights, graph.nodes())
self.assertEqual(len(graph.edges()), 5)
```

## Next Steps


---

*Source: test_full_rary_tree.py:75 | Complexity: Intermediate | Last updated: 2026-05-05*