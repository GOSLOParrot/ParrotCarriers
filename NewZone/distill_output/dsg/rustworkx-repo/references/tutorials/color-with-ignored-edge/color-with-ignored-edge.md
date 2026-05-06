# How To: Color With Ignored Edge

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Input:
┌─────────────┐                 ┌─────────────┐
│             │                 │             │
│    q0       │                 │    c0       │
│             │                 │             │
└───┬─────────┘                 └──────┬──────┘
    │          ┌─────────────┐         │
q0  │          │             │         │  c0
    └─────────►│     rx      │◄────────┘
    ┌──────────┤             ├─────────┐
q0  │          └─────────────┘         │  c0
    │                                  │
    │          ┌─────────────┐         │
    │          │             │         │
    └─────────►│  barrier    │         │
     ┌─────────┤             │         │
     │         └─────────────┘         │
 q0  │                                 │ c0
     │                                 │
     │         ┌─────────────┐         │
     │         │             │         │
     └────────►│     rz      │◄────────┘
    ┌──────────┤             ├─────────┐
q0  │          └─────────────┘         │  c0
    │                                  │
┌───▼─────────┐                 ┌──────▼──────┐
│             │                 │             │
│    q0       │                 │    c0       │
│             │                 │             │
└─────────────┘                 └─────────────┘

Expected: []

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: '\n        Input:\n        ┌─────────────┐                 ┌─────────────┐\n        │             │                 │             │\n        │    q0       │                 │    c0       │\n        │             │                 │             │\n        └───┬─────────┘                 └──────┬──────┘\n            │          ┌─────────────┐         │\n        q0  │          │             │         │  c0\n            └─────────►│     rx      │◄────────┘\n            ┌──────────┤             ├─────────┐\n        q0  │          └─────────────┘         │  c0\n            │                                  │\n            │          ┌─────────────┐         │\n            │          │             │         │\n            └─────────►│  barrier    │         │\n             ┌─────────┤             │         │\n             │         └─────────────┘         │\n         q0  │                                 │ c0\n             │                                 │\n             │         ┌─────────────┐         │\n             │         │             │         │\n             └────────►│     rz      │◄────────┘\n            ┌──────────┤             ├─────────┐\n        q0  │          └─────────────┘         │  c0\n            │                                  │\n        ┌───▼─────────┐                 ┌──────▼──────┐\n        │             │                 │             │\n        │    q0       │                 │    c0       │\n        │             │                 │             │\n        └─────────────┘                 └─────────────┘\n\n        Expected: []\n        '

```python
'\n        Input:\n        ┌─────────────┐                 ┌─────────────┐\n        │             │                 │             │\n        │    q0       │                 │    c0       │\n        │             │                 │             │\n        └───┬─────────┘                 └──────┬──────┘\n            │          ┌─────────────┐         │\n        q0  │          │             │         │  c0\n            └─────────►│     rx      │◄────────┘\n            ┌──────────┤             ├─────────┐\n        q0  │          └─────────────┘         │  c0\n            │                                  │\n            │          ┌─────────────┐         │\n            │          │             │         │\n            └─────────►│  barrier    │         │\n             ┌─────────┤             │         │\n             │         └─────────────┘         │\n         q0  │                                 │ c0\n             │                                 │\n             │         ┌─────────────┐         │\n             │         │             │         │\n             └────────►│     rz      │◄────────┘\n            ┌──────────┤             ├─────────┐\n        q0  │          └─────────────┘         │  c0\n            │                                  │\n        ┌───▼─────────┐                 ┌──────▼──────┐\n        │             │                 │             │\n        │    q0       │                 │    c0       │\n        │             │                 │             │\n        └─────────────┘                 └─────────────┘\n\n        Expected: []\n        '
```

### Step 2: Assign dag = rustworkx.PyDAG(...)

```python
dag = rustworkx.PyDAG()
```

### Step 3: Assign q0_list = value

```python
q0_list = []
```

