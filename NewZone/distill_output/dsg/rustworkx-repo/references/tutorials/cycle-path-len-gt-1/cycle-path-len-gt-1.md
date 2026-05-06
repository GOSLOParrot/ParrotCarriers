# How To: Cycle Path Len Gt 1

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow:     ┌─┐              ┌─┐
 ┌4─┤a├─1┐           │m├──1───┐
 │  └─┘  │           └┬┘      │
┌┴┐     ┌┴┐           │      ┌┴┐
│d│     │b│   ───►    │      │b│
└┬┘     └┬┘           │      └┬┘
 │  ┌─┐  2            │  ┌─┐  2
 └3─┤c├──┘            └3─┤c├──┘
    └─┘                  └─┘

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: '\n            ┌─┐              ┌─┐\n         ┌4─┤a├─1┐           │m├──1───┐\n         │  └─┘  │           └┬┘      │\n        ┌┴┐     ┌┴┐           │      ┌┴┐\n        │d│     │b│   ───►    │      │b│\n        └┬┘     └┬┘           │      └┬┘\n         │  ┌─┐  2            │  ┌─┐  2\n         └3─┤c├──┘            └3─┤c├──┘\n            └─┘                  └─┘\n        '

```python
'\n            ┌─┐              ┌─┐\n         ┌4─┤a├─1┐           │m├──1───┐\n         │  └─┘  │           └┬┘      │\n        ┌┴┐     ┌┴┐           │      ┌┴┐\n        │d│     │b│   ───►    │      │b│\n        └┬┘     └┬┘           │      └┬┘\n         │  ┌─┐  2            │  ┌─┐  2\n         └3─┤c├──┘            └3─┤c├──┘\n            └─┘                  └─┘\n        '
```

### Step 2: Assign dag = rustworkx.PyGraph(...)

```python
dag = rustworkx.PyGraph()
```

### Step 3: Assign node_a = dag.add_node(...)

```python
node_a = dag.add_node('a')
```

### Step 4: Assign node_b = dag.add_node(...)

```python
node_b = dag.add_node('b')
```

### Step 5: Assign node_c = dag.add_node(...)

```python
node_c = dag.add_node('c')
```

### Step 6: Assign node_d = dag.add_node(...)

```python
node_d = dag.add_node('d')
```

### Step 7: Call dag.add_edge()

```python
dag.add_edge(node_a, node_b, 1)
```

### Step 8: Call dag.add_edge()

```python
dag.add_edge(node_b, node_c, 2)
```

### Step 9: Call dag.add_edge()

```python
dag.add_edge(node_c, node_d, 3)
```

### Step 10: Call dag.add_edge()

```python
dag.add_edge(node_a, node_d, 4)
```

### Step 11: Assign node_m = dag.contract_nodes(...)

```python
node_m = dag.contract_nodes([node_a, node_d], 'm')
```

### Step 12: Call self.assertEqual()

```python
self.assertEqual([node_b, node_c, node_m], dag.node_indexes())
```

### Step 13: Call self.assertEqual()

```python
self.assertEqual({UndirectedEdge((node_b, node_c)), UndirectedEdge((node_c, node_m)), UndirectedEdge((node_b, node_m))}, set((UndirectedEdge(e) for e in dag.edge_list())))
```


## Complete Example

```python
# Workflow
'\n            ┌─┐              ┌─┐\n         ┌4─┤a├─1┐           │m├──1───┐\n         │  └─┘  │           └┬┘      │\n        ┌┴┐     ┌┴┐           │      ┌┴┐\n        │d│     │b│   ───►    │      │b│\n        └┬┘     └┬┘           │      └┬┘\n         │  ┌─┐  2            │  ┌─┐  2\n         └3─┤c├──┘            └3─┤c├──┘\n            └─┘                  └─┘\n        '
dag = rustworkx.PyGraph()
node_a = dag.add_node('a')
node_b = dag.add_node('b')
node_c = dag.add_node('c')
node_d = dag.add_node('d')
dag.add_edge(node_a, node_b, 1)
dag.add_edge(node_b, node_c, 2)
dag.add_edge(node_c, node_d, 3)
dag.add_edge(node_a, node_d, 4)
node_m = dag.contract_nodes([node_a, node_d], 'm')
self.assertEqual([node_b, node_c, node_m], dag.node_indexes())
self.assertEqual({UndirectedEdge((node_b, node_c)), UndirectedEdge((node_c, node_m)), UndirectedEdge((node_b, node_m))}, set((UndirectedEdge(e) for e in dag.edge_list())))
```

## Next Steps


---

*Source: test_contract_nodes.py:57 | Complexity: Advanced | Last updated: 2026-05-05*