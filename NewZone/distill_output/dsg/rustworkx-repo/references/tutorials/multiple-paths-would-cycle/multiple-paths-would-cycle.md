# How To: Multiple Paths Would Cycle

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow:     ┌─┐     ┌─┐                  ┌─┐     ┌─┐
 ┌3─┤c│     │e├─5┐            ┌──┤c│     │e├──┐
 │  └┬┘     └┬┘  │            │  └┬┘     └┬┘  │
┌┴┐  2  ┌─┐  4  ┌┴┐           │   2  ┌─┐  4   │
│d│  └──┤b├──┘  │f│   ───►    │   └──┤b├──┘   │
└─┘     └┬┘     └─┘           3      └┬┘      5
         1                    │       1       │
        ┌┴┐                   │      ┌┴┐      │
        │a│                   └──────┤m├──────┘
        └─┘                          └─┘

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: '\n            ┌─┐     ┌─┐                  ┌─┐     ┌─┐\n         ┌3─┤c│     │e├─5┐            ┌──┤c│     │e├──┐\n         │  └┬┘     └┬┘  │            │  └┬┘     └┬┘  │\n        ┌┴┐  2  ┌─┐  4  ┌┴┐           │   2  ┌─┐  4   │\n        │d│  └──┤b├──┘  │f│   ───►    │   └──┤b├──┘   │\n        └─┘     └┬┘     └─┘           3      └┬┘      5\n                 1                    │       1       │\n                ┌┴┐                   │      ┌┴┐      │\n                │a│                   └──────┤m├──────┘\n                └─┘                          └─┘\n        '

```python
'\n            ┌─┐     ┌─┐                  ┌─┐     ┌─┐\n         ┌3─┤c│     │e├─5┐            ┌──┤c│     │e├──┐\n         │  └┬┘     └┬┘  │            │  └┬┘     └┬┘  │\n        ┌┴┐  2  ┌─┐  4  ┌┴┐           │   2  ┌─┐  4   │\n        │d│  └──┤b├──┘  │f│   ───►    │   └──┤b├──┘   │\n        └─┘     └┬┘     └─┘           3      └┬┘      5\n                 1                    │       1       │\n                ┌┴┐                   │      ┌┴┐      │\n                │a│                   └──────┤m├──────┘\n                └─┘                          └─┘\n        '
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

### Step 7: Assign node_e = dag.add_node(...)

```python
node_e = dag.add_node('e')
```

### Step 8: Assign node_f = dag.add_node(...)

```python
node_f = dag.add_node('f')
```

### Step 9: Call dag.add_edge()

```python
dag.add_edge(node_a, node_b, 1)
```

### Step 10: Call dag.add_edge()

```python
dag.add_edge(node_b, node_c, 2)
```

### Step 11: Call dag.add_edge()

```python
dag.add_edge(node_c, node_d, 3)
```

### Step 12: Call dag.add_edge()

```python
dag.add_edge(node_b, node_e, 4)
```

### Step 13: Call dag.add_edge()

```python
dag.add_edge(node_e, node_f, 5)
```

### Step 14: Assign node_m = dag.contract_nodes(...)

```python
node_m = dag.contract_nodes([node_a, node_d, node_f], 'm')
```

### Step 15: Call self.assertEqual()

```python
self.assertEqual([node_b, node_c, node_e, node_m], list(dag.node_indexes()))
```

### Step 16: Call self.assertEqual()

```python
self.assertEqual({UndirectedEdge((node_b, node_c)), UndirectedEdge((node_c, node_m)), UndirectedEdge((node_e, node_m)), UndirectedEdge((node_b, node_e)), UndirectedEdge((node_b, node_m))}, set((UndirectedEdge(e) for e in dag.edge_list())))
```


## Complete Example

```python
# Workflow
'\n            ┌─┐     ┌─┐                  ┌─┐     ┌─┐\n         ┌3─┤c│     │e├─5┐            ┌──┤c│     │e├──┐\n         │  └┬┘     └┬┘  │            │  └┬┘     └┬┘  │\n        ┌┴┐  2  ┌─┐  4  ┌┴┐           │   2  ┌─┐  4   │\n        │d│  └──┤b├──┘  │f│   ───►    │   └──┤b├──┘   │\n        └─┘     └┬┘     └─┘           3      └┬┘      5\n                 1                    │       1       │\n                ┌┴┐                   │      ┌┴┐      │\n                │a│                   └──────┤m├──────┘\n                └─┘                          └─┘\n        '
dag = rustworkx.PyGraph()
node_a = dag.add_node('a')
node_b = dag.add_node('b')
node_c = dag.add_node('c')
node_d = dag.add_node('d')
node_e = dag.add_node('e')
node_f = dag.add_node('f')
dag.add_edge(node_a, node_b, 1)
dag.add_edge(node_b, node_c, 2)
dag.add_edge(node_c, node_d, 3)
dag.add_edge(node_b, node_e, 4)
dag.add_edge(node_e, node_f, 5)
node_m = dag.contract_nodes([node_a, node_d, node_f], 'm')
self.assertEqual([node_b, node_c, node_e, node_m], list(dag.node_indexes()))
self.assertEqual({UndirectedEdge((node_b, node_c)), UndirectedEdge((node_c, node_m)), UndirectedEdge((node_e, node_m)), UndirectedEdge((node_b, node_e)), UndirectedEdge((node_b, node_m))}, set((UndirectedEdge(e) for e in dag.edge_list())))
```

## Next Steps


---

*Source: test_contract_nodes.py:92 | Complexity: Advanced | Last updated: 2026-05-05*