# How To: Many Parents

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test many parents

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign dag = rustworkx.PyDAG(...)

```python
dag = rustworkx.PyDAG()
```

### Step 2: Assign node_a = dag.add_node(...)

```python
node_a = dag.add_node('a')
```

### Step 3: Assign res_even = dag.find_predecessors_by_edge(...)

```python
res_even = dag.find_predecessors_by_edge(node_a, lambda x: x['edge'] % 2 == 0)
```

### Step 4: Assign res_odd = dag.find_predecessors_by_edge(...)

```python
res_odd = dag.find_predecessors_by_edge(node_a, lambda x: x['edge'] % 2 != 0)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual([{'numeral': 8}, {'numeral': 6}, {'numeral': 4}, {'numeral': 2}, {'numeral': 0}], res_even)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual([{'numeral': 9}, {'numeral': 7}, {'numeral': 5}, {'numeral': 3}, {'numeral': 1}], res_odd)
```

### Step 7: Call dag.add_parent()

```python
dag.add_parent(node_a, {'numeral': i}, {'edge': i})
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
for i in range(10):
    dag.add_parent(node_a, {'numeral': i}, {'edge': i})
res_even = dag.find_predecessors_by_edge(node_a, lambda x: x['edge'] % 2 == 0)
res_odd = dag.find_predecessors_by_edge(node_a, lambda x: x['edge'] % 2 != 0)
self.assertEqual([{'numeral': 8}, {'numeral': 6}, {'numeral': 4}, {'numeral': 2}, {'numeral': 0}], res_even)
self.assertEqual([{'numeral': 9}, {'numeral': 7}, {'numeral': 5}, {'numeral': 3}, {'numeral': 1}], res_odd)
```

## Next Steps


---

*Source: test_pred_succ.py:144 | Complexity: Intermediate | Last updated: 2026-05-05*