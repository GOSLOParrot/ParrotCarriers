# How To: Two Colors

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Input:
┌─────────────┐                 ┌─────────────┐
│             │                 │             │
│    q0       │                 │    q1       │
│             │                 │             │
└───┬─────────┘                 └──────┬──────┘
    │          ┌─────────────┐         │
q0  │          │             │         │  q1
    │          │             │         │
    └─────────►│     cx      │◄────────┘
    ┌──────────┤             ├─────────┐
    │          │             │         │
q0  │          └─────────────┘         │  q1
    │                                  │
    │          ┌─────────────┐         │
    │          │             │         │
    └─────────►│      cz     │◄────────┘
     ┌─────────┤             ├─────────┐
     │         └─────────────┘         │
 q0  │                                 │ q1
     │                                 │
 ┌───▼─────────┐                ┌──────▼──────┐
 │             │                │             │
 │    q0       │                │    q1       │
 │             │                │             │
 └─────────────┘                └─────────────┘

Expected: [[cx, cz]]

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: '\n        Input:\n        ┌─────────────┐                 ┌─────────────┐\n        │             │                 │             │\n        │    q0       │                 │    q1       │\n        │             │                 │             │\n        └───┬─────────┘                 └──────┬──────┘\n            │          ┌─────────────┐         │\n        q0  │          │             │         │  q1\n            │          │             │         │\n            └─────────►│     cx      │◄────────┘\n            ┌──────────┤             ├─────────┐\n            │          │             │         │\n        q0  │          └─────────────┘         │  q1\n            │                                  │\n            │          ┌─────────────┐         │\n            │          │             │         │\n            └─────────►│      cz     │◄────────┘\n             ┌─────────┤             ├─────────┐\n             │         └─────────────┘         │\n         q0  │                                 │ q1\n             │                                 │\n         ┌───▼─────────┐                ┌──────▼──────┐\n         │             │                │             │\n         │    q0       │                │    q1       │\n         │             │                │             │\n         └─────────────┘                └─────────────┘\n\n        Expected: [[cx, cz]]\n        '

```python
'\n        Input:\n        ┌─────────────┐                 ┌─────────────┐\n        │             │                 │             │\n        │    q0       │                 │    q1       │\n        │             │                 │             │\n        └───┬─────────┘                 └──────┬──────┘\n            │          ┌─────────────┐         │\n        q0  │          │             │         │  q1\n            │          │             │         │\n            └─────────►│     cx      │◄────────┘\n            ┌──────────┤             ├─────────┐\n            │          │             │         │\n        q0  │          └─────────────┘         │  q1\n            │                                  │\n            │          ┌─────────────┐         │\n            │          │             │         │\n            └─────────►│      cz     │◄────────┘\n             ┌─────────┤             ├─────────┐\n             │         └─────────────┘         │\n         q0  │                                 │ q1\n             │                                 │\n         ┌───▼─────────┐                ┌──────▼──────┐\n         │             │                │             │\n         │    q0       │                │    q1       │\n         │             │                │             │\n         └─────────────┘                └─────────────┘\n\n        Expected: [[cx, cz]]\n        '
```

### Step 2: Assign dag = rustworkx.PyDAG(...)

```python
dag = rustworkx.PyDAG()
```

### Step 3: Assign q0_list = value

```python
q0_list = []
```

### Step 4: Assign q1_list = value

```python
q1_list = []
```

### Step 5: Assign cx_gate = dag.add_node(...)

```python
cx_gate = dag.add_node('cx')
```

### Step 6: Assign cz_gate = dag.add_node(...)

```python
cz_gate = dag.add_node('cz')
```

### Step 7: Call dag.add_edge()

```python
dag.add_edge(q0_list[0], cx_gate, 'q0')
```

### Step 8: Call dag.add_edge()

```python
dag.add_edge(q1_list[0], cx_gate, 'q1')
```

### Step 9: Call dag.add_edge()

```python
dag.add_edge(cx_gate, cz_gate, 'q0')
```

### Step 10: Call dag.add_edge()

```python
dag.add_edge(cx_gate, cz_gate, 'q1')
```

### Step 11: Call dag.add_edge()

```python
dag.add_edge(cz_gate, q0_list[1], 'q0')
```

### Step 12: Call dag.add_edge()

```python
dag.add_edge(cz_gate, q1_list[1], 'q1')
```

### Step 13: Call self.assertEqual()

```python
self.assertEqual([['cx', 'cz']], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))
```

### Step 14: Call q0_list.append()

```python
q0_list.append(dag.add_node('q0'))
```

### Step 15: Call q1_list.append()

```python
q1_list.append(dag.add_node('q1'))
```


## Complete Example

```python
# Workflow
'\n        Input:\n        ┌─────────────┐                 ┌─────────────┐\n        │             │                 │             │\n        │    q0       │                 │    q1       │\n        │             │                 │             │\n        └───┬─────────┘                 └──────┬──────┘\n            │          ┌─────────────┐         │\n        q0  │          │             │         │  q1\n            │          │             │         │\n            └─────────►│     cx      │◄────────┘\n            ┌──────────┤             ├─────────┐\n            │          │             │         │\n        q0  │          └─────────────┘         │  q1\n            │                                  │\n            │          ┌─────────────┐         │\n            │          │             │         │\n            └─────────►│      cz     │◄────────┘\n             ┌─────────┤             ├─────────┐\n             │         └─────────────┘         │\n         q0  │                                 │ q1\n             │                                 │\n         ┌───▼─────────┐                ┌──────▼──────┐\n         │             │                │             │\n         │    q0       │                │    q1       │\n         │             │                │             │\n         └─────────────┘                └─────────────┘\n\n        Expected: [[cx, cz]]\n        '
dag = rustworkx.PyDAG()
q0_list = []
q1_list = []
for _ in range(2):
    q0_list.append(dag.add_node('q0'))
    q1_list.append(dag.add_node('q1'))
cx_gate = dag.add_node('cx')
cz_gate = dag.add_node('cz')
dag.add_edge(q0_list[0], cx_gate, 'q0')
dag.add_edge(q1_list[0], cx_gate, 'q1')
dag.add_edge(cx_gate, cz_gate, 'q0')
dag.add_edge(cx_gate, cz_gate, 'q1')
dag.add_edge(cz_gate, q0_list[1], 'q0')
dag.add_edge(cz_gate, q1_list[1], 'q1')

def filter_function(node):
    if node in ['cx', 'cz']:
        return True
    else:
        return None

def color_function(edge):
    if 'q' in edge:
        return int(edge[1:])
    else:
        return None
self.assertEqual([['cx', 'cz']], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))
```

## Next Steps


---

*Source: test_collect_bicolor_runs.py:47 | Complexity: Advanced | Last updated: 2026-05-05*