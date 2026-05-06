# How To: Dagcircuit Basic Index Output

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test dagcircuit basic index output

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign dag = rustworkx.PyDAG(...)

```python
dag = rustworkx.PyDAG()
```

### Step 2: Assign qr_0_in = dag.add_node(...)

```python
qr_0_in = dag.add_node('qr[0]')
```

### Step 3: Assign qr_0_out = dag.add_node(...)

```python
qr_0_out = dag.add_node('qr[0]')
```

### Step 4: Assign qr_1_in = dag.add_node(...)

```python
qr_1_in = dag.add_node('qr[1]')
```

### Step 5: Assign qr_1_out = dag.add_node(...)

```python
qr_1_out = dag.add_node('qr[1]')
```

### Step 6: Assign cr_0_in = dag.add_node(...)

```python
cr_0_in = dag.add_node('cr[0]')
```

### Step 7: Assign cr_0_out = dag.add_node(...)

```python
cr_0_out = dag.add_node('cr[0]')
```

### Step 8: Assign cr_1_in = dag.add_node(...)

```python
cr_1_in = dag.add_node('cr[1]')
```

### Step 9: Assign cr_1_out = dag.add_node(...)

```python
cr_1_out = dag.add_node('cr[1]')
```

### Step 10: Assign input_nodes = value

```python
input_nodes = [qr_0_in, qr_1_in, cr_0_in, cr_1_in]
```

### Step 11: Assign h_gate = dag.add_child(...)

```python
h_gate = dag.add_child(qr_0_in, 'h', 'qr[0]')
```

### Step 12: Assign cx_gate = dag.add_child(...)

```python
cx_gate = dag.add_child(h_gate, 'cx', 'qr[0]')
```

### Step 13: Call dag.add_edge()

```python
dag.add_edge(qr_1_in, cx_gate, 'qr[1]')
```

### Step 14: Assign measure_qr_1 = dag.add_child(...)

```python
measure_qr_1 = dag.add_child(cx_gate, 'measure', 'qr[1]')
```

### Step 15: Call dag.add_edge()

```python
dag.add_edge(cr_1_in, measure_qr_1, 'cr[1]')
```

### Step 16: Assign x_gate = dag.add_child(...)

```python
x_gate = dag.add_child(measure_qr_1, 'x', 'qr[1]')
```

### Step 17: Call dag.add_edge()

```python
dag.add_edge(measure_qr_1, x_gate, 'cr[1]')
```

### Step 18: Call dag.add_edge()

```python
dag.add_edge(cr_0_in, x_gate, 'cr[0]')
```

### Step 19: Assign measure_qr_0 = dag.add_child(...)

```python
measure_qr_0 = dag.add_child(cx_gate, 'measure', 'qr[0]')
```

### Step 20: Call dag.add_edge()

```python
dag.add_edge(measure_qr_0, qr_0_out, 'qr[0]')
```

### Step 21: Call dag.add_edge()

```python
dag.add_edge(measure_qr_0, cr_0_out, 'cr[0]')
```

### Step 22: Call dag.add_edge()

```python
dag.add_edge(x_gate, measure_qr_0, 'cr[0]')
```

### Step 23: Assign measure_qr_1_out = dag.add_child(...)

```python
measure_qr_1_out = dag.add_child(x_gate, 'measure', 'cr[1]')
```

### Step 24: Call dag.add_edge()

```python
dag.add_edge(x_gate, measure_qr_1_out, 'qr[1]')
```

### Step 25: Call dag.add_edge()

```python
dag.add_edge(measure_qr_1_out, qr_1_out, 'qr[1]')
```

### Step 26: Call dag.add_edge()

```python
dag.add_edge(measure_qr_1_out, cr_1_out, 'cr[1]')
```

### Step 27: Assign res = rustworkx.layers(...)

```python
res = rustworkx.layers(dag, input_nodes, index_output=True)
```

### Step 28: Assign expected = value

```python
expected = [[qr_0_in, qr_1_in, cr_0_in, cr_1_in], [h_gate], [cx_gate], [measure_qr_1], [x_gate], [measure_qr_1_out, measure_qr_0], [cr_1_out, qr_1_out, cr_0_out, qr_0_out]]
```

### Step 29: Call self.assertEqual()

```python
self.assertEqual(expected, res)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
qr_0_in = dag.add_node('qr[0]')
qr_0_out = dag.add_node('qr[0]')
qr_1_in = dag.add_node('qr[1]')
qr_1_out = dag.add_node('qr[1]')
cr_0_in = dag.add_node('cr[0]')
cr_0_out = dag.add_node('cr[0]')
cr_1_in = dag.add_node('cr[1]')
cr_1_out = dag.add_node('cr[1]')
input_nodes = [qr_0_in, qr_1_in, cr_0_in, cr_1_in]
h_gate = dag.add_child(qr_0_in, 'h', 'qr[0]')
cx_gate = dag.add_child(h_gate, 'cx', 'qr[0]')
dag.add_edge(qr_1_in, cx_gate, 'qr[1]')
measure_qr_1 = dag.add_child(cx_gate, 'measure', 'qr[1]')
dag.add_edge(cr_1_in, measure_qr_1, 'cr[1]')
x_gate = dag.add_child(measure_qr_1, 'x', 'qr[1]')
dag.add_edge(measure_qr_1, x_gate, 'cr[1]')
dag.add_edge(cr_0_in, x_gate, 'cr[0]')
measure_qr_0 = dag.add_child(cx_gate, 'measure', 'qr[0]')
dag.add_edge(measure_qr_0, qr_0_out, 'qr[0]')
dag.add_edge(measure_qr_0, cr_0_out, 'cr[0]')
dag.add_edge(x_gate, measure_qr_0, 'cr[0]')
measure_qr_1_out = dag.add_child(x_gate, 'measure', 'cr[1]')
dag.add_edge(x_gate, measure_qr_1_out, 'qr[1]')
dag.add_edge(measure_qr_1_out, qr_1_out, 'qr[1]')
dag.add_edge(measure_qr_1_out, cr_1_out, 'cr[1]')
res = rustworkx.layers(dag, input_nodes, index_output=True)
expected = [[qr_0_in, qr_1_in, cr_0_in, cr_1_in], [h_gate], [cx_gate], [measure_qr_1], [x_gate], [measure_qr_1_out, measure_qr_0], [cr_1_out, qr_1_out, cr_0_out, qr_0_out]]
self.assertEqual(expected, res)
```

## Next Steps


---

*Source: test_layers.py:67 | Complexity: Advanced | Last updated: 2026-05-05*