### Step 4: Assign c0_list = value

```python
c0_list = []
```

### Step 5: Assign rx_gate = dag.add_node(...)

```python
rx_gate = dag.add_node('rx')
```

### Step 6: Assign barrier = dag.add_node(...)

```python
barrier = dag.add_node('barrier')
```

### Step 7: Assign rz_gate = dag.add_node(...)

```python
rz_gate = dag.add_node('rz')
```

### Step 8: Call dag.add_edge()

```python
dag.add_edge(q0_list[0], rx_gate, 'q0')
```

### Step 9: Call dag.add_edge()

```python
dag.add_edge(c0_list[0], rx_gate, 'c0')
```

### Step 10: Call dag.add_edge()

```python
dag.add_edge(rx_gate, barrier, 'q0')
```

### Step 11: Call dag.add_edge()

```python
dag.add_edge(barrier, rz_gate, 'q0')
```

### Step 12: Call dag.add_edge()

```python
dag.add_edge(rx_gate, rz_gate, 'c0')
```

### Step 13: Call dag.add_edge()

```python
dag.add_edge(rz_gate, q0_list[1], 'q0')
```

### Step 14: Call dag.add_edge()

```python
dag.add_edge(rz_gate, c0_list[1], 'c0')
```

### Step 15: Call self.assertEqual()

```python
self.assertEqual([], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))
```

### Step 16: Call q0_list.append()

```python
q0_list.append(dag.add_node('q0'))
```

### Step 17: Call c0_list.append()

```python
c0_list.append(dag.add_node('c0'))
```


## Complete Example

```python
# Workflow
'\n        Input:\n        ┌─────────────┐                 ┌─────────────┐\n        │             │                 │             │\n        │    q0       │                 │    c0       │\n        │             │                 │             │\n        └───┬─────────┘                 └──────┬──────┘\n            │          ┌─────────────┐         │\n        q0  │          │             │         │  c0\n            └─────────►│     rx      │◄────────┘\n            ┌──────────┤             ├─────────┐\n        q0  │          └─────────────┘         │  c0\n            │                                  │\n            │          ┌─────────────┐         │\n            │          │             │         │\n            └─────────►│  barrier    │         │\n             ┌─────────┤             │         │\n             │         └─────────────┘         │\n         q0  │                                 │ c0\n             │                                 │\n             │         ┌─────────────┐         │\n             │         │             │         │\n             └────────►│     rz      │◄────────┘\n            ┌──────────┤             ├─────────┐\n        q0  │          └─────────────┘         │  c0\n            │                                  │\n        ┌───▼─────────┐                 ┌──────▼──────┐\n        │             │                 │             │\n        │    q0       │                 │    c0       │\n        │             │                 │             │\n        └─────────────┘                 └─────────────┘\n\n        Expected: []\n        '
dag = rustworkx.PyDAG()
q0_list = []
c0_list = []
for _ in range(2):
    q0_list.append(dag.add_node('q0'))
    c0_list.append(dag.add_node('c0'))
rx_gate = dag.add_node('rx')
barrier = dag.add_node('barrier')
rz_gate = dag.add_node('rz')
dag.add_edge(q0_list[0], rx_gate, 'q0')
dag.add_edge(c0_list[0], rx_gate, 'c0')
dag.add_edge(rx_gate, barrier, 'q0')
dag.add_edge(barrier, rz_gate, 'q0')
dag.add_edge(rx_gate, rz_gate, 'c0')
dag.add_edge(rz_gate, q0_list[1], 'q0')
dag.add_edge(rz_gate, c0_list[1], 'c0')

def filter_function(node):
    if node == 'barrier':
        return False
    else:
        return None

def color_function(edge):
    if 'q' in edge:
        return int(edge[1:])
    else:
        return None
self.assertEqual([], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))
```

## Next Steps


---

*Source: test_collect_bicolor_runs.py:278 | Complexity: Advanced | Last updated: 2026-05-05*