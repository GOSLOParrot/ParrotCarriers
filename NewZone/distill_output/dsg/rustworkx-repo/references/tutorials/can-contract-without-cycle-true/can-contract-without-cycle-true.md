# How To: Can Contract Without Cycle True

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test can contract without cycle true

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyDiGraph(...)

```python
graph = rustworkx.PyDiGraph()
```

### Step 2: Assign a = graph.add_node(...)

```python
a = graph.add_node('a')
```

### Step 3: Assign b = graph.add_node(...)

```python
b = graph.add_node('b')
```

### Step 4: Assign c = graph.add_node(...)

```python
c = graph.add_node('c')
```

### Step 5: Call graph.add_edge()

```python
graph.add_edge(a, b, 0)
```

### Step 6: Call graph.add_edge()

```python
graph.add_edge(b, c, 0)
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(graph.can_contract_without_cycle([b, c]))
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyDiGraph()
a = graph.add_node('a')
b = graph.add_node('b')
c = graph.add_node('c')
graph.add_edge(a, b, 0)
graph.add_edge(b, c, 0)
self.assertTrue(graph.can_contract_without_cycle([b, c]))
```

## Next Steps


---

*Source: test_contract_nodes.py:269 | Complexity: Intermediate | Last updated: 2026-05-05*