# Test Example Extraction Report

**Total Examples**: 1510  
**High Value Examples** (confidence > 0.7): 1510  
**Average Complexity**: 0.52  

## Examples by Category

- **instantiation**: 362
- **method_call**: 542
- **workflow**: 606

## Examples by Language

- **Python**: 1510

## Extracted Examples

### test_isomorphic_identical

**Category**: workflow  
**Description**: Workflow: test isomorphic identical  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDAG()
dag_b = rustworkx.PyDAG()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'a_1')
dag_a.add_child(node_a, 'a_3', 'a_2')
node_b = dag_b.add_node('a_1')
dag_b.add_child(node_b, 'a_2', 'a_1')
dag_b.add_child(node_b, 'a_3', 'a_2')
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_isomorphic(dag_a, dag_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isomorphic.py:38*

### test_isomorphic_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test isomorphic mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDAG()
dag_b = rustworkx.PyDAG()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'a_1')
dag_a.add_child(node_a, 'a_3', 'a_2')
node_b = dag_b.add_node('b_1')
dag_b.add_child(node_b, 'b_2', 'b_1')
dag_b.add_child(node_b, 'b_3', 'b_2')
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_isomorphic(dag_a, dag_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isomorphic.py:53*

### test_isomorphic_compare_nodes_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test isomorphic compare nodes mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDAG()
dag_b = rustworkx.PyDAG()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'a_1')
dag_a.add_child(node_a, 'a_3', 'a_2')
node_b = dag_b.add_node('b_1')
dag_b.add_child(node_b, 'b_2', 'b_1')
dag_b.add_child(node_b, 'b_3', 'b_2')
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertFalse(rustworkx.is_isomorphic(dag_a, dag_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isomorphic.py:68*

### test_is_isomorphic_nodes_compare_raises

**Category**: workflow  
**Description**: Workflow: test is isomorphic nodes compare raises  
**Expected**: self.assertRaises(TypeError, rustworkx.is_isomorphic, (dag_a, dag_b, compare_nodes))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDAG()
dag_b = rustworkx.PyDAG()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'a_1')
dag_a.add_child(node_a, 'a_3', 'a_2')
node_b = dag_b.add_node('b_1')
dag_b.add_child(node_b, 'b_2', 'b_1')
dag_b.add_child(node_b, 'b_3', 'b_2')

def compare_nodes(a, b):
    raise TypeError('Failure')
self.assertRaises(TypeError, rustworkx.is_isomorphic, (dag_a, dag_b, compare_nodes))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isomorphic.py:85*

### test_isomorphic_compare_nodes_identical

**Category**: workflow  
**Description**: Workflow: test isomorphic compare nodes identical  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDAG()
dag_b = rustworkx.PyDAG()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'a_1')
dag_a.add_child(node_a, 'a_3', 'a_2')
node_b = dag_b.add_node('a_1')
dag_b.add_child(node_b, 'a_2', 'a_1')
dag_b.add_child(node_b, 'a_3', 'a_2')
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_isomorphic(dag_a, dag_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isomorphic.py:102*

### test_isomorphic_compare_edges_identical

**Category**: workflow  
**Description**: Workflow: test isomorphic compare edges identical  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDAG()
dag_b = rustworkx.PyDAG()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'a_1')
dag_a.add_child(node_a, 'a_3', 'a_2')
node_b = dag_b.add_node('a_1')
dag_b.add_child(node_b, 'a_2', 'a_1')
dag_b.add_child(node_b, 'a_3', 'a_2')
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_isomorphic(dag_a, dag_b, edge_matcher=lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isomorphic.py:119*

### test_digraph_vf2_number_of_valid_mappings

**Category**: workflow  
**Description**: Workflow: test digraph vf2 number of valid mappings  
**Expected**: self.assertEqual(total, 6)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_mesh_graph(3)
mapping = rustworkx.digraph_vf2_mapping(graph, graph, id_order=True)
total = 0
for _ in mapping:
    total += 1
self.assertEqual(total, 6)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isomorphic.py:336*

### test_isomorphic_identical

**Category**: workflow  
**Description**: Workflow: test isomorphic identical  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDAG()
dag_b = rustworkx.PyDAG()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'a_1')
dag_a.add_child(node_a, 'a_3', 'a_2')
node_b = dag_b.add_node('a_1')
dag_b.add_child(node_b, 'a_2', 'a_1')
dag_b.add_child(node_b, 'a_3', 'a_2')
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_isomorphic(dag_a, dag_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isomorphic.py:38*

### test_isomorphic_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test isomorphic mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDAG()
dag_b = rustworkx.PyDAG()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'a_1')
dag_a.add_child(node_a, 'a_3', 'a_2')
node_b = dag_b.add_node('b_1')
dag_b.add_child(node_b, 'b_2', 'b_1')
dag_b.add_child(node_b, 'b_3', 'b_2')
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_isomorphic(dag_a, dag_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isomorphic.py:53*

### test_isomorphic_compare_nodes_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test isomorphic compare nodes mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDAG()
dag_b = rustworkx.PyDAG()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'a_1')
dag_a.add_child(node_a, 'a_3', 'a_2')
node_b = dag_b.add_node('b_1')
dag_b.add_child(node_b, 'b_2', 'b_1')
dag_b.add_child(node_b, 'b_3', 'b_2')
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertFalse(rustworkx.is_isomorphic(dag_a, dag_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isomorphic.py:68*

### test_deepcopy_returns_graph

**Category**: workflow  
**Description**: Workflow: test deepcopy returns graph  
**Expected**: self.assertIsInstance(dag_b, rustworkx.PyGraph)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyGraph()
node_a = dag_a.add_node('a_1')
node_b = dag_a.add_node('a_2')
dag_a.add_edge(node_a, node_b, 'edge_1')
node_c = dag_a.add_node('a_3')
dag_a.add_edge(node_b, node_c, 'edge_2')
dag_b = copy.deepcopy(dag_a)
self.assertIsInstance(dag_b, rustworkx.PyGraph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_deepcopy.py:20*

### test_deepcopy_with_holes_returns_graph

**Category**: workflow  
**Description**: Workflow: test deepcopy with holes returns graph  
**Expected**: self.assertEqual([node_a, node_c], dag_b.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyGraph()
node_a = dag_a.add_node('a_1')
node_b = dag_a.add_node('a_2')
dag_a.add_edge(node_a, node_b, 'edge_1')
node_c = dag_a.add_node('a_3')
dag_a.add_edge(node_b, node_c, 'edge_2')
dag_a.remove_node(node_b)
dag_b = copy.deepcopy(dag_a)
self.assertIsInstance(dag_b, rustworkx.PyGraph)
self.assertEqual([node_a, node_c], dag_b.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_deepcopy.py:30*

### test_deepcopy_returns_graph

**Category**: workflow  
**Description**: Workflow: test deepcopy returns graph  
**Expected**: self.assertIsInstance(dag_b, rustworkx.PyGraph)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyGraph()
node_a = dag_a.add_node('a_1')
node_b = dag_a.add_node('a_2')
dag_a.add_edge(node_a, node_b, 'edge_1')
node_c = dag_a.add_node('a_3')
dag_a.add_edge(node_b, node_c, 'edge_2')
dag_b = copy.deepcopy(dag_a)
self.assertIsInstance(dag_b, rustworkx.PyGraph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_deepcopy.py:20*

### test_deepcopy_with_holes_returns_graph

**Category**: workflow  
**Description**: Workflow: test deepcopy with holes returns graph  
**Expected**: self.assertEqual([node_a, node_c], dag_b.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyGraph()
node_a = dag_a.add_node('a_1')
node_b = dag_a.add_node('a_2')
dag_a.add_edge(node_a, node_b, 'edge_1')
node_c = dag_a.add_node('a_3')
dag_a.add_edge(node_b, node_c, 'edge_2')
dag_a.remove_node(node_b)
dag_b = copy.deepcopy(dag_a)
self.assertIsInstance(dag_b, rustworkx.PyGraph)
self.assertEqual([node_a, node_c], dag_b.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_deepcopy.py:30*

### test_hits

**Category**: workflow  
**Description**: Workflow: test hits  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
edges = [(0, 2), (0, 4), (1, 0), (2, 4), (4, 3), (4, 2), (5, 4)]
rx_graph = rustworkx.PyDiGraph()
rx_graph.extend_from_edge_list(edges)
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(edges)
rx_h, rx_a = rustworkx.hits(rx_graph)
nx_h, nx_a = hits_python(nx_graph)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_h[v], nx_h[v], delta=0.0001)
    self.assertAlmostEqual(rx_a[v], nx_a[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_hits.py:108*

### test_multi_digraph_versus_weighted

**Category**: workflow  
**Description**: Workflow: test multi digraph versus weighted  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
multi_graph = rustworkx.PyDiGraph()
multi_graph.extend_from_edge_list([(0, 1), (1, 0), (0, 1), (1, 0), (0, 1), (1, 0), (1, 2), (2, 1), (1, 2), (2, 1), (2, 3), (3, 2), (2, 3), (3, 2)])
weighted_graph = rustworkx.PyDiGraph()
weighted_graph.extend_from_weighted_edge_list([(0, 1, 3), (1, 0, 3), (1, 2, 2), (2, 1, 2), (2, 3, 2), (3, 2, 2)])
h_multi, a_multi = rustworkx.hits(multi_graph, weight_fn=lambda _: 1.0)
h_weight, a_weight = rustworkx.hits(weighted_graph, weight_fn=float)
for v in multi_graph.node_indices():
    self.assertAlmostEqual(h_multi[v], h_weight[v], delta=0.0001)
    self.assertAlmostEqual(a_multi[v], a_weight[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_hits.py:135*

### test_hits

**Category**: workflow  
**Description**: Workflow: test hits  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
edges = [(0, 2), (0, 4), (1, 0), (2, 4), (4, 3), (4, 2), (5, 4)]
rx_graph = rustworkx.PyDiGraph()
rx_graph.extend_from_edge_list(edges)
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(edges)
rx_h, rx_a = rustworkx.hits(rx_graph)
nx_h, nx_a = hits_python(nx_graph)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_h[v], nx_h[v], delta=0.0001)
    self.assertAlmostEqual(rx_a[v], nx_a[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_hits.py:108*

### test_multi_digraph_versus_weighted

**Category**: workflow  
**Description**: Workflow: test multi digraph versus weighted  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
multi_graph = rustworkx.PyDiGraph()
multi_graph.extend_from_edge_list([(0, 1), (1, 0), (0, 1), (1, 0), (0, 1), (1, 0), (1, 2), (2, 1), (1, 2), (2, 1), (2, 3), (3, 2), (2, 3), (3, 2)])
weighted_graph = rustworkx.PyDiGraph()
weighted_graph.extend_from_weighted_edge_list([(0, 1, 3), (1, 0, 3), (1, 2, 2), (2, 1, 2), (2, 3, 2), (3, 2, 2)])
h_multi, a_multi = rustworkx.hits(multi_graph, weight_fn=lambda _: 1.0)
h_weight, a_weight = rustworkx.hits(weighted_graph, weight_fn=float)
for v in multi_graph.node_indices():
    self.assertAlmostEqual(h_multi[v], h_weight[v], delta=0.0001)
    self.assertAlmostEqual(a_multi[v], a_weight[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_hits.py:135*

### test_digraph_dfs_tree_edges_restricted

**Category**: workflow  
**Description**: Workflow: test digraph dfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (2, 1), (1, 3)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

class TreeEdgesRecorderRestricted(rustworkx.visit.DFSVisitor):
    prohibited = [(0, 1), (5, 3)]

    def __init__(self):
        self.edges = []

    def tree_edge(self, edge):
        edge = (edge[0], edge[1])
        if edge in self.prohibited:
            raise rustworkx.visit.PruneSearch
        self.edges.append(edge)
vis = TreeEdgesRecorderRestricted()
rustworkx.digraph_dfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (2, 1), (1, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_search.py:58*

### test_digraph_dfs_tree_edges_restricted

**Category**: workflow  
**Description**: Workflow: test digraph dfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (2, 1), (1, 3)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
class TreeEdgesRecorderRestricted(rustworkx.visit.DFSVisitor):
    prohibited = [(0, 1), (5, 3)]

    def __init__(self):
        self.edges = []

    def tree_edge(self, edge):
        edge = (edge[0], edge[1])
        if edge in self.prohibited:
            raise rustworkx.visit.PruneSearch
        self.edges.append(edge)
vis = TreeEdgesRecorderRestricted()
rustworkx.digraph_dfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (2, 1), (1, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_search.py:58*

### test_dagcircuit_basic

**Category**: workflow  
**Description**: Workflow: test dagcircuit basic  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
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
res = rustworkx.layers(dag, input_nodes)
expected = [['qr[0]', 'qr[1]', 'cr[0]', 'cr[1]'], ['h'], ['cx'], ['measure'], ['x'], ['measure', 'measure'], ['cr[1]', 'qr[1]', 'cr[0]', 'qr[0]']]
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layers.py:19*

### test_dagcircuit_basic_index_output

**Category**: workflow  
**Description**: Workflow: test dagcircuit basic index output  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layers.py:67*

### test_dagcircuit_basic

**Category**: workflow  
**Description**: Workflow: test dagcircuit basic  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
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
res = rustworkx.layers(dag, input_nodes)
expected = [['qr[0]', 'qr[1]', 'cr[0]', 'cr[1]'], ['h'], ['cx'], ['measure'], ['x'], ['measure', 'measure'], ['cr[1]', 'qr[1]', 'cr[0]', 'qr[0]']]
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layers.py:19*

### test_dagcircuit_basic_index_output

**Category**: workflow  
**Description**: Workflow: test dagcircuit basic index output  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layers.py:67*

### test_single_source_all_shortest_paths_zero_weight

**Category**: workflow  
**Description**: Workflow: test single source all shortest paths zero weight  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.cycle = rustworkx.PyGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.grid = rustworkx.generators.grid_graph(4, 4)
for edge in self.grid.edge_list():
    self.grid.update_edge(edge[0], edge[1], 1.0)
self.disconnected = rustworkx.PyGraph()
self.disconnected_nodes = self.disconnected.add_nodes_from([0, 1, 2, 3, 4])
self.disconnected.add_edges_from([(self.disconnected_nodes[0], self.disconnected_nodes[1], 1), (self.disconnected_nodes[1], self.disconnected_nodes[2], 1), (self.disconnected_nodes[2], self.disconnected_nodes[3], 1), (self.disconnected_nodes[3], self.disconnected_nodes[0], 1)])

graph = rustworkx.PyGraph()
nodes = graph.add_nodes_from([0, 1, 2, 3])
graph.add_edge(nodes[0], nodes[1], 0.0)
graph.add_edge(nodes[1], nodes[2], 0.0)
graph.add_edge(nodes[2], nodes[0], 0.0)
graph.add_edge(nodes[2], nodes[3], 1.0)
source = nodes[0]
shortest_lengths = rustworkx.dijkstra_shortest_path_lengths(graph, source, lambda x: x)

def path_weight(path):
    total = 0.0
    for i in range(len(path) - 1):
        edge_data = graph.get_edge_data(path[i], path[i + 1])
        total += edge_data
    return total
expected = {source: [[source]]}
for target in graph.nodes():
    if target != source:
        paths = rustworkx.all_simple_paths(graph, source, target)
        expected_paths = [path for path in paths if path_weight(path) == shortest_lengths[target]]
        expected[target] = expected_paths
paths = rustworkx.graph_single_source_all_shortest_paths(graph, source)
for node in expected:
    self.assertEqual(sorted(paths[node]), sorted(expected[node]))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_single_source_all_shortest_paths.py:100*

### test_single_source_all_shortest_paths_zero_weight

**Category**: workflow  
**Description**: Workflow: test single source all shortest paths zero weight  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
nodes = graph.add_nodes_from([0, 1, 2, 3])
graph.add_edge(nodes[0], nodes[1], 0.0)
graph.add_edge(nodes[1], nodes[2], 0.0)
graph.add_edge(nodes[2], nodes[0], 0.0)
graph.add_edge(nodes[2], nodes[3], 1.0)
source = nodes[0]
shortest_lengths = rustworkx.dijkstra_shortest_path_lengths(graph, source, lambda x: x)

def path_weight(path):
    total = 0.0
    for i in range(len(path) - 1):
        edge_data = graph.get_edge_data(path[i], path[i + 1])
        total += edge_data
    return total
expected = {source: [[source]]}
for target in graph.nodes():
    if target != source:
        paths = rustworkx.all_simple_paths(graph, source, target)
        expected_paths = [path for path in paths if path_weight(path) == shortest_lengths[target]]
        expected[target] = expected_paths
paths = rustworkx.graph_single_source_all_shortest_paths(graph, source)
for node in expected:
    self.assertEqual(sorted(paths[node]), sorted(expected[node]))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_single_source_all_shortest_paths.py:100*

### test_remove_nodes_from

**Category**: workflow  
**Description**: Workflow: test remove nodes from  
**Expected**: self.assertEqual([0], graph.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'Edgy_mk2')
graph.remove_nodes_from([node_b, node_c])
res = graph.nodes()
self.assertEqual(['a'], res)
self.assertEqual([0], graph.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_nodes.py:59*

### test_remove_nodes_from_gen

**Category**: workflow  
**Description**: Workflow: test remove nodes from gen  
**Expected**: self.assertEqual([0], graph.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'Edgy_mk2')
graph.remove_nodes_from((n for n in [node_b, node_c]))
res = graph.nodes()
self.assertEqual(['a'], res)
self.assertEqual([0], graph.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_nodes.py:71*

### test_remove_nodes_from_with_invalid_index

**Category**: workflow  
**Description**: Workflow: test remove nodes from with invalid index  
**Expected**: self.assertEqual([0], graph.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'Edgy_mk2')
graph.remove_nodes_from([node_b, node_c, 76])
res = graph.nodes()
self.assertEqual(['a'], res)
self.assertEqual([0], graph.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_nodes.py:83*

### test_add_nodes_from_gen

**Category**: workflow  
**Description**: Workflow: test add nodes from gen  
**Expected**: self.assertEqual(res, nodes)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
nodes = list(range(100))
node_gen = (i ** 2 for i in nodes)
res = graph.add_nodes_from(node_gen)
self.assertEqual(len(res), 100)
self.assertEqual(res, nodes)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_nodes.py:136*

### test_set_node_data_setitem

**Category**: workflow  
**Description**: Workflow: test set node data setitem  
**Expected**: self.assertEqual('Oh so cool', graph[node_b])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
graph[node_b] = 'Oh so cool'
self.assertEqual('Oh so cool', graph[node_b])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_nodes.py:164*

### test_set_node_data_setitem_bad_index

**Category**: workflow  
**Description**: Workflow: test set node data setitem bad index  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
with self.assertRaises(IndexError):
    graph[42] = 'Oh so cool'
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_nodes.py:172*

### test_remove_node_delitem

**Category**: workflow  
**Description**: Workflow: test remove node delitem  
**Expected**: self.assertEqual([0, 2], graph.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'Edgy_mk2')
del graph[node_b]
res = graph.nodes()
self.assertEqual(['a', 'c'], res)
self.assertEqual([0, 2], graph.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_nodes.py:180*

### test_remove_nodes_from

**Category**: workflow  
**Description**: Workflow: test remove nodes from  
**Expected**: self.assertEqual([0], graph.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'Edgy_mk2')
graph.remove_nodes_from([node_b, node_c])
res = graph.nodes()
self.assertEqual(['a'], res)
self.assertEqual([0], graph.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_nodes.py:59*

### test_remove_nodes_from_gen

**Category**: workflow  
**Description**: Workflow: test remove nodes from gen  
**Expected**: self.assertEqual([0], graph.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'Edgy_mk2')
graph.remove_nodes_from((n for n in [node_b, node_c]))
res = graph.nodes()
self.assertEqual(['a'], res)
self.assertEqual([0], graph.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_nodes.py:71*

### test_remove_nodes_from_with_invalid_index

**Category**: workflow  
**Description**: Workflow: test remove nodes from with invalid index  
**Expected**: self.assertEqual([0], graph.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'Edgy_mk2')
graph.remove_nodes_from([node_b, node_c, 76])
res = graph.nodes()
self.assertEqual(['a'], res)
self.assertEqual([0], graph.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_nodes.py:83*

### test_draw_edges_min_source_target_margins

**Category**: workflow  
**Description**: Workflow: Test that there is a wider gap between the node and the start of an
incident edge when min_source_margin is specified.

This test checks that the use of min_{source/target}_margin kwargs
result in shorter (more padding) between the edges and source and
target nodes. As a crude visual example, let 's' and 't' represent
source and target nodes, respectively:
   Default:
   s-----------------------------t
   With margins:
   s   -----------------------   t  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
"Test that there is a wider gap between the node and the start of an\n        incident edge when min_source_margin is specified.\n\n        This test checks that the use of min_{source/target}_margin kwargs\n        result in shorter (more padding) between the edges and source and\n        target nodes. As a crude visual example, let 's' and 't' represent\n        source and target nodes, respectively:\n           Default:\n           s-----------------------------t\n           With margins:\n           s   -----------------------   t\n        "
node_shapes = ['o', 's']
graph = rustworkx.PyGraph()
graph.extend_from_edge_list([(0, 1)])
pos = {0: (0, 0), 1: (1, 0)}
for node_shape in node_shapes:
    with self.subTest(shape=node_shape):
        fig, ax = plt.subplots()
        mpl_draw(graph, pos=pos, ax=ax, node_shape=node_shape, min_source_margin=100, min_target_margin=100)
        _save_images(fig, f'test_node_shape_{node_shape}.png')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_mpl.py:96*

### test_alpha_iter

**Category**: workflow  
**Description**: Workflow: test alpha iter  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.grid_graph(4, 6)
plt.subplot(131)
mpl_draw(graph, alpha=[0.1, 0.2])
num_nodes = len(graph)
alpha = [x / num_nodes for x in range(num_nodes)]
colors = range(num_nodes)
plt.subplot(132)
mpl_draw(graph, node_color=colors, alpha=alpha)
alpha.append(1)
plt.subplot(133)
mpl_draw(graph, alpha=alpha)
fig = plt.gcf()
_save_images(fig, 'test_alpha_iter.png')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_mpl.py:127*

### test_labels_and_colors

**Category**: workflow  
**Description**: Workflow: test labels and colors  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
graph.add_nodes_from(list(range(8)))
edge_list = [(0, 1, 5), (1, 2, 2), (2, 3, 7), (3, 0, 6), (5, 6, 1), (4, 5, 7), (6, 7, 3), (7, 4, 7)]
labels = {}
labels[0] = '$a$'
labels[1] = '$b$'
labels[2] = '$c$'
labels[3] = '$d$'
labels[4] = '$\\alpha$'
labels[5] = '$\\beta$'
labels[6] = '$\\gamma$'
labels[7] = '$\\delta$'
graph.add_edges_from(edge_list)
pos = rustworkx.random_layout(graph)
mpl_draw(graph, pos=pos, node_list=[0, 1, 2, 3], node_color='r', edge_list=[(0, 1), (1, 2), (2, 3), (3, 0)], node_size=500, alpha=0.75, width=1.0, labels=lambda x: labels[x], font_size=16)
mpl_draw(graph, pos=pos, node_list=[4, 5, 6, 7], node_color='b', node_size=500, alpha=0.5, edge_list=[(4, 5), (5, 6), (6, 7), (7, 4)], width=8, edge_color='r', rotate=False, edge_labels=lambda edge: labels[edge])
fig = plt.gcf()
_save_images(fig, 'test_labels_and_colors.png')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_mpl.py:145*

### test_draw_edges_min_source_target_margins

**Category**: workflow  
**Description**: Workflow: Test that there is a wider gap between the node and the start of an
incident edge when min_source_margin is specified.

This test checks that the use of min_{source/target}_margin kwargs
result in shorter (more padding) between the edges and source and
target nodes. As a crude visual example, let 's' and 't' represent
source and target nodes, respectively:
   Default:
   s-----------------------------t
   With margins:
   s   -----------------------   t  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
"Test that there is a wider gap between the node and the start of an\n        incident edge when min_source_margin is specified.\n\n        This test checks that the use of min_{source/target}_margin kwargs\n        result in shorter (more padding) between the edges and source and\n        target nodes. As a crude visual example, let 's' and 't' represent\n        source and target nodes, respectively:\n           Default:\n           s-----------------------------t\n           With margins:\n           s   -----------------------   t\n        "
node_shapes = ['o', 's']
graph = rustworkx.PyGraph()
graph.extend_from_edge_list([(0, 1)])
pos = {0: (0, 0), 1: (1, 0)}
for node_shape in node_shapes:
    with self.subTest(shape=node_shape):
        fig, ax = plt.subplots()
        mpl_draw(graph, pos=pos, ax=ax, node_shape=node_shape, min_source_margin=100, min_target_margin=100)
        _save_images(fig, f'test_node_shape_{node_shape}.png')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_mpl.py:96*

### test_alpha_iter

**Category**: workflow  
**Description**: Workflow: test alpha iter  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.grid_graph(4, 6)
plt.subplot(131)
mpl_draw(graph, alpha=[0.1, 0.2])
num_nodes = len(graph)
alpha = [x / num_nodes for x in range(num_nodes)]
colors = range(num_nodes)
plt.subplot(132)
mpl_draw(graph, node_color=colors, alpha=alpha)
alpha.append(1)
plt.subplot(133)
mpl_draw(graph, alpha=alpha)
fig = plt.gcf()
_save_images(fig, 'test_alpha_iter.png')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_mpl.py:127*

### test_labels_and_colors

**Category**: workflow  
**Description**: Workflow: test labels and colors  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
graph.add_nodes_from(list(range(8)))
edge_list = [(0, 1, 5), (1, 2, 2), (2, 3, 7), (3, 0, 6), (5, 6, 1), (4, 5, 7), (6, 7, 3), (7, 4, 7)]
labels = {}
labels[0] = '$a$'
labels[1] = '$b$'
labels[2] = '$c$'
labels[3] = '$d$'
labels[4] = '$\\alpha$'
labels[5] = '$\\beta$'
labels[6] = '$\\gamma$'
labels[7] = '$\\delta$'
graph.add_edges_from(edge_list)
pos = rustworkx.random_layout(graph)
mpl_draw(graph, pos=pos, node_list=[0, 1, 2, 3], node_color='r', edge_list=[(0, 1), (1, 2), (2, 3), (3, 0)], node_size=500, alpha=0.75, width=1.0, labels=lambda x: labels[x], font_size=16)
mpl_draw(graph, pos=pos, node_list=[4, 5, 6, 7], node_color='b', node_size=500, alpha=0.5, edge_list=[(4, 5), (5, 6), (6, 7), (7, 4)], width=8, edge_color='r', rotate=False, edge_labels=lambda edge: labels[edge])
fig = plt.gcf()
_save_images(fig, 'test_labels_and_colors.png')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_mpl.py:145*

### test_another_trivial_graph

**Category**: workflow  
**Description**: Workflow: test another trivial graph  
**Expected**: self.assertEqual(sorted_edges(rustworkx.bridges(graph)), {(0, 1), (1, 2)})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
super().setUp()
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 2), (0, 3), (1, 4), (4, 9), (5, 7), (0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 8), (5, 6), (6, 7), (8, 9)])
self.barbell_graph = rustworkx.PyGraph()
self.barbell_graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])

graph = rustworkx.PyGraph()
a = graph.add_node(0)
b = graph.add_node(1)
c = graph.add_node(2)
graph.add_edge(a, b, None)
graph.add_edge(b, c, None)
self.assertEqual(rustworkx.articulation_points(graph), {1})
self.assertEqual(sorted_edges(rustworkx.bridges(graph)), {(0, 1), (1, 2)})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_biconnected.py:74*

### test_another_trivial_graph

**Category**: workflow  
**Description**: Workflow: test another trivial graph  
**Expected**: self.assertEqual(sorted_edges(rustworkx.bridges(graph)), {(0, 1), (1, 2)})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
a = graph.add_node(0)
b = graph.add_node(1)
c = graph.add_node(2)
graph.add_edge(a, b, None)
graph.add_edge(b, c, None)
self.assertEqual(rustworkx.articulation_points(graph), {1})
self.assertEqual(sorted_edges(rustworkx.bridges(graph)), {(0, 1), (1, 2)})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_biconnected.py:74*

### test_astar_null_heuristic

**Category**: workflow  
**Description**: Workflow: test astar null heuristic  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
c = g.add_node('C')
d = g.add_node('D')
e = g.add_node('E')
f = g.add_node('F')
g.add_edge(a, b, 7)
g.add_edge(c, a, 9)
g.add_edge(a, d, 14)
g.add_edge(b, c, 10)
g.add_edge(d, c, 2)
g.add_edge(d, e, 9)
g.add_edge(b, f, 15)
g.add_edge(c, f, 11)
g.add_edge(e, f, 6)
path = rustworkx.graph_astar_shortest_path(g, a, lambda goal: goal == 'E', lambda x: float(x), lambda y: 0)
expected = [a, c, d, e]
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_astar.py:19*

### test_astar_manhattan_heuristic

**Category**: workflow  
**Description**: Workflow: test astar manhattan heuristic  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node((0.0, 0.0))
b = g.add_node((2.0, 0.0))
c = g.add_node((1.0, 1.0))
d = g.add_node((0.0, 2.0))
e = g.add_node((3.0, 3.0))
f = g.add_node((4.0, 2.0))
no_path = g.add_node((5.0, 5.0))
g.add_edge(a, b, 2.0)
g.add_edge(a, d, 4.0)
g.add_edge(b, c, 1.0)
g.add_edge(b, f, 7.0)
g.add_edge(c, e, 5.0)
g.add_edge(e, f, 1.0)
g.add_edge(d, e, 1.0)

def heuristic_func(f):
    x1, x2 = f
    return abs(x2 - x1)

def finish_func(node, x):
    return x == g.get_node_data(node)
expected = [[0], [0, 1], [0, 1, 2], [0, 3], [0, 3, 4], [0, 3, 4, 5]]
for index, end in enumerate([a, b, c, d, e, f]):
    path = rustworkx.graph_astar_shortest_path(g, a, lambda finish: finish_func(end, finish), lambda x: float(x), heuristic_func)
    self.assertEqual(expected[index], path)
with self.assertRaises(rustworkx.NoPathFound):
    rustworkx.graph_astar_shortest_path(g, a, lambda finish: finish_func(no_path, finish), lambda x: float(x), heuristic_func)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_astar.py:42*

### test_astar_null_heuristic

**Category**: workflow  
**Description**: Workflow: test astar null heuristic  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
c = g.add_node('C')
d = g.add_node('D')
e = g.add_node('E')
f = g.add_node('F')
g.add_edge(a, b, 7)
g.add_edge(c, a, 9)
g.add_edge(a, d, 14)
g.add_edge(b, c, 10)
g.add_edge(d, c, 2)
g.add_edge(d, e, 9)
g.add_edge(b, f, 15)
g.add_edge(c, f, 11)
g.add_edge(e, f, 6)
path = rustworkx.graph_astar_shortest_path(g, a, lambda goal: goal == 'E', lambda x: float(x), lambda y: 0)
expected = [a, c, d, e]
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_astar.py:19*

### test_astar_manhattan_heuristic

**Category**: workflow  
**Description**: Workflow: test astar manhattan heuristic  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node((0.0, 0.0))
b = g.add_node((2.0, 0.0))
c = g.add_node((1.0, 1.0))
d = g.add_node((0.0, 2.0))
e = g.add_node((3.0, 3.0))
f = g.add_node((4.0, 2.0))
no_path = g.add_node((5.0, 5.0))
g.add_edge(a, b, 2.0)
g.add_edge(a, d, 4.0)
g.add_edge(b, c, 1.0)
g.add_edge(b, f, 7.0)
g.add_edge(c, e, 5.0)
g.add_edge(e, f, 1.0)
g.add_edge(d, e, 1.0)

def heuristic_func(f):
    x1, x2 = f
    return abs(x2 - x1)

def finish_func(node, x):
    return x == g.get_node_data(node)
expected = [[0], [0, 1], [0, 1, 2], [0, 3], [0, 3, 4], [0, 3, 4, 5]]
for index, end in enumerate([a, b, c, d, e, f]):
    path = rustworkx.graph_astar_shortest_path(g, a, lambda finish: finish_func(end, finish), lambda x: float(x), heuristic_func)
    self.assertEqual(expected[index], path)
with self.assertRaises(rustworkx.NoPathFound):
    rustworkx.graph_astar_shortest_path(g, a, lambda finish: finish_func(no_path, finish), lambda x: float(x), heuristic_func)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_astar.py:42*

### test_write_edge_list_round_trip

**Category**: workflow  
**Description**: Workflow: test write edge list round trip  
**Expected**: self.assertEqual(expected, new_graph.weighted_edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
path = os.path.join(tempfile.gettempdir(), 'round_trip.txt')
graph = rustworkx.generators.star_graph(5)
count = iter(range(5))

def weight_fn(edge):
    return str(next(count))
graph.write_edge_list(path, weight_fn=weight_fn)
self.addCleanup(os.remove, path)
new_graph = rustworkx.PyGraph.read_edge_list(path)
expected = [(0, 1, '0'), (0, 2, '1'), (0, 3, '2'), (0, 4, '3')]
self.assertEqual(expected, new_graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edgelist.py:185*

### test_write_edge_list_round_trip

**Category**: workflow  
**Description**: Workflow: test write edge list round trip  
**Expected**: self.assertEqual(expected, new_graph.weighted_edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
path = os.path.join(tempfile.gettempdir(), 'round_trip.txt')
graph = rustworkx.generators.star_graph(5)
count = iter(range(5))

def weight_fn(edge):
    return str(next(count))
graph.write_edge_list(path, weight_fn=weight_fn)
self.addCleanup(os.remove, path)
new_graph = rustworkx.PyGraph.read_edge_list(path)
expected = [(0, 1, '0'), (0, 2, '1'), (0, 3, '2'), (0, 4, '3')]
self.assertEqual(expected, new_graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edgelist.py:185*

### test_gnp_random_against_networkx_max_cardinality

**Category**: workflow  
**Description**: Workflow: test gnp random against networkx max cardinality  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.undirected_gnp_random_graph(10, 0.78, seed=428)
nx_graph = networkx.Graph(list(rx_graph.edge_list()))
nx_matches = networkx.max_weight_matching(nx_graph, maxcardinality=True)
rx_matches = rustworkx.max_weight_matching(rx_graph, max_cardinality=True, verify_optimum=True)
self.compare_rx_nx_sets(rx_graph, rx_matches, nx_matches, 428, nx_graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_max_weight_matching.py:539*

### test_gnm_random_against_networkx

**Category**: workflow  
**Description**: Workflow: test gnm random against networkx  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.undirected_gnm_random_graph(10, 13, seed=42)
nx_graph = networkx.Graph(list(rx_graph.edge_list()))
nx_matches = networkx.max_weight_matching(nx_graph)
rx_matches = rustworkx.max_weight_matching(rx_graph, verify_optimum=True)
self.compare_rx_nx_sets(rx_graph, rx_matches, nx_matches, 42, nx_graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_max_weight_matching.py:586*

### test_gnm_random_against_networkx_max_cardinality

**Category**: workflow  
**Description**: Workflow: test gnm random against networkx max cardinality  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.undirected_gnm_random_graph(10, 12, seed=42)
nx_graph = networkx.Graph(list(rx_graph.edge_list()))
nx_matches = networkx.max_weight_matching(nx_graph, maxcardinality=True)
rx_matches = rustworkx.max_weight_matching(rx_graph, max_cardinality=True, verify_optimum=True)
self.compare_rx_nx_sets(rx_graph, rx_matches, nx_matches, 42, nx_graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_max_weight_matching.py:593*

### test_gnp_random_against_networkx_max_cardinality

**Category**: workflow  
**Description**: Workflow: test gnp random against networkx max cardinality  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.undirected_gnp_random_graph(10, 0.78, seed=428)
nx_graph = networkx.Graph(list(rx_graph.edge_list()))
nx_matches = networkx.max_weight_matching(nx_graph, maxcardinality=True)
rx_matches = rustworkx.max_weight_matching(rx_graph, max_cardinality=True, verify_optimum=True)
self.compare_rx_nx_sets(rx_graph, rx_matches, nx_matches, 428, nx_graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_max_weight_matching.py:539*

### test_gnm_random_against_networkx

**Category**: workflow  
**Description**: Workflow: test gnm random against networkx  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.undirected_gnm_random_graph(10, 13, seed=42)
nx_graph = networkx.Graph(list(rx_graph.edge_list()))
nx_matches = networkx.max_weight_matching(nx_graph)
rx_matches = rustworkx.max_weight_matching(rx_graph, verify_optimum=True)
self.compare_rx_nx_sets(rx_graph, rx_matches, nx_matches, 42, nx_graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_max_weight_matching.py:586*

### test_gnm_random_against_networkx_max_cardinality

**Category**: workflow  
**Description**: Workflow: test gnm random against networkx max cardinality  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.undirected_gnm_random_graph(10, 12, seed=42)
nx_graph = networkx.Graph(list(rx_graph.edge_list()))
nx_matches = networkx.max_weight_matching(nx_graph, maxcardinality=True)
rx_matches = rustworkx.max_weight_matching(rx_graph, max_cardinality=True, verify_optimum=True)
self.compare_rx_nx_sets(rx_graph, rx_matches, nx_matches, 42, nx_graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_max_weight_matching.py:593*

### test_subgraph_isomorphic_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyDiGraph()
g_b = rustworkx.PyDiGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['b_1', 'b_2', 'b_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'b_1'), (nodes[1], nodes[2], 'b_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_subgraph_isomorphic(g_a, g_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph_isomorphic.py:51*

### test_subgraph_isomorphic_compare_nodes_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic compare nodes mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyDiGraph()
g_b = rustworkx.PyDiGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['b_1', 'b_2', 'b_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'b_1'), (nodes[1], nodes[2], 'b_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertFalse(rustworkx.is_subgraph_isomorphic(g_a, g_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph_isomorphic.py:70*

### test_subgraph_isomorphic_compare_nodes_identical

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic compare nodes identical  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyDiGraph()
g_b = rustworkx.PyDiGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_subgraph_isomorphic(g_a, g_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph_isomorphic.py:93*

### test_subgraph_isomorphic_compare_edges_identical

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic compare edges identical  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyDiGraph()
g_b = rustworkx.PyDiGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_subgraph_isomorphic(g_a, g_b, edge_matcher=lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph_isomorphic.py:130*

### test_subgraph_isomorphic_node_count_not_ge

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic node count not ge  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyDiGraph()
g_b = rustworkx.PyDiGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1')])
nodes = g_b.add_nodes_from(['a_0', 'a_1', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertFalse(rustworkx.is_subgraph_isomorphic(g_a, g_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph_isomorphic.py:156*

### test_non_induced_subgraph_isomorphic

**Category**: workflow  
**Description**: Workflow: test non induced subgraph isomorphic  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyDiGraph()
g_b = rustworkx.PyDiGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[2], nodes[0], 'a_3')])
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order, induced=True):
        self.assertFalse(rustworkx.is_subgraph_isomorphic(g_a, g_b, id_order=id_order, induced=True))
    with self.subTest(id_order=id_order, induced=False):
        self.assertTrue(rustworkx.is_subgraph_isomorphic(g_a, g_b, id_order=id_order, induced=False))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph_isomorphic.py:193*

### test_vf2pp_remapping

**Category**: workflow  
**Description**: Workflow: test vf2pp remapping  
**Expected**: self.assertEqual(next(mapping), {5: 0, 6: 1, 8: 2, 9: 3})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
temp = rustworkx.generators.directed_grid_graph(3, 3)
graph = rustworkx.PyDiGraph()
dummy = graph.add_node(0)
graph.compose(temp, dict())
graph.remove_node(dummy)
second_graph = rustworkx.generators.directed_grid_graph(2, 2)
mapping = rustworkx.digraph_vf2_mapping(graph, second_graph, subgraph=True, id_order=False)
self.assertEqual(next(mapping), {5: 0, 6: 1, 8: 2, 9: 3})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph_isomorphic.py:247*

### test_subgraph_isomorphic_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyDiGraph()
g_b = rustworkx.PyDiGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['b_1', 'b_2', 'b_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'b_1'), (nodes[1], nodes[2], 'b_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_subgraph_isomorphic(g_a, g_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph_isomorphic.py:51*

### test_subgraph_isomorphic_compare_nodes_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic compare nodes mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyDiGraph()
g_b = rustworkx.PyDiGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['b_1', 'b_2', 'b_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'b_1'), (nodes[1], nodes[2], 'b_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertFalse(rustworkx.is_subgraph_isomorphic(g_a, g_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph_isomorphic.py:70*

### test_subgraph_isomorphic_compare_nodes_identical

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic compare nodes identical  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyDiGraph()
g_b = rustworkx.PyDiGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_subgraph_isomorphic(g_a, g_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph_isomorphic.py:93*

### test_multiple_successor_edges

**Category**: workflow  
**Description**: Workflow: test multiple successor edges  
**Expected**: self.assertEqual([['cx', 'cx', 'cx']], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDiGraph()
q0, q1 = dag.add_nodes_from(['q0', 'q1'])
cx_1 = dag.add_child(q0, 'cx', 'q0')
dag.add_edge(q1, cx_1, 'q1')
cx_2 = dag.add_child(cx_1, 'cx', 'q0')
dag.add_edge(q1, cx_2, 'q1')
cx_3 = dag.add_child(cx_2, 'cx', 'q0')
dag.add_edge(q1, cx_3, 'q1')

def filter_function(node):
    return node == 'cx'
res = rustworkx.collect_runs(dag, filter_function)
self.assertEqual([['cx', 'cx', 'cx']], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_runs.py:58*

### test_h_h_cx

**Category**: workflow  
**Description**: Workflow: test h h cx  
**Expected**: self.assertEqual([['h', 'cx'], ['h']], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDiGraph()
q0, q1 = dag.add_nodes_from(['q0', 'q1'])
h_1 = dag.add_child(q0, 'h', 'q0')
h_2 = dag.add_child(q1, 'h', 'q1')
cx_2 = dag.add_child(h_1, 'cx', 'q0')
dag.add_edge(h_2, cx_2, 'q1')

def filter_function(node):
    return node in ['cx', 'h']
res = rustworkx.collect_runs(dag, filter_function)
self.assertEqual([['h', 'cx'], ['h']], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_runs.py:95*

### test_cx_h_h_cx

**Category**: workflow  
**Description**: Workflow: test cx h h cx  
**Expected**: self.assertEqual([['cx'], ['h', 'cx'], ['h']], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDiGraph()
q0, q1 = dag.add_nodes_from(['q0', 'q1'])
cx_1 = dag.add_child(q0, 'cx', 'q0')
dag.add_edge(q1, cx_1, 'q1')
h_1 = dag.add_child(cx_1, 'h', 'q0')
h_2 = dag.add_child(cx_1, 'h', 'q1')
cx_2 = dag.add_child(h_1, 'cx', 'q0')
dag.add_edge(h_2, cx_2, 'q1')

def filter_function(node):
    return node in ['cx', 'h']
res = rustworkx.collect_runs(dag, filter_function)
self.assertEqual([['cx'], ['h', 'cx'], ['h']], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_runs.py:109*

### test_cx_h_cx

**Category**: workflow  
**Description**: Workflow: test cx h cx  
**Expected**: self.assertEqual([['cx'], ['h', 'cx']], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDiGraph()
q0, q1 = dag.add_nodes_from(['q0', 'q1'])
cx_1 = dag.add_child(q0, 'cx', 'q0')
dag.add_edge(q1, cx_1, 'q1')
h_1 = dag.add_child(cx_1, 'h', 'q0')
cx_2 = dag.add_child(h_1, 'cx', 'q0')
dag.add_edge(cx_1, cx_2, 'q1')

def filter_function(node):
    return node in ['cx', 'h']
res = rustworkx.collect_runs(dag, filter_function)
self.assertEqual([['cx'], ['h', 'cx']], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_runs.py:125*

### test_multiple_successor_edges

**Category**: workflow  
**Description**: Workflow: test multiple successor edges  
**Expected**: self.assertEqual([['cx', 'cx', 'cx']], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDiGraph()
q0, q1 = dag.add_nodes_from(['q0', 'q1'])
cx_1 = dag.add_child(q0, 'cx', 'q0')
dag.add_edge(q1, cx_1, 'q1')
cx_2 = dag.add_child(cx_1, 'cx', 'q0')
dag.add_edge(q1, cx_2, 'q1')
cx_3 = dag.add_child(cx_2, 'cx', 'q0')
dag.add_edge(q1, cx_3, 'q1')

def filter_function(node):
    return node == 'cx'
res = rustworkx.collect_runs(dag, filter_function)
self.assertEqual([['cx', 'cx', 'cx']], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_runs.py:58*

### test_h_h_cx

**Category**: workflow  
**Description**: Workflow: test h h cx  
**Expected**: self.assertEqual([['h', 'cx'], ['h']], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDiGraph()
q0, q1 = dag.add_nodes_from(['q0', 'q1'])
h_1 = dag.add_child(q0, 'h', 'q0')
h_2 = dag.add_child(q1, 'h', 'q1')
cx_2 = dag.add_child(h_1, 'cx', 'q0')
dag.add_edge(h_2, cx_2, 'q1')

def filter_function(node):
    return node in ['cx', 'h']
res = rustworkx.collect_runs(dag, filter_function)
self.assertEqual([['h', 'cx'], ['h']], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_runs.py:95*

### test_cx_h_h_cx

**Category**: workflow  
**Description**: Workflow: test cx h h cx  
**Expected**: self.assertEqual([['cx'], ['h', 'cx'], ['h']], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDiGraph()
q0, q1 = dag.add_nodes_from(['q0', 'q1'])
cx_1 = dag.add_child(q0, 'cx', 'q0')
dag.add_edge(q1, cx_1, 'q1')
h_1 = dag.add_child(cx_1, 'h', 'q0')
h_2 = dag.add_child(cx_1, 'h', 'q1')
cx_2 = dag.add_child(h_1, 'cx', 'q0')
dag.add_edge(h_2, cx_2, 'q1')

def filter_function(node):
    return node in ['cx', 'h']
res = rustworkx.collect_runs(dag, filter_function)
self.assertEqual([['cx'], ['h', 'cx'], ['h']], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_runs.py:109*

### test_cx_h_cx

**Category**: workflow  
**Description**: Workflow: test cx h cx  
**Expected**: self.assertEqual([['cx'], ['h', 'cx']], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDiGraph()
q0, q1 = dag.add_nodes_from(['q0', 'q1'])
cx_1 = dag.add_child(q0, 'cx', 'q0')
dag.add_edge(q1, cx_1, 'q1')
h_1 = dag.add_child(cx_1, 'h', 'q0')
cx_2 = dag.add_child(h_1, 'cx', 'q0')
dag.add_edge(cx_1, cx_2, 'q1')

def filter_function(node):
    return node in ['cx', 'h']
res = rustworkx.collect_runs(dag, filter_function)
self.assertEqual([['cx'], ['h', 'cx']], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_runs.py:125*

### test_graph_dfs_edges_star

**Category**: workflow  
**Description**: Workflow: test graph dfs edges star  
**Expected**: self.assertEqual(visited, set(spokes))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.star_graph(101)
hub = 0
spokes = list(range(1, 101))
edges = rustworkx.graph_dfs_edges(graph, hub)
self.assertEqual(len(edges), 100)
for src, tgt in edges:
    self.assertEqual(src, hub)
visited = {tgt for _, tgt in edges}
self.assertEqual(visited, set(spokes))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_edges.py:53*

### test_graph_dfs_edges_star

**Category**: workflow  
**Description**: Workflow: test graph dfs edges star  
**Expected**: self.assertEqual(visited, set(spokes))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.star_graph(101)
hub = 0
spokes = list(range(1, 101))
edges = rustworkx.graph_dfs_edges(graph, hub)
self.assertEqual(len(edges), 100)
for src, tgt in edges:
    self.assertEqual(src, hub)
visited = {tgt for _, tgt in edges}
self.assertEqual(visited, set(spokes))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_edges.py:53*

### test_empty

**Category**: workflow  
**Description**: Workflow: test empty  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
N = 5
graph = rustworkx.PyGraph()
graph.add_nodes_from([i for i in range(N)])
expected_graph = rustworkx.PyGraph()
expected_graph.extend_from_edge_list([(i, j) for i in range(N) for j in range(N) if i < j])
complement_graph = rustworkx.complement(graph)
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_complement.py:28*

### test_complement

**Category**: workflow  
**Description**: Workflow: test complement  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
N = 8
graph = rustworkx.PyGraph()
graph.extend_from_edge_list([(j, i) for i in range(N) for j in range(N) if i < j and (i + j) % 3 == 0])
expected_graph = rustworkx.PyGraph()
expected_graph.extend_from_edge_list([(i, j) for i in range(N) for j in range(N) if i < j and (i + j) % 3 != 0])
complement_graph = rustworkx.complement(graph)
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_complement.py:50*

### test_empty

**Category**: workflow  
**Description**: Workflow: test empty  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
N = 5
graph = rustworkx.PyGraph()
graph.add_nodes_from([i for i in range(N)])
expected_graph = rustworkx.PyGraph()
expected_graph.extend_from_edge_list([(i, j) for i in range(N) for j in range(N) if i < j])
complement_graph = rustworkx.complement(graph)
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_complement.py:28*

### test_complement

**Category**: workflow  
**Description**: Workflow: test complement  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
N = 8
graph = rustworkx.PyGraph()
graph.extend_from_edge_list([(j, i) for i in range(N) for j in range(N) if i < j and (i + j) % 3 == 0])
expected_graph = rustworkx.PyGraph()
expected_graph.extend_from_edge_list([(i, j) for i in range(N) for j in range(N) if i < j and (i + j) % 3 != 0])
complement_graph = rustworkx.complement(graph)
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_complement.py:50*

### test_multiple_mapping

**Category**: workflow  
**Description**: Workflow: test multiple mapping  
**Expected**: self.assertEqual(expected, graph.edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.directed_path_graph(5)

graph = rustworkx.generators.directed_star_graph(5)
in_graph = rustworkx.generators.directed_star_graph(3, inward=True)

def map_function(source, target, _weight):
    if target > 2:
        return 2
    return 1
res = graph.substitute_node_with_subgraph(0, in_graph, map_function)
self.assertEqual({0: 5, 1: 6, 2: 7}, res)
expected = [(6, 5), (7, 5), (7, 4), (7, 3), (6, 2), (6, 1)]
self.assertEqual(expected, graph.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_substitute_node_with_subgraph.py:72*

### test_multiple_mapping_full

**Category**: workflow  
**Description**: Workflow: test multiple mapping full  
**Expected**: self.assertEqual(expected, graph.weighted_edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.directed_path_graph(5)

graph = rustworkx.generators.directed_star_graph(5)
in_graph = rustworkx.generators.directed_star_graph(weights=list(range(3)), inward=True)
in_graph.add_edge(1, 2, None)

def map_function(source, target, _weight):
    if target > 2:
        return 2
    return 1

def filter_fn(node):
    return node > 0

def map_weight(_):
    return 'migrated'
res = graph.substitute_node_with_subgraph(0, in_graph, map_function, filter_fn, map_weight)
self.assertEqual({1: 5, 2: 6}, res)
expected = [(5, 6, 'migrated'), (6, 4, None), (6, 3, None), (5, 2, None), (5, 1, None)]
self.assertEqual(expected, graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_substitute_node_with_subgraph.py:86*

### test_bidirectional

**Category**: workflow  
**Description**: Workflow: test bidirectional  
**Expected**: self.assertEqual(expected_edge_list, graph.edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.directed_path_graph(5)

graph = rustworkx.generators.directed_path_graph(5, bidirectional=True)
in_graph = rustworkx.generators.directed_star_graph(5, bidirectional=True)

def map_function(source, target, _weight):
    if source != 2:
        return 0
    else:
        return target
res = graph.substitute_node_with_subgraph(2, in_graph, map_function)
expected_node_map = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9}
self.assertEqual(expected_node_map, res)
expected_edge_list = [(0, 1), (1, 0), (3, 4), (4, 3), (6, 5), (5, 6), (7, 5), (5, 7), (8, 5), (5, 8), (9, 5), (5, 9), (3, 5), (1, 5), (8, 3), (6, 1)]
self.assertEqual(expected_edge_list, graph.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_substitute_node_with_subgraph.py:132*

### test_multiple_mapping

**Category**: workflow  
**Description**: Workflow: test multiple mapping  
**Expected**: self.assertEqual(expected, graph.edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_star_graph(5)
in_graph = rustworkx.generators.directed_star_graph(3, inward=True)

def map_function(source, target, _weight):
    if target > 2:
        return 2
    return 1
res = graph.substitute_node_with_subgraph(0, in_graph, map_function)
self.assertEqual({0: 5, 1: 6, 2: 7}, res)
expected = [(6, 5), (7, 5), (7, 4), (7, 3), (6, 2), (6, 1)]
self.assertEqual(expected, graph.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_substitute_node_with_subgraph.py:72*

### test_multiple_mapping_full

**Category**: workflow  
**Description**: Workflow: test multiple mapping full  
**Expected**: self.assertEqual(expected, graph.weighted_edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_star_graph(5)
in_graph = rustworkx.generators.directed_star_graph(weights=list(range(3)), inward=True)
in_graph.add_edge(1, 2, None)

def map_function(source, target, _weight):
    if target > 2:
        return 2
    return 1

def filter_fn(node):
    return node > 0

def map_weight(_):
    return 'migrated'
res = graph.substitute_node_with_subgraph(0, in_graph, map_function, filter_fn, map_weight)
self.assertEqual({1: 5, 2: 6}, res)
expected = [(5, 6, 'migrated'), (6, 4, None), (6, 3, None), (5, 2, None), (5, 1, None)]
self.assertEqual(expected, graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_substitute_node_with_subgraph.py:86*

### test_bidirectional

**Category**: workflow  
**Description**: Workflow: test bidirectional  
**Expected**: self.assertEqual(expected_edge_list, graph.edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_path_graph(5, bidirectional=True)
in_graph = rustworkx.generators.directed_star_graph(5, bidirectional=True)

def map_function(source, target, _weight):
    if source != 2:
        return 0
    else:
        return target
res = graph.substitute_node_with_subgraph(2, in_graph, map_function)
expected_node_map = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9}
self.assertEqual(expected_node_map, res)
expected_edge_list = [(0, 1), (1, 0), (3, 4), (4, 3), (6, 5), (5, 6), (7, 5), (5, 7), (8, 5), (5, 8), (9, 5), (5, 9), (3, 5), (1, 5), (8, 3), (6, 1)]
self.assertEqual(expected_edge_list, graph.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_substitute_node_with_subgraph.py:132*

### test_union_merge_all

**Category**: workflow  
**Description**: Workflow: test union merge all  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(dag_a, dag_c))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDiGraph()
dag_b = rustworkx.PyDiGraph()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'e_1')
dag_a.add_child(node_a, 'a_3', 'e_2')
node_b = dag_b.add_node('a_1')
dag_b.add_child(node_b, 'a_2', 'e_1')
dag_b.add_child(node_b, 'a_3', 'e_2')
dag_c = rustworkx.digraph_union(dag_a, dag_b, True, True)
self.assertTrue(rustworkx.is_isomorphic(dag_a, dag_c))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_union.py:18*

### test_union_basic_merge_nodes_only

**Category**: workflow  
**Description**: Workflow: test union basic merge nodes only  
**Expected**: self.assertTrue(len(dag_c.nodes()) == 3)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDiGraph()
dag_b = rustworkx.PyDiGraph()
node_a = dag_a.add_node('a_1')
child_a = dag_a.add_child(node_a, 'a_2', 'e_1')
dag_a.add_child(node_a, 'a_3', 'e_2')
node_b = dag_b.add_node('a_1')
dag_b.add_child(node_b, 'a_2', 'e_1')
dag_b.add_child(node_b, 'a_3', 'e_2')
dag_c = rustworkx.digraph_union(dag_a, dag_b, True, False)
self.assertTrue(len(dag_c.edge_list()) == 4)
self.assertTrue(len(dag_c.get_all_edge_data(node_a, child_a)) == 2)
self.assertTrue(len(dag_c.nodes()) == 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_union.py:34*

### test_union_basic_merge_none

**Category**: workflow  
**Description**: Workflow: test union basic merge none  
**Expected**: self.assertTrue(len(dag_c.edge_list()) == 4)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDiGraph()
dag_b = rustworkx.PyDiGraph()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'e_1')
dag_a.add_child(node_a, 'a_3', 'r_2')
node_b = dag_b.add_node('a_1')
dag_b.add_child(node_b, 'a_2', 'e_1')
dag_b.add_child(node_b, 'a_3', 'e_2')
dag_c = rustworkx.digraph_union(dag_a, dag_b, False, False)
self.assertTrue(len(dag_c.nodes()) == 6)
self.assertTrue(len(dag_c.edge_list()) == 4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_union.py:52*

### test_union_mismatch_edge_weight

**Category**: workflow  
**Description**: Workflow: test union mismatch edge weight  
**Expected**: self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 1, 'b')])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
first = rustworkx.PyDiGraph()
nodes = first.add_nodes_from([0, 1])
first.add_edges_from([(nodes[0], nodes[1], 'a')])
second = rustworkx.PyDiGraph()
nodes = second.add_nodes_from([0, 1])
second.add_edges_from([(nodes[0], nodes[1], 'b')])
final = rustworkx.digraph_union(first, second, merge_nodes=True, merge_edges=True)
self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 1, 'b')])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_union.py:69*

### test_union_node_hole

**Category**: workflow  
**Description**: Workflow: test union node hole  
**Expected**: self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a')])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
first = rustworkx.PyDiGraph()
nodes = first.add_nodes_from([0, 1])
first.add_edges_from([(nodes[0], nodes[1], 'a')])
second = rustworkx.PyDiGraph()
dummy = second.add_node('dummy')
nodes = second.add_nodes_from([0, 1])
second.add_edges_from([(nodes[0], nodes[1], 'a')])
second.remove_node(dummy)
final = rustworkx.digraph_union(first, second, merge_nodes=True, merge_edges=True)
self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a')])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_union.py:81*

### test_union_edge_between_merged_and_unmerged_nodes

**Category**: workflow  
**Description**: Workflow: test union edge between merged and unmerged nodes  
**Expected**: self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 2, 'b')])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
first = rustworkx.PyDiGraph()
nodes = first.add_nodes_from([0, 1])
first.add_edges_from([(nodes[0], nodes[1], 'a')])
second = rustworkx.PyDiGraph()
nodes = second.add_nodes_from([0, 2])
second.add_edges_from([(nodes[0], nodes[1], 'b')])
final = rustworkx.digraph_union(first, second, merge_nodes=True, merge_edges=True)
self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 2, 'b')])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_union.py:95*

### test_union_merge_all

**Category**: workflow  
**Description**: Workflow: test union merge all  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(dag_a, dag_c))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDiGraph()
dag_b = rustworkx.PyDiGraph()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'e_1')
dag_a.add_child(node_a, 'a_3', 'e_2')
node_b = dag_b.add_node('a_1')
dag_b.add_child(node_b, 'a_2', 'e_1')
dag_b.add_child(node_b, 'a_3', 'e_2')
dag_c = rustworkx.digraph_union(dag_a, dag_b, True, True)
self.assertTrue(rustworkx.is_isomorphic(dag_a, dag_c))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_union.py:18*

### test_union_basic_merge_nodes_only

**Category**: workflow  
**Description**: Workflow: test union basic merge nodes only  
**Expected**: self.assertTrue(len(dag_c.nodes()) == 3)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDiGraph()
dag_b = rustworkx.PyDiGraph()
node_a = dag_a.add_node('a_1')
child_a = dag_a.add_child(node_a, 'a_2', 'e_1')
dag_a.add_child(node_a, 'a_3', 'e_2')
node_b = dag_b.add_node('a_1')
dag_b.add_child(node_b, 'a_2', 'e_1')
dag_b.add_child(node_b, 'a_3', 'e_2')
dag_c = rustworkx.digraph_union(dag_a, dag_b, True, False)
self.assertTrue(len(dag_c.edge_list()) == 4)
self.assertTrue(len(dag_c.get_all_edge_data(node_a, child_a)) == 2)
self.assertTrue(len(dag_c.nodes()) == 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_union.py:34*

### test_union_basic_merge_none

**Category**: workflow  
**Description**: Workflow: test union basic merge none  
**Expected**: self.assertTrue(len(dag_c.edge_list()) == 4)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDiGraph()
dag_b = rustworkx.PyDiGraph()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'e_1')
dag_a.add_child(node_a, 'a_3', 'r_2')
node_b = dag_b.add_node('a_1')
dag_b.add_child(node_b, 'a_2', 'e_1')
dag_b.add_child(node_b, 'a_3', 'e_2')
dag_c = rustworkx.digraph_union(dag_a, dag_b, False, False)
self.assertTrue(len(dag_c.nodes()) == 6)
self.assertTrue(len(dag_c.edge_list()) == 4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_union.py:52*

### test_union_mismatch_edge_weight

**Category**: workflow  
**Description**: Workflow: test union mismatch edge weight  
**Expected**: self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 1, 'b')])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
first = rustworkx.PyDiGraph()
nodes = first.add_nodes_from([0, 1])
first.add_edges_from([(nodes[0], nodes[1], 'a')])
second = rustworkx.PyDiGraph()
nodes = second.add_nodes_from([0, 1])
second.add_edges_from([(nodes[0], nodes[1], 'b')])
final = rustworkx.digraph_union(first, second, merge_nodes=True, merge_edges=True)
self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 1, 'b')])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_union.py:69*

### test_multigraph_sum_cast_weight_func

**Category**: workflow  
**Description**: Workflow: test multigraph sum cast weight func  
**Expected**: self.assertTrue(np.array_equal(np.array([[0.0, 7.5], [0.0, 0.0]]), res))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 7.0)
dag.add_edge(node_a, node_b, 0.5)
res = rustworkx.digraph_adjacency_matrix(dag, lambda x: float(x))
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[0.0, 7.5], [0.0, 0.0]]), res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adjacency_matrix.py:79*

### test_multigraph_sum_cast_weight_func_non_zero_null

**Category**: workflow  
**Description**: Workflow: test multigraph sum cast weight func non zero null  
**Expected**: self.assertTrue(np.array_equal(np.array([[np.inf, 7.5], [np.inf, np.inf]]), res))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 7.0)
graph.add_edge(node_a, node_b, 0.5)
res = rustworkx.adjacency_matrix(graph, lambda x: float(x), null_value=np.inf)
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[np.inf, 7.5], [np.inf, np.inf]]), res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adjacency_matrix.py:88*

### test_digraph_with_index_holes

**Category**: workflow  
**Description**: Workflow: test digraph with index holes  
**Expected**: self.assertTrue(np.array_equal(np.array([[0, 1], [0, 0]]), res))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 1)
dag.add_child(node_a, 'c', 1)
dag.remove_node(node_b)
res = rustworkx.digraph_adjacency_matrix(dag, lambda x: 1)
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[0, 1], [0, 0]]), res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adjacency_matrix.py:109*

### test_random_graph_full_path

**Category**: workflow  
**Description**: Workflow: test random graph full path  
**Expected**: self.assertTrue(np.array_equal(adjacency_matrix, new_adjacency_matrix))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.directed_gnp_random_graph(100, 0.95, seed=42)
adjacency_matrix = rustworkx.digraph_adjacency_matrix(graph)
new_graph = rustworkx.PyDiGraph.from_adjacency_matrix(adjacency_matrix)
new_adjacency_matrix = rustworkx.digraph_adjacency_matrix(new_graph)
self.assertTrue(np.array_equal(adjacency_matrix, new_adjacency_matrix))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adjacency_matrix.py:128*

### test_non_zero_null

**Category**: workflow  
**Description**: Workflow: test non zero null  
**Expected**: self.assertTrue(np.array_equal(adj_matrix, expected_matrix))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
input_matrix = np.array([[np.inf, 1, np.inf], [1, np.inf, 1], [np.inf, 1, np.inf]], dtype=np.float64)
graph = rustworkx.PyDiGraph.from_adjacency_matrix(input_matrix, null_value=np.inf)
adj_matrix = rustworkx.adjacency_matrix(graph, float)
expected_matrix = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]], dtype=np.float64)
self.assertTrue(np.array_equal(adj_matrix, expected_matrix))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adjacency_matrix.py:154*

### test_nan_null

**Category**: workflow  
**Description**: Workflow: test nan null  
**Expected**: self.assertTrue(np.array_equal(adj_matrix, expected_matrix))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
input_matrix = np.array([[np.nan, 1, np.nan], [1, np.nan, 1], [np.nan, 1, np.nan]], dtype=np.float64)
graph = rustworkx.PyDiGraph.from_adjacency_matrix(input_matrix, null_value=np.nan)
adj_matrix = rustworkx.adjacency_matrix(graph, float)
expected_matrix = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=np.float64)
self.assertTrue(np.array_equal(adj_matrix, expected_matrix))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adjacency_matrix.py:177*

### test_parallel_edge

**Category**: workflow  
**Description**: Workflow: test parallel edge  
**Expected**: np.testing.assert_array_equal([[0.0, 8.0, 2.0], [0.0, 0.0, 9.0], [1.0, 0.0, 0.0]], sum_matrix)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
a = graph.add_node('A')
b = graph.add_node('B')
c = graph.add_node('C')
graph.add_edges_from([(a, b, 3.0), (a, b, 1.0), (a, c, 2.0), (b, c, 7.0), (c, a, 1.0), (b, c, 2.0), (a, b, 4.0)])
min_matrix = rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='min')
np.testing.assert_array_equal([[0.0, 1.0, 2.0], [0.0, 0.0, 2.0], [1.0, 0.0, 0.0]], min_matrix)
max_matrix = rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='max')
np.testing.assert_array_equal([[0.0, 4.0, 2.0], [0.0, 0.0, 7.0], [1.0, 0.0, 0.0]], max_matrix)
avg_matrix = rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='avg')
np.testing.assert_array_equal([[0.0, 8 / 3.0, 2.0], [0.0, 0.0, 4.5], [1.0, 0.0, 0.0]], avg_matrix)
sum_matrix = rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='sum')
np.testing.assert_array_equal([[0.0, 8.0, 2.0], [0.0, 0.0, 9.0], [1.0, 0.0, 0.0]], sum_matrix)
with self.assertRaises(ValueError):
    rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='error')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adjacency_matrix.py:266*

### test_multigraph_sum_cast_weight_func

**Category**: workflow  
**Description**: Workflow: test multigraph sum cast weight func  
**Expected**: self.assertTrue(np.array_equal(np.array([[0.0, 7.5], [0.0, 0.0]]), res))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 7.0)
dag.add_edge(node_a, node_b, 0.5)
res = rustworkx.digraph_adjacency_matrix(dag, lambda x: float(x))
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[0.0, 7.5], [0.0, 0.0]]), res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adjacency_matrix.py:79*

### test_multigraph_sum_cast_weight_func_non_zero_null

**Category**: workflow  
**Description**: Workflow: test multigraph sum cast weight func non zero null  
**Expected**: self.assertTrue(np.array_equal(np.array([[np.inf, 7.5], [np.inf, np.inf]]), res))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 7.0)
graph.add_edge(node_a, node_b, 0.5)
res = rustworkx.adjacency_matrix(graph, lambda x: float(x), null_value=np.inf)
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[np.inf, 7.5], [np.inf, np.inf]]), res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adjacency_matrix.py:88*

### test_digraph_with_index_holes

**Category**: workflow  
**Description**: Workflow: test digraph with index holes  
**Expected**: self.assertTrue(np.array_equal(np.array([[0, 1], [0, 0]]), res))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 1)
dag.add_child(node_a, 'c', 1)
dag.remove_node(node_b)
res = rustworkx.digraph_adjacency_matrix(dag, lambda x: 1)
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[0, 1], [0, 0]]), res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adjacency_matrix.py:109*

### test_irreducible1

**Category**: workflow  
**Description**: Workflow: Graph taken from figure 2 of "A simple, fast dominance algorithm." (2006).
https://hdl.handle.net/1911/96345  
**Expected**: self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph, 5).items())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n        Graph taken from figure 2 of "A simple, fast dominance algorithm." (2006).\n        https://hdl.handle.net/1911/96345\n        '
edges = [(1, 2), (2, 1), (3, 2), (4, 1), (5, 3), (5, 4)]
graph = rx.PyDiGraph()
graph.add_node(0)
graph.extend_from_edge_list(edges)
result = rx.immediate_dominators(graph, 5)
self.assertDictEqual(result, {i: 5 for i in range(1, 6)})
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(graph.edge_list())
self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph, 5).items())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dominance.py:65*

### test_irreducible2

**Category**: workflow  
**Description**: Workflow: Graph taken from figure 4 of "A simple, fast dominance algorithm." (2006).
https://hdl.handle.net/1911/96345  
**Expected**: self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph, 6).items())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n        Graph taken from figure 4 of "A simple, fast dominance algorithm." (2006).\n        https://hdl.handle.net/1911/96345\n        '
edges = [(1, 2), (2, 1), (2, 3), (3, 2), (4, 2), (4, 3), (5, 1), (6, 4), (6, 5)]
graph = rx.PyDiGraph()
graph.add_node(0)
graph.extend_from_edge_list(edges)
result = rx.immediate_dominators(graph, 6)
self.assertDictEqual(result, {i: 6 for i in range(1, 7)})
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(graph.edge_list())
self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph, 6).items())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dominance.py:83*

### test_domrel_png

**Category**: workflow  
**Description**: Workflow: Graph taken from https://commons.wikipedia.org/wiki/File:Domrel.png  
**Expected**: self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph.reverse(copy=False), 6).items())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n        Graph taken from https://commons.wikipedia.org/wiki/File:Domrel.png\n        '
edges = [(1, 2), (2, 3), (2, 4), (2, 6), (3, 5), (4, 5), (5, 2)]
graph = rx.PyDiGraph()
graph.add_node(0)
graph.extend_from_edge_list(edges)
result = rx.immediate_dominators(graph, 1)
self.assertDictEqual(result, {1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2})
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(graph.edge_list())
self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph, 1).items())
graph.reverse()
result = rx.immediate_dominators(graph, 6)
self.assertDictEqual(result, {1: 2, 2: 6, 3: 5, 4: 5, 5: 2, 6: 6})
self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph.reverse(copy=False), 6).items())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dominance.py:101*

### test_boost_example

**Category**: workflow  
**Description**: Workflow: Graph taken from Figure 1 of
http://www.boost.org/doc/libs/1_56_0/libs/graph/doc/lengauer_tarjan_dominator.htm  
**Expected**: self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph.reverse(copy=False), 7).items())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n        Graph taken from Figure 1 of\n        http://www.boost.org/doc/libs/1_56_0/libs/graph/doc/lengauer_tarjan_dominator.htm\n        '
edges = [(0, 1), (1, 2), (1, 3), (2, 7), (3, 4), (4, 5), (4, 6), (5, 7), (6, 4)]
graph = rx.PyDiGraph()
graph.extend_from_edge_list(edges)
result = rx.immediate_dominators(graph, 0)
self.assertDictEqual(result, {0: 0, 1: 0, 2: 1, 3: 1, 4: 3, 5: 4, 6: 4, 7: 1})
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(graph.edge_list())
self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph, 0).items())
graph.reverse()
result = rx.immediate_dominators(graph, 7)
self.assertDictEqual(result, {0: 1, 1: 7, 2: 7, 3: 4, 4: 5, 5: 7, 6: 4, 7: 7})
self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph.reverse(copy=False), 7).items())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dominance.py:127*

### test_irreducible1

**Category**: workflow  
**Description**: Workflow: Graph taken from figure 2 of "A simple, fast dominance algorithm." (2006).
https://hdl.handle.net/1911/96345  
**Expected**: self.assertDictEqual(nx.dominance_frontiers(nx_graph, 5), result)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n        Graph taken from figure 2 of "A simple, fast dominance algorithm." (2006).\n        https://hdl.handle.net/1911/96345\n        '
edges = [(1, 2), (2, 1), (3, 2), (4, 1), (5, 3), (5, 4)]
graph = rx.PyDiGraph()
graph.add_node(0)
graph.extend_from_edge_list(edges)
result = rx.dominance_frontiers(graph, 5)
self.assertDictEqual(result, {1: {2}, 2: {1}, 3: {2}, 4: {1}, 5: set()})
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(graph.edge_list())
self.assertDictEqual(nx.dominance_frontiers(nx_graph, 5), result)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dominance.py:194*

### test_irreducible2

**Category**: workflow  
**Description**: Workflow: Graph taken from figure 4 of "A simple, fast dominance algorithm." (2006).
https://hdl.handle.net/1911/96345  
**Expected**: self.assertDictEqual(nx.dominance_frontiers(nx_graph, 6), result)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n        Graph taken from figure 4 of "A simple, fast dominance algorithm." (2006).\n        https://hdl.handle.net/1911/96345\n        '
edges = [(1, 2), (2, 1), (2, 3), (3, 2), (4, 2), (4, 3), (5, 1), (6, 4), (6, 5)]
graph = rx.PyDiGraph()
graph.add_node(0)
graph.extend_from_edge_list(edges)
result = rx.dominance_frontiers(graph, 6)
self.assertDictEqual(result, {1: {2}, 2: {1, 3}, 3: {2}, 4: {2, 3}, 5: {1}, 6: set()})
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(graph.edge_list())
self.assertDictEqual(nx.dominance_frontiers(nx_graph, 6), result)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dominance.py:211*

### test_domrel_png

**Category**: workflow  
**Description**: Workflow: Graph taken from https://commons.wikipedia.org/wiki/File:Domrel.png  
**Expected**: self.assertDictEqual(nx.dominance_frontiers(nx_graph.reverse(copy=False), 6), result)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n        Graph taken from https://commons.wikipedia.org/wiki/File:Domrel.png\n        '
edges = [(1, 2), (2, 3), (2, 4), (2, 6), (3, 5), (4, 5), (5, 2)]
graph = rx.PyDiGraph()
graph.add_node(0)
graph.extend_from_edge_list(edges)
result = rx.dominance_frontiers(graph, 1)
self.assertDictEqual(result, {1: set(), 2: {2}, 3: {5}, 4: {5}, 5: {2}, 6: set()})
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(graph.edge_list())
self.assertDictEqual(nx.dominance_frontiers(nx_graph, 1), result)
graph.reverse()
result = rx.dominance_frontiers(graph, 6)
self.assertDictEqual(result, {1: set(), 2: {2}, 3: {2}, 4: {2}, 5: {2}, 6: set()})
self.assertDictEqual(nx.dominance_frontiers(nx_graph.reverse(copy=False), 6), result)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dominance.py:239*

### test_boost_example

**Category**: workflow  
**Description**: Workflow: Graph taken from Figure 1 of
http://www.boost.org/doc/libs/1_56_0/libs/graph/doc/lengauer_tarjan_dominator.htm  
**Expected**: self.assertDictEqual(nx.dominance_frontiers(nx_graph.reverse(copy=False), 7), result)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n        Graph taken from Figure 1 of\n        http://www.boost.org/doc/libs/1_56_0/libs/graph/doc/lengauer_tarjan_dominator.htm\n        '
edges = [(0, 1), (1, 2), (1, 3), (2, 7), (3, 4), (4, 5), (4, 6), (5, 7), (6, 4)]
graph = rx.PyDiGraph()
graph.extend_from_edge_list(edges)
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(graph.edge_list())
result = rx.dominance_frontiers(graph, 0)
self.assertDictEqual(result, {0: set(), 1: set(), 2: {7}, 3: {7}, 4: {4, 7}, 5: {7}, 6: {4}, 7: set()})
self.assertDictEqual(nx.dominance_frontiers(nx_graph, 0), result)
graph.reverse()
result = rx.dominance_frontiers(graph, 7)
self.assertDictEqual(result, {0: set(), 1: set(), 2: {1}, 3: {1}, 4: {1, 4}, 5: {1}, 6: {4}, 7: set()})
self.assertDictEqual(nx.dominance_frontiers(nx_graph.reverse(copy=False), 7), result)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dominance.py:283*

### test_missing_immediate_doms

**Category**: workflow  
**Description**: Workflow: Test that the `dominance_frontiers` function doesn't regress on
https://github.com/networkx/networkx/issues/2070  
**Expected**: self.assertDictEqual(result, {0: set(), 1: set(), 2: set(), 3: set(), 4: set(), 5: {3}})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
"\n        Test that the `dominance_frontiers` function doesn't regress on\n        https://github.com/networkx/networkx/issues/2070\n        "
edges = [(0, 1), (1, 2), (2, 3), (3, 4), (5, 3)]
graph = rx.PyDiGraph()
graph.extend_from_edge_list(edges)
idom = rx.immediate_dominators(graph, 0)
self.assertNotIn(5, idom)
result = rx.dominance_frontiers(graph, 0)
self.assertDictEqual(result, {0: set(), 1: set(), 2: set(), 3: set(), 4: set(), 5: {3}})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dominance.py:331*

### test_irreducible1

**Category**: workflow  
**Description**: Workflow: Graph taken from figure 2 of "A simple, fast dominance algorithm." (2006).
https://hdl.handle.net/1911/96345  
**Expected**: self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph, 5).items())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n        Graph taken from figure 2 of "A simple, fast dominance algorithm." (2006).\n        https://hdl.handle.net/1911/96345\n        '
edges = [(1, 2), (2, 1), (3, 2), (4, 1), (5, 3), (5, 4)]
graph = rx.PyDiGraph()
graph.add_node(0)
graph.extend_from_edge_list(edges)
result = rx.immediate_dominators(graph, 5)
self.assertDictEqual(result, {i: 5 for i in range(1, 6)})
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(graph.edge_list())
self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph, 5).items())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dominance.py:65*

### test_bellman_ford_length_with_no_path

**Category**: workflow  
**Description**: Workflow: test bellman ford length with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)

g = rustworkx.PyDiGraph()
a = g.add_node('A')
g.add_node('B')
path_lengths = rustworkx.digraph_bellman_ford_shortest_path_lengths(g, a, edge_cost_fn=float)
expected = {}
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bellman_ford.py:47*

### test_bellman_ford_length_with_no_path_and_goal

**Category**: workflow  
**Description**: Workflow: test bellman ford length with no path and goal  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)

g = rustworkx.PyDiGraph()
a = g.add_node('A')
b = g.add_node('B')
path_lengths = rustworkx.digraph_bellman_ford_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
expected = rustworkx.digraph_dijkstra_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bellman_ford.py:135*

### test_bellman_ford_with_no_path

**Category**: workflow  
**Description**: Workflow: test bellman ford with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)

g = rustworkx.PyDiGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.digraph_bellman_ford_shortest_path_lengths(g, a, lambda x: float(x))
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bellman_ford.py:147*

### test_bellman_ford_path_with_no_path

**Category**: workflow  
**Description**: Workflow: test bellman ford path with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)

g = rustworkx.PyDiGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.digraph_bellman_ford_shortest_paths(g, a)
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bellman_ford.py:155*

### test_bellman_ford_with_disconnected_nodes

**Category**: workflow  
**Description**: Workflow: test bellman ford with disconnected nodes  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)

g = rustworkx.PyDiGraph()
a = g.add_node('A')
b = g.add_child(a, 'B', 1.2)
g.add_node('C')
g.add_parent(b, 'D', 2.4)
path = rustworkx.digraph_bellman_ford_shortest_path_lengths(g, a, lambda x: x)
expected = {1: 1.2}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bellman_ford.py:163*

### test_find_negative_cycle_true_cycle

**Category**: workflow  
**Description**: Workflow: test find negative cycle true cycle  
**Expected**: self.assertTrue(cycle_weight < 0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)

graph = rustworkx.PyDiGraph()
graph.add_nodes_from(list(range(4)))
graph.add_edges_from([(0, 1, 1), (1, 2, -1), (2, 3, -1), (3, 0, -1)])
cycle = rustworkx.find_negative_cycle(graph, edge_cost_fn=float)
cycle_weight = 0
for i in range(len(cycle) - 1):
    cycle_weight += graph.get_edge_data(cycle[i], cycle[i + 1])
self.assertTrue(cycle_weight < 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bellman_ford.py:276*

### test_find_negative_cycle_self_loop_cycle

**Category**: workflow  
**Description**: Workflow: test find negative cycle self loop cycle  
**Expected**: self.assertTrue(cycle_weight < 0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)

graph = rustworkx.PyDiGraph()
graph.add_nodes_from(list(range(4)))
graph.add_edges_from([(0, 1, 1), (1, 0, 1), (0, 0, -1)])
cycle = rustworkx.find_negative_cycle(graph, edge_cost_fn=float)
cycle_weight = 0
for i in range(len(cycle) - 1):
    cycle_weight += graph.get_edge_data(cycle[i], cycle[i + 1])
self.assertTrue(cycle_weight < 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bellman_ford.py:296*

### test_bellman_ford_length_with_no_path

**Category**: workflow  
**Description**: Workflow: test bellman ford length with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDiGraph()
a = g.add_node('A')
g.add_node('B')
path_lengths = rustworkx.digraph_bellman_ford_shortest_path_lengths(g, a, edge_cost_fn=float)
expected = {}
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bellman_ford.py:47*

### test_bellman_ford_length_with_no_path_and_goal

**Category**: workflow  
**Description**: Workflow: test bellman ford length with no path and goal  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDiGraph()
a = g.add_node('A')
b = g.add_node('B')
path_lengths = rustworkx.digraph_bellman_ford_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
expected = rustworkx.digraph_dijkstra_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bellman_ford.py:135*

### test_bellman_ford_with_no_path

**Category**: workflow  
**Description**: Workflow: test bellman ford with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDiGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.digraph_bellman_ford_shortest_path_lengths(g, a, lambda x: float(x))
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bellman_ford.py:147*

### test_single_source_all_shortest_paths_zero_weight

**Category**: workflow  
**Description**: Workflow: test single source all shortest paths zero weight  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.cycle = rustworkx.PyDiGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.directed = rustworkx.PyDiGraph()
self.directed_nodes = self.directed.add_nodes_from([0, 1, 2, 3])
self.directed.add_edges_from([(self.directed_nodes[0], self.directed_nodes[1], 1), (self.directed_nodes[0], self.directed_nodes[2], 1), (self.directed_nodes[1], self.directed_nodes[3], 1), (self.directed_nodes[2], self.directed_nodes[3], 1)])

graph = rustworkx.PyDiGraph()
nodes = graph.add_nodes_from([0, 1, 2, 3])
graph.add_edge(nodes[0], nodes[1], 0.0)
graph.add_edge(nodes[0], nodes[2], 1.0)
graph.add_edge(nodes[1], nodes[3], 1.0)
graph.add_edge(nodes[2], nodes[3], 0.0)
source = nodes[0]
shortest_lengths = rustworkx.digraph_dijkstra_shortest_path_lengths(graph, source, lambda e: e)
all_shortest_paths = rustworkx.digraph_single_source_all_shortest_paths(graph, source)
for target in nodes:
    target_idx = target
    if target_idx == source:
        continue
    all_paths = rustworkx.all_simple_paths(graph, source, target_idx)

    def path_weight(path):
        weight = 0.0
        for i in range(len(path) - 1):
            edge = graph.get_edge_data(path[i], path[i + 1])
            weight += edge
        return weight
    expected_paths = [path for path in all_paths if path_weight(path) == shortest_lengths[target_idx]]
    computed_paths = all_shortest_paths.get(target_idx, [])
    expected_paths.sort()
    computed_paths.sort()
    self.assertEqual(computed_paths, expected_paths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_digraph_single_source_all_shortest_paths.py:55*

### test_single_source_all_shortest_paths_zero_weight

**Category**: workflow  
**Description**: Workflow: test single source all shortest paths zero weight  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
nodes = graph.add_nodes_from([0, 1, 2, 3])
graph.add_edge(nodes[0], nodes[1], 0.0)
graph.add_edge(nodes[0], nodes[2], 1.0)
graph.add_edge(nodes[1], nodes[3], 1.0)
graph.add_edge(nodes[2], nodes[3], 0.0)
source = nodes[0]
shortest_lengths = rustworkx.digraph_dijkstra_shortest_path_lengths(graph, source, lambda e: e)
all_shortest_paths = rustworkx.digraph_single_source_all_shortest_paths(graph, source)
for target in nodes:
    target_idx = target
    if target_idx == source:
        continue
    all_paths = rustworkx.all_simple_paths(graph, source, target_idx)

    def path_weight(path):
        weight = 0.0
        for i in range(len(path) - 1):
            edge = graph.get_edge_data(path[i], path[i + 1])
            weight += edge
        return weight
    expected_paths = [path for path in all_paths if path_weight(path) == shortest_lengths[target_idx]]
    computed_paths = all_shortest_paths.get(target_idx, [])
    expected_paths.sort()
    computed_paths.sort()
    self.assertEqual(computed_paths, expected_paths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_digraph_single_source_all_shortest_paths.py:55*

### test_partially_connected_graph

**Category**: workflow  
**Description**: Workflow: test partially connected graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.cycle_graph(32)
graph.add_nodes_from(list(range(32)))
with self.subTest(disconnected=False):
    res = rustworkx.unweighted_average_shortest_path_length(graph)
    self.assertTrue(math.isinf(res), 'Output is not infinity')
with self.subTest(disconnected=True):
    s = 8192
    den = 992
    res = rustworkx.unweighted_average_shortest_path_length(graph, disconnected=True)
    self.assertAlmostEqual(s / den, res, delta=1e-07)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_avg_shortest_path.py:71*

### test_connected_cycle_graph

**Category**: workflow  
**Description**: Workflow: test connected cycle graph  
**Expected**: self.assertAlmostEqual(s / den, res, delta=1e-07)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.cycle_graph(32)
res = rustworkx.unweighted_average_shortest_path_length(graph)
s = 8192
den = 992
self.assertAlmostEqual(s / den, res, delta=1e-07)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_avg_shortest_path.py:84*

### test_partially_connected_graph

**Category**: workflow  
**Description**: Workflow: test partially connected graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.cycle_graph(32)
graph.add_nodes_from(list(range(32)))
with self.subTest(disconnected=False):
    res = rustworkx.unweighted_average_shortest_path_length(graph)
    self.assertTrue(math.isinf(res), 'Output is not infinity')
with self.subTest(disconnected=True):
    s = 8192
    den = 992
    res = rustworkx.unweighted_average_shortest_path_length(graph, disconnected=True)
    self.assertAlmostEqual(s / den, res, delta=1e-07)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_avg_shortest_path.py:71*

### test_connected_cycle_graph

**Category**: workflow  
**Description**: Workflow: test connected cycle graph  
**Expected**: self.assertAlmostEqual(s / den, res, delta=1e-07)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.cycle_graph(32)
res = rustworkx.unweighted_average_shortest_path_length(graph)
s = 8192
den = 992
self.assertAlmostEqual(s / den, res, delta=1e-07)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_avg_shortest_path.py:84*

### test_complete_graph

**Category**: workflow  
**Description**: Workflow: test complete graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.mesh_graph(5)
centrality = rustworkx.eigenvector_centrality(graph)
expected_value = math.sqrt(1.0 / 5.0)
for value in centrality.values():
    self.assertAlmostEqual(value, expected_value)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_centrality.py:133*

### test_complete_graph

**Category**: workflow  
**Description**: Workflow: test complete graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.complete_graph(5)
centrality = rustworkx.graph_katz_centrality(graph)
expected_value = math.sqrt(1.0 / 5.0)
for value in centrality.values():
    self.assertAlmostEqual(value, expected_value, delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_centrality.py:154*

### test_beta_dictionary

**Category**: workflow  
**Description**: Workflow: test beta dictionary  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.generators.generalized_petersen_graph(5, 2)
beta = {i: 0.1 * i ** 2 for i in range(10)}
rx_centrality = rustworkx.katz_centrality(rx_graph, alpha=0.25, beta=beta)
nx_graph = nx.Graph()
nx_graph.add_edges_from(rx_graph.edge_list())
nx_centrality = nx.katz_centrality(nx_graph, alpha=0.25, beta=beta)
for key in rx_centrality.keys():
    self.assertAlmostEqual(rx_centrality[key], nx_centrality[key], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_centrality.py:175*

### test_complete_graph

**Category**: workflow  
**Description**: Workflow: test complete graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.mesh_graph(5)
centrality = rustworkx.edge_betweenness_centrality(graph)
for value in centrality.values():
    self.assertAlmostEqual(value, 0.1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_centrality.py:195*

### test_degree_centrality_complete_graph

**Category**: workflow  
**Description**: Workflow: test degree centrality complete graph  
**Expected**: self.assertEqual(expected, centrality)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
edge_list = [(self.a, self.b, 1), (self.b, self.c, 1), (self.c, self.d, 1)]
self.graph.add_edges_from(edge_list)

graph = rustworkx.generators.complete_graph(5)
centrality = rustworkx.degree_centrality(graph)
expected = {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}
self.assertEqual(expected, centrality)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_centrality.py:275*

### test_degree_centrality_multigraph

**Category**: workflow  
**Description**: Workflow: test degree centrality multigraph  
**Expected**: self.assertEqual(expected, dict(centrality))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
edge_list = [(self.a, self.b, 1), (self.b, self.c, 1), (self.c, self.d, 1)]
self.graph.add_edges_from(edge_list)

graph = rustworkx.PyGraph()
a = graph.add_node('A')
b = graph.add_node('B')
c = graph.add_node('C')
edge_list = [(a, b, 1), (a, b, 2), (b, c, 1)]
graph.add_edges_from(edge_list)
centrality = rustworkx.degree_centrality(graph)
expected = {0: 1.0, 1: 1.5, 2: 0.5}
self.assertEqual(expected, dict(centrality))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_centrality.py:293*

### test_complete_graph

**Category**: workflow  
**Description**: Workflow: test complete graph  
**Expected**: self.assertAlmostEqual(result, 1.0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.complete_graph(4)
result = rustworkx.graph_group_degree_centrality(graph, [0])
self.assertAlmostEqual(result, 1.0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_centrality.py:320*

### test_star_center

**Category**: workflow  
**Description**: Workflow: test star center  
**Expected**: self.assertAlmostEqual(result, 1.0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
center = graph.add_node('center')
for _ in range(4):
    leaf = graph.add_node('leaf')
    graph.add_edge(center, leaf, None)
result = rustworkx.graph_group_closeness_centrality(graph, [center])
self.assertAlmostEqual(result, 1.0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_centrality.py:347*

### test_star_center

**Category**: workflow  
**Description**: Workflow: test star center  
**Expected**: self.assertAlmostEqual(result, 6.0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
center = graph.add_node('center')
for _ in range(4):
    leaf = graph.add_node('leaf')
    graph.add_edge(center, leaf, None)
result = rustworkx.graph_group_betweenness_centrality(graph, [center], normalized=False)
self.assertAlmostEqual(result, 6.0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_centrality.py:385*

### test_degree_complete_graph

**Category**: workflow  
**Description**: Workflow: test degree complete graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.complete_graph(6)
cases = {(0,): 1.0, (0, 1): 1.0, (0, 2, 4): 1.0}
for group, expected in cases.items():
    result = rustworkx.graph_group_degree_centrality(graph, list(group))
    self.assertAlmostEqual(result, expected, places=10)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_centrality.py:439*

### test_vs_dijkstra_all_pairs

**Category**: workflow  
**Description**: Workflow: test vs dijkstra all pairs  
**Expected**: self.assertEqual(result, expected)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
a = graph.add_node('A')
b = graph.add_node('B')
c = graph.add_node('C')
d = graph.add_node('D')
e = graph.add_node('E')
f = graph.add_node('F')
edge_list = [(a, b, 7), (c, a, 9), (a, d, 14), (b, c, 10), (d, c, 2), (d, e, 9), (b, f, 15), (c, f, 11), (e, f, 6)]
graph.add_edges_from(edge_list)
dijkstra_lengths = rustworkx.digraph_all_pairs_dijkstra_path_lengths(graph, float)
expected = {k: {**v, k: 0.0} for k, v in dijkstra_lengths.items()}
result = rustworkx.digraph_floyd_warshall(graph, float, parallel_threshold=self.parallel_threshold)
self.assertEqual(result, expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_floyd_warshall.py:79*

### test_vs_dijkstra_all_pairs_with_node_removal

**Category**: workflow  
**Description**: Workflow: test vs dijkstra all pairs with node removal  
**Expected**: self.assertEqual(result, expected)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
a = graph.add_node('A')
b = graph.add_node('B')
c = graph.add_node('C')
d = graph.add_node('D')
e = graph.add_node('E')
f = graph.add_node('F')
edge_list = [(a, b, 7), (c, a, 9), (a, d, 14), (b, c, 10), (d, c, 2), (d, e, 9), (b, f, 15), (c, f, 11), (e, f, 6)]
graph.add_edges_from(edge_list)
graph.remove_node(d)
dijkstra_lengths = rustworkx.digraph_all_pairs_dijkstra_path_lengths(graph, float)
expected = {k: {**v, k: 0.0} for k, v in dijkstra_lengths.items()}
result = rustworkx.digraph_floyd_warshall(graph, float, parallel_threshold=self.parallel_threshold)
self.assertEqual(result, expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_floyd_warshall.py:110*

### test_vs_dijkstra_all_pairs

**Category**: workflow  
**Description**: Workflow: test vs dijkstra all pairs  
**Expected**: self.assertEqual(result, expected)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
a = graph.add_node('A')
b = graph.add_node('B')
c = graph.add_node('C')
d = graph.add_node('D')
e = graph.add_node('E')
f = graph.add_node('F')
edge_list = [(a, b, 7), (c, a, 9), (a, d, 14), (b, c, 10), (d, c, 2), (d, e, 9), (b, f, 15), (c, f, 11), (e, f, 6)]
graph.add_edges_from(edge_list)
dijkstra_lengths = rustworkx.digraph_all_pairs_dijkstra_path_lengths(graph, float)
expected = {k: {**v, k: 0.0} for k, v in dijkstra_lengths.items()}
result = rustworkx.digraph_floyd_warshall(graph, float, parallel_threshold=self.parallel_threshold)
self.assertEqual(result, expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_floyd_warshall.py:79*

### test_vs_dijkstra_all_pairs_with_node_removal

**Category**: workflow  
**Description**: Workflow: test vs dijkstra all pairs with node removal  
**Expected**: self.assertEqual(result, expected)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
a = graph.add_node('A')
b = graph.add_node('B')
c = graph.add_node('C')
d = graph.add_node('D')
e = graph.add_node('E')
f = graph.add_node('F')
edge_list = [(a, b, 7), (c, a, 9), (a, d, 14), (b, c, 10), (d, c, 2), (d, e, 9), (b, f, 15), (c, f, 11), (e, f, 6)]
graph.add_edges_from(edge_list)
graph.remove_node(d)
dijkstra_lengths = rustworkx.digraph_all_pairs_dijkstra_path_lengths(graph, float)
expected = {k: {**v, k: 0.0} for k, v in dijkstra_lengths.items()}
result = rustworkx.digraph_floyd_warshall(graph, float, parallel_threshold=self.parallel_threshold)
self.assertEqual(result, expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_floyd_warshall.py:110*

### test_path_2_tensor_path_2

**Category**: workflow  
**Description**: Workflow: test path 2 tensor path 2  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.path_graph(2)
graph_2 = rustworkx.generators.path_graph(2)
graph_product, node_map = rustworkx.graph_tensor_product(graph_1, graph_2)
expected_node_map = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (1, 1): 3}
self.assertEqual(node_map, expected_node_map)
expected_edges = [(0, 3), (1, 2)]
self.assertEqual(graph_product.num_nodes(), 4)
self.assertEqual(graph_product.num_edges(), 2)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_tensor_product.py:26*

### test_path_2_tensor_path_3

**Category**: workflow  
**Description**: Workflow: test path 2 tensor path 3  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.path_graph(2)
graph_2 = rustworkx.generators.path_graph(3)
graph_product, node_map = rustworkx.graph_tensor_product(graph_1, graph_2)
expected_node_map = {(0, 1): 1, (1, 0): 3, (0, 0): 0, (1, 2): 5, (0, 2): 2, (1, 1): 4}
self.assertEqual(dict(node_map), expected_node_map)
expected_edges = [(0, 4), (1, 5), (1, 3), (2, 4)]
self.assertEqual(graph_product.num_nodes(), 6)
self.assertEqual(graph_product.num_edges(), 4)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_tensor_product.py:40*

### test_multi_graph_1

**Category**: workflow  
**Description**: Workflow: test multi graph 1  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.path_graph(2)
graph_1.add_edge(0, 1, None)
graph_2 = rustworkx.generators.path_graph(2)
graph_product, _ = rustworkx.graph_tensor_product(graph_1, graph_2)
expected_edges = [(0, 3), (0, 3), (1, 2), (1, 2)]
self.assertEqual(graph_product.num_edges(), 4)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_tensor_product.py:74*

### test_multi_graph_2

**Category**: workflow  
**Description**: Workflow: test multi graph 2  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.path_graph(2)
graph_1.add_edge(0, 0, None)
graph_2 = rustworkx.generators.path_graph(2)
graph_product, _ = rustworkx.graph_tensor_product(graph_1, graph_2)
expected_edges = [(0, 3), (0, 1), (1, 2)]
self.assertEqual(graph_product.num_edges(), 3)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_tensor_product.py:84*

### test_multi_graph_3

**Category**: workflow  
**Description**: Workflow: test multi graph 3  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.path_graph(2)
graph_2 = rustworkx.generators.path_graph(2)
graph_2.add_edge(0, 1, None)
graph_product, _ = rustworkx.graph_tensor_product(graph_1, graph_2)
expected_edges = [(0, 3), (0, 3), (1, 2), (1, 2)]
self.assertEqual(graph_product.num_edges(), 4)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_tensor_product.py:94*

### test_multi_graph_4

**Category**: workflow  
**Description**: Workflow: test multi graph 4  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.path_graph(2)
graph_2 = rustworkx.generators.path_graph(2)
graph_2.add_edge(0, 0, None)
graph_product, _ = rustworkx.graph_tensor_product(graph_1, graph_2)
expected_edges = [(0, 3), (0, 2), (1, 2)]
self.assertEqual(graph_product.num_edges(), 3)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_tensor_product.py:104*

### test_path_2_tensor_path_2

**Category**: workflow  
**Description**: Workflow: test path 2 tensor path 2  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.path_graph(2)
graph_2 = rustworkx.generators.path_graph(2)
graph_product, node_map = rustworkx.graph_tensor_product(graph_1, graph_2)
expected_node_map = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (1, 1): 3}
self.assertEqual(node_map, expected_node_map)
expected_edges = [(0, 3), (1, 2)]
self.assertEqual(graph_product.num_nodes(), 4)
self.assertEqual(graph_product.num_edges(), 2)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_tensor_product.py:26*

### test_path_2_tensor_path_3

**Category**: workflow  
**Description**: Workflow: test path 2 tensor path 3  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.path_graph(2)
graph_2 = rustworkx.generators.path_graph(3)
graph_product, node_map = rustworkx.graph_tensor_product(graph_1, graph_2)
expected_node_map = {(0, 1): 1, (1, 0): 3, (0, 0): 0, (1, 2): 5, (0, 2): 2, (1, 1): 4}
self.assertEqual(dict(node_map), expected_node_map)
expected_edges = [(0, 4), (1, 5), (1, 3), (2, 4)]
self.assertEqual(graph_product.num_nodes(), 6)
self.assertEqual(graph_product.num_edges(), 4)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_tensor_product.py:40*

### test_multi_graph_1

**Category**: workflow  
**Description**: Workflow: test multi graph 1  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.path_graph(2)
graph_1.add_edge(0, 1, None)
graph_2 = rustworkx.generators.path_graph(2)
graph_product, _ = rustworkx.graph_tensor_product(graph_1, graph_2)
expected_edges = [(0, 3), (0, 3), (1, 2), (1, 2)]
self.assertEqual(graph_product.num_edges(), 4)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_tensor_product.py:74*

### test_multi_graph_2

**Category**: workflow  
**Description**: Workflow: test multi graph 2  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.path_graph(2)
graph_1.add_edge(0, 0, None)
graph_2 = rustworkx.generators.path_graph(2)
graph_product, _ = rustworkx.graph_tensor_product(graph_1, graph_2)
expected_edges = [(0, 3), (0, 1), (1, 2)]
self.assertEqual(graph_product.num_edges(), 3)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_tensor_product.py:84*

### test_full_rary_tree_graph

**Category**: workflow  
**Description**: Workflow: test full rary tree graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
b_factors = {0: 0, 1: 2, 2: 2, 3: 5}
num_nodes = {0: 0, 1: 4, 2: 10, 3: 15}
expected_edges = {0: [], 1: [(0, 1), (0, 2), (1, 3)], 2: [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7), (3, 8), (4, 9)], 3: [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (2, 11), (2, 12), (2, 13), (2, 14)]}
for n in range(4):
    with self.subTest(n=n):
        graph = rustworkx.generators.full_rary_tree(b_factors[n], num_nodes[n])
        self.assertEqual(list(graph.edge_list()), expected_edges[n])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_full_rary_tree.py:18*

### test_full_rary_tree_graph_weights

**Category**: workflow  
**Description**: Workflow: test full rary tree graph weights  
**Expected**: self.assertEqual(list(graph.edge_list()), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.full_rary_tree(2, 4, weights=list(range(4)))
expected_edges = [(0, 1), (0, 2), (1, 3)]
self.assertEqual(len(graph), 4)
self.assertEqual([x for x in range(4)], graph.nodes())
self.assertEqual(len(graph.edges()), 3)
self.assertEqual(list(graph.edge_list()), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_full_rary_tree.py:67*

### test_full_rary_tree_graph_weight_less_nodes

**Category**: workflow  
**Description**: Workflow: test full rary tree graph weight less nodes  
**Expected**: self.assertEqual(len(graph.edges()), 5)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.full_rary_tree(2, 6, weights=list(range(4)))
self.assertEqual(len(graph), 6)
expected_weights = [x for x in range(4)]
expected_weights.extend([None, None])
self.assertEqual(expected_weights, graph.nodes())
self.assertEqual(len(graph.edges()), 5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_full_rary_tree.py:75*

### test_full_rary_tree_graph

**Category**: workflow  
**Description**: Workflow: test full rary tree graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
b_factors = {0: 0, 1: 2, 2: 2, 3: 5}
num_nodes = {0: 0, 1: 4, 2: 10, 3: 15}
expected_edges = {0: [], 1: [(0, 1), (0, 2), (1, 3)], 2: [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7), (3, 8), (4, 9)], 3: [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (2, 11), (2, 12), (2, 13), (2, 14)]}
for n in range(4):
    with self.subTest(n=n):
        graph = rustworkx.generators.full_rary_tree(b_factors[n], num_nodes[n])
        self.assertEqual(list(graph.edge_list()), expected_edges[n])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_full_rary_tree.py:18*

### test_full_rary_tree_graph_weights

**Category**: workflow  
**Description**: Workflow: test full rary tree graph weights  
**Expected**: self.assertEqual(list(graph.edge_list()), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.full_rary_tree(2, 4, weights=list(range(4)))
expected_edges = [(0, 1), (0, 2), (1, 3)]
self.assertEqual(len(graph), 4)
self.assertEqual([x for x in range(4)], graph.nodes())
self.assertEqual(len(graph.edges()), 3)
self.assertEqual(list(graph.edge_list()), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_full_rary_tree.py:67*

### test_full_rary_tree_graph_weight_less_nodes

**Category**: workflow  
**Description**: Workflow: test full rary tree graph weight less nodes  
**Expected**: self.assertEqual(len(graph.edges()), 5)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.full_rary_tree(2, 6, weights=list(range(4)))
self.assertEqual(len(graph), 6)
expected_weights = [x for x in range(4)]
expected_weights.extend([None, None])
self.assertEqual(expected_weights, graph.nodes())
self.assertEqual(len(graph.edges()), 5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_full_rary_tree.py:75*

### test_graph

**Category**: workflow  
**Description**: Workflow: test graph  
**Expected**: self.assertEqual(out_edge_map, expected_edge_map)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
node_d = graph.add_node('d')
edge_ab = graph.add_edge(node_a, node_b, 1)
edge_ac = graph.add_edge(node_a, node_c, 1)
edge_bc = graph.add_edge(node_b, node_c, 1)
edge_ad = graph.add_edge(node_a, node_d, 1)
out_graph, out_edge_map = rustworkx.graph_line_graph(graph)
expected_nodes = [0, 1, 2, 3]
expected_edge_map = {edge_ab: 0, edge_ac: 1, edge_bc: 2, edge_ad: 3}
expected_edges = [(3, 1), (3, 0), (1, 0), (2, 0), (2, 1)]
self.assertEqual(out_graph.node_indices(), expected_nodes)
self.assertEqual(out_graph.edge_list(), expected_edges)
self.assertEqual(out_edge_map, expected_edge_map)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_line_graph.py:19*

### test_graph_with_holes

**Category**: workflow  
**Description**: Workflow: Graph with missing node and edge indices.  
**Expected**: self.assertEqual(out_edge_map, expected_edge_map)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Graph with missing node and edge indices.'
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
node_d = graph.add_node('d')
node_e = graph.add_node('e')
edge_ab = graph.add_edge(node_a, node_b, 1)
graph.add_edge(node_b, node_c, 1)
graph.add_edge(node_c, node_d, 1)
edge_de = graph.add_edge(node_d, node_e, 1)
graph.remove_node(node_c)
out_graph, out_edge_map = rustworkx.graph_line_graph(graph)
expected_nodes = [0, 1]
expected_edge_map = {edge_ab: 0, edge_de: 1}
expected_edges = []
self.assertEqual(out_graph.node_indices(), expected_nodes)
self.assertEqual(out_graph.edge_list(), expected_edges)
self.assertEqual(out_edge_map, expected_edge_map)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_line_graph.py:38*

### test_graph

**Category**: workflow  
**Description**: Workflow: test graph  
**Expected**: self.assertEqual(out_edge_map, expected_edge_map)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
node_d = graph.add_node('d')
edge_ab = graph.add_edge(node_a, node_b, 1)
edge_ac = graph.add_edge(node_a, node_c, 1)
edge_bc = graph.add_edge(node_b, node_c, 1)
edge_ad = graph.add_edge(node_a, node_d, 1)
out_graph, out_edge_map = rustworkx.graph_line_graph(graph)
expected_nodes = [0, 1, 2, 3]
expected_edge_map = {edge_ab: 0, edge_ac: 1, edge_bc: 2, edge_ad: 3}
expected_edges = [(3, 1), (3, 0), (1, 0), (2, 0), (2, 1)]
self.assertEqual(out_graph.node_indices(), expected_nodes)
self.assertEqual(out_graph.edge_list(), expected_edges)
self.assertEqual(out_edge_map, expected_edge_map)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_line_graph.py:19*

### test_graph_with_holes

**Category**: workflow  
**Description**: Workflow: Graph with missing node and edge indices.  
**Expected**: self.assertEqual(out_edge_map, expected_edge_map)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Graph with missing node and edge indices.'
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
node_d = graph.add_node('d')
node_e = graph.add_node('e')
edge_ab = graph.add_edge(node_a, node_b, 1)
graph.add_edge(node_b, node_c, 1)
graph.add_edge(node_c, node_d, 1)
edge_de = graph.add_edge(node_d, node_e, 1)
graph.remove_node(node_c)
out_graph, out_edge_map = rustworkx.graph_line_graph(graph)
expected_nodes = [0, 1]
expected_edge_map = {edge_ab: 0, edge_de: 1}
expected_edges = []
self.assertEqual(out_graph.node_indices(), expected_nodes)
self.assertEqual(out_graph.edge_list(), expected_edges)
self.assertEqual(out_edge_map, expected_edge_map)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_line_graph.py:38*

### test_transitivity_fulltriangle_directed

**Category**: workflow  
**Description**: Workflow: test transitivity fulltriangle directed  
**Expected**: self.assertEqual(res, 1.0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
graph.add_nodes_from(list(range(3)))
graph.add_edges_from_no_data([(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)])
res = rustworkx.transitivity(graph)
self.assertEqual(res, 1.0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitivity.py:33*

### test_transitivity_fulltriangle_directed

**Category**: workflow  
**Description**: Workflow: test transitivity fulltriangle directed  
**Expected**: self.assertEqual(res, 1.0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
graph.add_nodes_from(list(range(3)))
graph.add_edges_from_no_data([(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)])
res = rustworkx.transitivity(graph)
self.assertEqual(res, 1.0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitivity.py:33*

### test_directed_path_graph_node_attrs

**Category**: workflow  
**Description**: Workflow: test directed path graph node attrs  
**Expected**: self.assertEqual(json.loads(res), expected)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_path_graph(3)
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
res = rustworkx.node_link_json(graph, node_attrs=dict)
expected = {'attrs': None, 'directed': True, 'links': [{'data': None, 'id': 0, 'source': 0, 'target': 1}, {'data': None, 'id': 1, 'source': 1, 'target': 2}], 'multigraph': True, 'nodes': [{'data': {'nodeLabel': 'node=0'}, 'id': 0}, {'data': {'nodeLabel': 'node=1'}, 'id': 1}, {'data': {'nodeLabel': 'node=2'}, 'id': 2}]}
self.assertEqual(json.loads(res), expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_node_link_json.py:44*

### test_file_output

**Category**: workflow  
**Description**: Workflow: test file output  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_path_graph(3)
graph.attrs = 'directed_path_graph'
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
for edge, (source, target, _weight) in graph.edge_index_map().items():
    graph.update_edge_by_index(edge, {'edgeLabel': f'{source}->{target}'})
expected = {'attrs': {'label': 'directed_path_graph'}, 'directed': True, 'links': [{'data': {'edgeLabel': '0->1'}, 'id': 0, 'source': 0, 'target': 1}, {'data': {'edgeLabel': '1->2'}, 'id': 1, 'source': 1, 'target': 2}], 'multigraph': True, 'nodes': [{'data': {'nodeLabel': 'node=0'}, 'id': 0}, {'data': {'nodeLabel': 'node=1'}, 'id': 1}, {'data': {'nodeLabel': 'node=2'}, 'id': 2}]}
with tempfile.NamedTemporaryFile() as fd:
    res = rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
    self.assertIsNone(res)
    json_dict = json.load(fd)
    self.assertEqual(json_dict, expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_node_link_json.py:95*

### test_round_trip_file

**Category**: workflow  
**Description**: Workflow: test round trip file  
**Expected**: self.assertEqual(new.attrs, graph.attrs)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_heavy_hex_graph(19)
graph.attrs = 'directed_heavy_hex_graph'
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
for edge, (source, target, _weight) in graph.edge_index_map().items():
    graph.update_edge_by_index(edge, {'edgeLabel': f'{source}-          >{target}'})
with tempfile.NamedTemporaryFile() as fd:
    rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
    new = rustworkx.from_node_link_json_file(fd.name, graph_attrs=lambda x: x['label'])
self.assertIsInstance(new, type(graph))
self.assertEqual(new.nodes(), graph.nodes())
self.assertEqual(new.weighted_edge_list(), graph.weighted_edge_list())
self.assertEqual(new.attrs, graph.attrs)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_node_link_json.py:154*

### test_round_trip_networkx

**Category**: workflow  
**Description**: Workflow: test round trip networkx  
**Expected**: self.assertEqual(new.edge_list(), list(graph.edges()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = nx.generators.path_graph(5, create_using=nx.DiGraph)
try:
    node_link_str = json.dumps(nx.node_link_data(graph, edges='links'))
except TypeError:
    node_link_str = json.dumps(nx.node_link_data(graph))
new = rustworkx.parse_node_link_json(node_link_str)
self.assertIsInstance(new, rustworkx.PyDiGraph)
self.assertEqual(new.num_nodes(), graph.number_of_nodes())
self.assertEqual(new.edge_list(), list(graph.edges()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_node_link_json.py:175*

### test_round_trip_file_no_callback

**Category**: workflow  
**Description**: Workflow: test round trip file no callback  
**Expected**: self.assertEqual(new.attrs, {'label': graph.attrs})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_heavy_hex_graph(19)
graph.attrs = 'directed_heavy_hex_graph'
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
for edge, (source, target, _weight) in graph.edge_index_map().items():
    graph.update_edge_by_index(edge, {'edgeLabel': f'{source}-          >{target}'})
with tempfile.NamedTemporaryFile() as fd:
    rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
    new = rustworkx.from_node_link_json_file(fd.name)
self.assertIsInstance(new, type(graph))
self.assertEqual(new.nodes(), graph.nodes())
self.assertEqual(new.weighted_edge_list(), graph.weighted_edge_list())
self.assertEqual(new.attrs, {'label': graph.attrs})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_node_link_json.py:187*

### test_node_indices_preserved_with_contraction

**Category**: workflow  
**Description**: Workflow: Test that node indices are preserved after contraction (issue #1503)  
**Expected**: self.assertEqual(graph.edge_list(), restored.edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test that node indices are preserved after contraction (issue #1503)'
graph = rustworkx.PyDiGraph()
graph.add_node('A')
graph.add_node('B')
graph.add_node('C')
contracted_idx = graph.contract_nodes([0, 1], 'AB')
graph.add_edge(2, contracted_idx, 'C->AB')
self.assertEqual([2, contracted_idx], graph.node_indices())
json_str = rustworkx.node_link_json(graph)
restored = rustworkx.parse_node_link_json(json_str)
self.assertEqual(graph.node_indices(), restored.node_indices())
self.assertEqual(graph.edge_list(), restored.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_node_link_json.py:247*

### test_directed_path_graph_node_attrs

**Category**: workflow  
**Description**: Workflow: test directed path graph node attrs  
**Expected**: self.assertEqual(json.loads(res), expected)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_path_graph(3)
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
res = rustworkx.node_link_json(graph, node_attrs=dict)
expected = {'attrs': None, 'directed': True, 'links': [{'data': None, 'id': 0, 'source': 0, 'target': 1}, {'data': None, 'id': 1, 'source': 1, 'target': 2}], 'multigraph': True, 'nodes': [{'data': {'nodeLabel': 'node=0'}, 'id': 0}, {'data': {'nodeLabel': 'node=1'}, 'id': 1}, {'data': {'nodeLabel': 'node=2'}, 'id': 2}]}
self.assertEqual(json.loads(res), expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_node_link_json.py:44*

### test_file_output

**Category**: workflow  
**Description**: Workflow: test file output  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_path_graph(3)
graph.attrs = 'directed_path_graph'
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
for edge, (source, target, _weight) in graph.edge_index_map().items():
    graph.update_edge_by_index(edge, {'edgeLabel': f'{source}->{target}'})
expected = {'attrs': {'label': 'directed_path_graph'}, 'directed': True, 'links': [{'data': {'edgeLabel': '0->1'}, 'id': 0, 'source': 0, 'target': 1}, {'data': {'edgeLabel': '1->2'}, 'id': 1, 'source': 1, 'target': 2}], 'multigraph': True, 'nodes': [{'data': {'nodeLabel': 'node=0'}, 'id': 0}, {'data': {'nodeLabel': 'node=1'}, 'id': 1}, {'data': {'nodeLabel': 'node=2'}, 'id': 2}]}
with tempfile.NamedTemporaryFile() as fd:
    res = rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
    self.assertIsNone(res)
    json_dict = json.load(fd)
    self.assertEqual(json_dict, expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_node_link_json.py:95*

### test_round_trip_file

**Category**: workflow  
**Description**: Workflow: test round trip file  
**Expected**: self.assertEqual(new.attrs, graph.attrs)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_heavy_hex_graph(19)
graph.attrs = 'directed_heavy_hex_graph'
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
for edge, (source, target, _weight) in graph.edge_index_map().items():
    graph.update_edge_by_index(edge, {'edgeLabel': f'{source}-          >{target}'})
with tempfile.NamedTemporaryFile() as fd:
    rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
    new = rustworkx.from_node_link_json_file(fd.name, graph_attrs=lambda x: x['label'])
self.assertIsInstance(new, type(graph))
self.assertEqual(new.nodes(), graph.nodes())
self.assertEqual(new.weighted_edge_list(), graph.weighted_edge_list())
self.assertEqual(new.attrs, graph.attrs)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_node_link_json.py:154*

### test_round_trip_networkx

**Category**: workflow  
**Description**: Workflow: test round trip networkx  
**Expected**: self.assertEqual(new.edge_list(), list(graph.edges()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = nx.generators.path_graph(5, create_using=nx.DiGraph)
try:
    node_link_str = json.dumps(nx.node_link_data(graph, edges='links'))
except TypeError:
    node_link_str = json.dumps(nx.node_link_data(graph))
new = rustworkx.parse_node_link_json(node_link_str)
self.assertIsInstance(new, rustworkx.PyDiGraph)
self.assertEqual(new.num_nodes(), graph.number_of_nodes())
self.assertEqual(new.edge_list(), list(graph.edges()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_node_link_json.py:175*

### test_with_dangling_node

**Category**: workflow  
**Description**: Workflow: test with dangling node  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
edges = [(0, 1), (0, 2), (2, 0), (2, 1), (2, 4), (3, 4), (3, 5), (4, 3), (4, 5), (5, 4)]
rx_graph = rustworkx.PyDiGraph()
nx_graph = nx.DiGraph()
rx_graph.extend_from_edge_list(edges)
nx_graph.add_edges_from(edges)
alpha = 0.9
tol = 1e-08
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha, tol=tol)
nx_ranks = pagerank_python(nx_graph, alpha=alpha, tol=tol)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pagerank.py:119*

### test_with_dangling_node_and_argument

**Category**: workflow  
**Description**: Workflow: test with dangling node and argument  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
edges = [(0, 1), (0, 2), (2, 0), (2, 1), (2, 4), (3, 4), (3, 5), (4, 3), (4, 5), (5, 4)]
rx_graph = rustworkx.PyDiGraph()
nx_graph = nx.DiGraph()
rx_graph.extend_from_edge_list(edges)
nx_graph.add_edges_from(edges)
dangling = {0: 0, 1: 1, 2: 2, 3: 0, 5: 0}
alpha = 0.85
tol = 1e-08
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha, tol=tol, dangling=dangling)
nx_ranks = pagerank_python(nx_graph, alpha=alpha, tol=tol, dangling=dangling)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pagerank.py:148*

### test_with_removed_node

**Category**: workflow  
**Description**: Workflow: test with removed node  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 0), (4, 1), (4, 2), (0, 4)]
graph.extend_from_edge_list(edges)
graph.remove_node(3)
ranks = rustworkx.pagerank(graph)
expected_ranks = {0: 0.17401467654615052, 1: 0.2479710438690554, 2: 0.3847906219106203, 4: 0.19322365767417365}
for v in graph.node_indices():
    self.assertAlmostEqual(ranks[v], expected_ranks[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pagerank.py:197*

### test_pagerank_with_nstart

**Category**: workflow  
**Description**: Workflow: test pagerank with nstart  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.generators.directed_complete_graph(4)
nstart = {0: 0.5, 1: 0.5, 2: 0, 3: 0}
alpha = 0.85
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha, nstart=nstart)
nx_graph = nx.DiGraph(list(rx_graph.edge_list()))
nx_ranks = pagerank_python(nx_graph, alpha=alpha, nstart=nstart)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pagerank.py:225*

### test_pagerank_with_personalize

**Category**: workflow  
**Description**: Workflow: test pagerank with personalize  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.generators.directed_complete_graph(4)
personalize = {0: 0, 1: 0, 2: 0, 3: 1}
alpha = 0.85
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha, personalization=personalize)
nx_graph = nx.DiGraph(list(rx_graph.edge_list()))
nx_ranks = pagerank_python(nx_graph, alpha=alpha, personalization=personalize)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pagerank.py:236*

### test_pagerank_with_personalize_missing

**Category**: workflow  
**Description**: Workflow: test pagerank with personalize missing  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.generators.directed_complete_graph(4)
personalize = {3: 1}
alpha = 0.85
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha, personalization=personalize)
nx_graph = nx.DiGraph(list(rx_graph.edge_list()))
nx_ranks = pagerank_python(nx_graph, alpha=alpha, personalization=personalize)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pagerank.py:247*

### test_multi_digraph

**Category**: workflow  
**Description**: Workflow: test multi digraph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.PyDiGraph()
rx_graph.extend_from_edge_list([(0, 1), (1, 0), (0, 1), (1, 0), (0, 1), (1, 0), (1, 2), (2, 1), (1, 2), (2, 1), (2, 3), (3, 2), (2, 3), (3, 2)])
nx_graph = nx.MultiDiGraph(list(rx_graph.edge_list()))
alpha = 0.9
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha)
nx_ranks = pagerank_python(nx_graph, alpha=alpha)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pagerank.py:258*

### test_multi_digraph_versus_weighted

**Category**: workflow  
**Description**: Workflow: test multi digraph versus weighted  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
multi_graph = rustworkx.PyDiGraph()
multi_graph.extend_from_edge_list([(0, 1), (1, 0), (0, 1), (1, 0), (0, 1), (1, 0), (1, 2), (2, 1), (1, 2), (2, 1), (2, 3), (3, 2), (2, 3), (3, 2)])
weighted_graph = rustworkx.PyDiGraph()
weighted_graph.extend_from_weighted_edge_list([(0, 1, 3), (1, 0, 3), (1, 2, 2), (2, 1, 2), (2, 3, 2), (3, 2, 2)])
alpha = 0.85
ranks_multi = rustworkx.pagerank(multi_graph, alpha=alpha, weight_fn=lambda _: 1.0)
ranks_weight = rustworkx.pagerank(weighted_graph, alpha=alpha, weight_fn=float)
for v in multi_graph.node_indices():
    self.assertAlmostEqual(ranks_multi[v], ranks_weight[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pagerank.py:292*

### test_with_dangling_node

**Category**: workflow  
**Description**: Workflow: test with dangling node  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
edges = [(0, 1), (0, 2), (2, 0), (2, 1), (2, 4), (3, 4), (3, 5), (4, 3), (4, 5), (5, 4)]
rx_graph = rustworkx.PyDiGraph()
nx_graph = nx.DiGraph()
rx_graph.extend_from_edge_list(edges)
nx_graph.add_edges_from(edges)
alpha = 0.9
tol = 1e-08
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha, tol=tol)
nx_ranks = pagerank_python(nx_graph, alpha=alpha, tol=tol)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pagerank.py:119*

### test_with_dangling_node_and_argument

**Category**: workflow  
**Description**: Workflow: test with dangling node and argument  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
edges = [(0, 1), (0, 2), (2, 0), (2, 1), (2, 4), (3, 4), (3, 5), (4, 3), (4, 5), (5, 4)]
rx_graph = rustworkx.PyDiGraph()
nx_graph = nx.DiGraph()
rx_graph.extend_from_edge_list(edges)
nx_graph.add_edges_from(edges)
dangling = {0: 0, 1: 1, 2: 2, 3: 0, 5: 0}
alpha = 0.85
tol = 1e-08
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha, tol=tol, dangling=dangling)
nx_ranks = pagerank_python(nx_graph, alpha=alpha, tol=tol, dangling=dangling)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pagerank.py:148*

### test_graph_dfs_tree_edges_restricted

**Category**: workflow  
**Description**: Workflow: test graph dfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

class TreeEdgesRecorderRestricted(rustworkx.visit.DFSVisitor):
    prohibited = [(0, 2), (1, 2)]

    def __init__(self):
        self.edges = []

    def tree_edge(self, edge):
        edge = (edge[0], edge[1])
        if edge in self.prohibited:
            raise rustworkx.visit.PruneSearch
        self.edges.append(edge)
vis = TreeEdgesRecorderRestricted()
rustworkx.graph_dfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_search.py:58*

### test_graph_dfs_tree_edges_restricted

**Category**: workflow  
**Description**: Workflow: test graph dfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
class TreeEdgesRecorderRestricted(rustworkx.visit.DFSVisitor):
    prohibited = [(0, 2), (1, 2)]

    def __init__(self):
        self.edges = []

    def tree_edge(self, edge):
        edge = (edge[0], edge[1])
        if edge in self.prohibited:
            raise rustworkx.visit.PruneSearch
        self.edges.append(edge)
vis = TreeEdgesRecorderRestricted()
rustworkx.graph_dfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_search.py:58*

### test_graph_to_dot_to_file

**Category**: workflow  
**Description**: Workflow: test graph to dot to file  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

graph = rustworkx.PyGraph()
graph.add_node({'color': 'black', 'fillcolor': 'green', 'label': 'a', 'style': 'filled'})
graph.add_node({'color': 'black', 'fillcolor': 'red', 'label': 'a', 'style': 'filled'})
graph.add_edge(0, 1, dict(label='1', name='1'))
expected = 'graph {\n0 [color=black, fillcolor=green, label="a", style=filled];\n1 [color=black, fillcolor=red, label="a", style=filled];\n0 -- 1 [label="1", name=1];\n}\n'
res = graph.to_dot(lambda node: node, lambda edge: edge, filename=self.path)
self.addCleanup(os.remove, self.path)
self.assertIsNone(res)
with open(self.path) as fd:
    res = fd.read()
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dot.py:80*

### test_graph_to_dot_to_file

**Category**: workflow  
**Description**: Workflow: test graph to dot to file  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
graph.add_node({'color': 'black', 'fillcolor': 'green', 'label': 'a', 'style': 'filled'})
graph.add_node({'color': 'black', 'fillcolor': 'red', 'label': 'a', 'style': 'filled'})
graph.add_edge(0, 1, dict(label='1', name='1'))
expected = 'graph {\n0 [color=black, fillcolor=green, label="a", style=filled];\n1 [color=black, fillcolor=red, label="a", style=filled];\n0 -- 1 [label="1", name=1];\n}\n'
res = graph.to_dot(lambda node: node, lambda edge: edge, filename=self.path)
self.addCleanup(os.remove, self.path)
self.assertIsNone(res)
with open(self.path) as fd:
    res = fd.read()
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dot.py:80*

### test_clear_edges_reuse

**Category**: workflow  
**Description**: Workflow: test clear edges reuse  
**Expected**: self.assertEqual(dag.edges(), [{'a': 1}, {'a': 2}])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
dag.clear_edges()
dag.add_edge(node_a, node_b, {'a': 1})
dag.add_edge(node_a, node_c, {'a': 2})
self.assertEqual(dag.num_nodes(), 3)
self.assertEqual(dag.num_edges(), 2)
self.assertEqual(dag.nodes(), ['a', 'b', 'c'])
self.assertEqual(dag.edges(), [{'a': 1}, {'a': 2}])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_clear.py:55*

### test_clear_edges_reuse

**Category**: workflow  
**Description**: Workflow: test clear edges reuse  
**Expected**: self.assertEqual(dag.edges(), [{'a': 1}, {'a': 2}])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
dag.clear_edges()
dag.add_edge(node_a, node_b, {'a': 1})
dag.add_edge(node_a, node_c, {'a': 2})
self.assertEqual(dag.num_nodes(), 3)
self.assertEqual(dag.num_edges(), 2)
self.assertEqual(dag.nodes(), ['a', 'b', 'c'])
self.assertEqual(dag.edges(), [{'a': 1}, {'a': 2}])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_clear.py:55*

### test_copy_returns_graph

**Category**: workflow  
**Description**: Workflow: test copy returns graph  
**Expected**: self.assertIsInstance(graph_b, rustworkx.PyDiGraph)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph()
node_a = graph_a.add_node('a_1')
node_b = graph_a.add_node('a_2')
graph_a.add_edge(node_a, node_b, 'edge_1')
node_c = graph_a.add_node('a_3')
graph_a.add_edge(node_b, node_c, 'edge_2')
graph_b = graph_a.copy()
self.assertIsInstance(graph_b, rustworkx.PyDiGraph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_copy.py:20*

### test_copy_with_holes_returns_graph

**Category**: workflow  
**Description**: Workflow: test copy with holes returns graph  
**Expected**: self.assertEqual([node_a, node_c], graph_b.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph()
node_a = graph_a.add_node('a_1')
node_b = graph_a.add_node('a_2')
graph_a.add_edge(node_a, node_b, 'edge_1')
node_c = graph_a.add_node('a_3')
graph_a.add_edge(node_b, node_c, 'edge_2')
graph_a.remove_node(node_b)
graph_b = graph_a.copy()
self.assertIsInstance(graph_b, rustworkx.PyDiGraph)
self.assertEqual([node_a, node_c], graph_b.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_copy.py:30*

### test_copy_shared_ref

**Category**: workflow  
**Description**: Workflow: test copy shared ref  
**Expected**: self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph()
node_a = graph_a.add_node({'a': 1})
node_b = graph_a.add_node({'b': 2})
graph_a.add_edge(node_a, node_b, {'edge': 1})
graph_b = graph_a.copy()
graph_a[0]['a'] = 42
graph_b.get_edge_data(0, 1)['edge'] = 162
self.assertEqual(graph_b[0]['a'], 42)
self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_copy.py:47*

### test_python_copy_check_cycle

**Category**: workflow  
**Description**: Workflow: test python copy check cycle  
**Expected**: self.assertFalse(graph_d.check_cycle)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph(check_cycle=True)
graph_b = copy.copy(graph_a)
graph_c = rustworkx.PyDiGraph(check_cycle=False)
graph_d = copy.copy(graph_c)
self.assertTrue(graph_b.check_cycle)
self.assertFalse(graph_d.check_cycle)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_copy.py:58*

### test_python_copy_same_objects

**Category**: workflow  
**Description**: Workflow: test python copy same objects  
**Expected**: self.assertIs(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph(attrs=[1])
node_a = graph_a.add_node([2])
node_b = graph_a.add_child(node_a, [3], [4])
graph_b = copy.copy(graph_a)
self.assertEqual(graph_a.attrs, graph_b.attrs)
self.assertIs(graph_a.attrs, graph_b.attrs)
self.assertEqual(graph_a[node_a], graph_b[node_a])
self.assertIs(graph_a[node_a], graph_b[node_a])
self.assertEqual(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))
self.assertIs(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_copy.py:66*

### test_copy_returns_graph

**Category**: workflow  
**Description**: Workflow: test copy returns graph  
**Expected**: self.assertIsInstance(graph_b, rustworkx.PyDiGraph)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph()
node_a = graph_a.add_node('a_1')
node_b = graph_a.add_node('a_2')
graph_a.add_edge(node_a, node_b, 'edge_1')
node_c = graph_a.add_node('a_3')
graph_a.add_edge(node_b, node_c, 'edge_2')
graph_b = graph_a.copy()
self.assertIsInstance(graph_b, rustworkx.PyDiGraph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_copy.py:20*

### test_copy_with_holes_returns_graph

**Category**: workflow  
**Description**: Workflow: test copy with holes returns graph  
**Expected**: self.assertEqual([node_a, node_c], graph_b.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph()
node_a = graph_a.add_node('a_1')
node_b = graph_a.add_node('a_2')
graph_a.add_edge(node_a, node_b, 'edge_1')
node_c = graph_a.add_node('a_3')
graph_a.add_edge(node_b, node_c, 'edge_2')
graph_a.remove_node(node_b)
graph_b = graph_a.copy()
self.assertIsInstance(graph_b, rustworkx.PyDiGraph)
self.assertEqual([node_a, node_c], graph_b.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_copy.py:30*

### test_copy_shared_ref

**Category**: workflow  
**Description**: Workflow: test copy shared ref  
**Expected**: self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph()
node_a = graph_a.add_node({'a': 1})
node_b = graph_a.add_node({'b': 2})
graph_a.add_edge(node_a, node_b, {'edge': 1})
graph_b = graph_a.copy()
graph_a[0]['a'] = 42
graph_b.get_edge_data(0, 1)['edge'] = 162
self.assertEqual(graph_b[0]['a'], 42)
self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_copy.py:47*

### test_python_copy_check_cycle

**Category**: workflow  
**Description**: Workflow: test python copy check cycle  
**Expected**: self.assertFalse(graph_d.check_cycle)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph(check_cycle=True)
graph_b = copy.copy(graph_a)
graph_c = rustworkx.PyDiGraph(check_cycle=False)
graph_d = copy.copy(graph_c)
self.assertTrue(graph_b.check_cycle)
self.assertFalse(graph_d.check_cycle)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_copy.py:58*

### test_python_copy_same_objects

**Category**: workflow  
**Description**: Workflow: test python copy same objects  
**Expected**: self.assertIs(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph(attrs=[1])
node_a = graph_a.add_node([2])
node_b = graph_a.add_child(node_a, [3], [4])
graph_b = copy.copy(graph_a)
self.assertEqual(graph_a.attrs, graph_b.attrs)
self.assertIs(graph_a.attrs, graph_b.attrs)
self.assertEqual(graph_a[node_a], graph_b[node_a])
self.assertIs(graph_a[node_a], graph_b[node_a])
self.assertEqual(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))
self.assertIs(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_copy.py:66*

### test_single_neighbor

**Category**: workflow  
**Description**: Workflow: test single neighbor  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res = dag.neighbors(node_a)
self.assertCountEqual([node_c, node_b], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_neighbors.py:20*

### test_unique_neighbors_on_dags

**Category**: workflow  
**Description**: Workflow: test unique neighbors on dags  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', ['edge a->b'])
node_c = dag.add_child(node_a, 'c', ['edge a->c'])
dag.add_edge(node_a, node_b, ['edge a->b bis'])
res = dag.neighbors(node_a)
self.assertCountEqual([node_c, node_b], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_neighbors.py:28*

### test_single_neighbor_dir

**Category**: workflow  
**Description**: Workflow: test single neighbor dir  
**Expected**: self.assertEqual([], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res = dag.successor_indices(node_a)
self.assertEqual([node_c, node_b], res)
res = dag.predecessor_indices(node_a)
self.assertEqual([], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_neighbors.py:37*

### test_neighbor_dir_surrounded

**Category**: workflow  
**Description**: Workflow: test neighbor dir surrounded  
**Expected**: self.assertEqual([node_a], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
res = dag.successor_indices(node_b)
self.assertEqual([node_c], res)
res = dag.predecessor_indices(node_b)
self.assertEqual([node_a], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_neighbors.py:47*

### test_undirected_neighbors

**Category**: workflow  
**Description**: Workflow: test undirected neighbors  
**Expected**: self.assertEqual([node_a], undirected)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
directed = dag.neighbors(node_b)
self.assertEqual([], directed)
undirected = dag.neighbors_undirected(node_b)
self.assertEqual([node_a], undirected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_neighbors.py:62*

### test_undirected_neighbors_cycle

**Category**: workflow  
**Description**: Workflow: test undirected neighbors cycle  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
num_nodes = 10
dag = rustworkx.generators.directed_cycle_graph(num_nodes, bidirectional=False)
undirected_dag = dag.to_undirected()
for node in dag.node_indices():
    undirected_neighbors = dag.neighbors_undirected(node)
    expected_neighbors = undirected_dag.neighbors(node)
    self.assertEqual(sorted(undirected_neighbors), sorted(expected_neighbors))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_neighbors.py:73*

### test_single_neighbor

**Category**: workflow  
**Description**: Workflow: test single neighbor  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res = dag.neighbors(node_a)
self.assertCountEqual([node_c, node_b], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_neighbors.py:20*

### test_unique_neighbors_on_dags

**Category**: workflow  
**Description**: Workflow: test unique neighbors on dags  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', ['edge a->b'])
node_c = dag.add_child(node_a, 'c', ['edge a->c'])
dag.add_edge(node_a, node_b, ['edge a->b bis'])
res = dag.neighbors(node_a)
self.assertCountEqual([node_c, node_b], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_neighbors.py:28*

### test_single_neighbor_dir

**Category**: workflow  
**Description**: Workflow: test single neighbor dir  
**Expected**: self.assertEqual([], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res = dag.successor_indices(node_a)
self.assertEqual([node_c, node_b], res)
res = dag.predecessor_indices(node_a)
self.assertEqual([], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_neighbors.py:37*

### test_neighbor_dir_surrounded

**Category**: workflow  
**Description**: Workflow: test neighbor dir surrounded  
**Expected**: self.assertEqual([node_a], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
res = dag.successor_indices(node_b)
self.assertEqual([node_c], res)
res = dag.predecessor_indices(node_b)
self.assertEqual([node_a], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_neighbors.py:47*

### test_single_neighbor

**Category**: workflow  
**Description**: Workflow: test single neighbor  
**Expected**: self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res = dag.adj(node_a)
self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adj.py:19*

### test_single_neighbor_dir

**Category**: workflow  
**Description**: Workflow: test single neighbor dir  
**Expected**: self.assertEqual({}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res = dag.adj_direction(node_a, False)
self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)
res = dag.adj_direction(node_a, True)
self.assertEqual({}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adj.py:33*

### test_neighbor_dir_surrounded

**Category**: workflow  
**Description**: Workflow: test neighbor dir surrounded  
**Expected**: self.assertEqual({node_a: {'a': 1}}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
res = dag.adj_direction(node_b, False)
self.assertEqual({node_c: {'a': 2}}, res)
res = dag.adj_direction(node_b, True)
self.assertEqual({node_a: {'a': 1}}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adj.py:43*

### test_single_neighbor_dir_out_edges

**Category**: workflow  
**Description**: Workflow: test single neighbor dir out edges  
**Expected**: self.assertEqual([(node_a, node_c, {'a': 2}), (node_a, node_b, {'a': 1})], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res = dag.out_edges(node_a)
self.assertEqual([(node_a, node_c, {'a': 2}), (node_a, node_b, {'a': 1})], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adj.py:53*

### test_neighbor_dir_surrounded_in_out_edges

**Category**: workflow  
**Description**: Workflow: test neighbor dir surrounded in out edges  
**Expected**: self.assertEqual([(node_a, node_b, {'a': 1})], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
res = dag.out_edges(node_b)
self.assertEqual([(node_b, node_c, {'a': 2})], res)
res = dag.in_edges(node_b)
self.assertEqual([(node_a, node_b, {'a': 1})], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adj.py:61*

### test_single_neighbor

**Category**: workflow  
**Description**: Workflow: test single neighbor  
**Expected**: self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res = dag.adj(node_a)
self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adj.py:19*

### test_single_neighbor_dir

**Category**: workflow  
**Description**: Workflow: test single neighbor dir  
**Expected**: self.assertEqual({}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res = dag.adj_direction(node_a, False)
self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)
res = dag.adj_direction(node_a, True)
self.assertEqual({}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adj.py:33*

### test_neighbor_dir_surrounded

**Category**: workflow  
**Description**: Workflow: test neighbor dir surrounded  
**Expected**: self.assertEqual({node_a: {'a': 1}}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
res = dag.adj_direction(node_b, False)
self.assertEqual({node_c: {'a': 2}}, res)
res = dag.adj_direction(node_b, True)
self.assertEqual({node_a: {'a': 1}}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adj.py:43*

### test_single_neighbor_dir_out_edges

**Category**: workflow  
**Description**: Workflow: test single neighbor dir out edges  
**Expected**: self.assertEqual([(node_a, node_c, {'a': 2}), (node_a, node_b, {'a': 1})], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res = dag.out_edges(node_a)
self.assertEqual([(node_a, node_c, {'a': 2}), (node_a, node_b, {'a': 1})], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adj.py:53*

### test_neighbor_dir_surrounded_in_out_edges

**Category**: workflow  
**Description**: Workflow: test neighbor dir surrounded in out edges  
**Expected**: self.assertEqual([(node_a, node_b, {'a': 1})], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
res = dag.out_edges(node_b)
self.assertEqual([(node_b, node_c, {'a': 2})], res)
res = dag.in_edges(node_b)
self.assertEqual([(node_a, node_b, {'a': 1})], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_adj.py:61*

### test_cycle_path_len_gt_1

**Category**: workflow  
**Description**: Workflow:     ┌─┐              ┌─┐
 ┌4─┤a├─1┐           │m├──1───┐
 │  └─┘  │           └▲┘      │
┌▼┐     ┌▼┐           │      ┌▼┐
│d│     │b│   ───►    │      │b│
└▲┘     └┬┘           │      └┬┘
 │  ┌─┐  2            │  ┌─┐  2
 └3─┤c│◄─┘            └3─┤c│◄─┘
    └─┘                  └─┘  
**Expected**: self.assertEqual({(node_b, node_c), (node_c, node_m), (node_m, node_b)}, set(dag.edge_list()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n            ┌─┐              ┌─┐\n         ┌4─┤a├─1┐           │m├──1───┐\n         │  └─┘  │           └▲┘      │\n        ┌▼┐     ┌▼┐           │      ┌▼┐\n        │d│     │b│   ───►    │      │b│\n        └▲┘     └┬┘           │      └┬┘\n         │  ┌─┐  2            │  ┌─┐  2\n         └3─┤c│◄─┘            └3─┤c│◄─┘\n            └─┘                  └─┘\n        '
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 1)
node_c = dag.add_child(node_b, 'c', 2)
node_d = dag.add_child(node_c, 'c', 3)
dag.add_edge(node_a, node_d, 4)
with self.assertRaises(rustworkx.DAGWouldCycle):
    dag.contract_nodes([node_a, node_d], 'm', check_cycle=True)
node_m = dag.contract_nodes([node_a, node_d], 'm')
self.assertEqual([node_b, node_c, node_m], dag.node_indexes())
self.assertEqual({(node_b, node_c), (node_c, node_m), (node_m, node_b)}, set(dag.edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_contract_nodes.py:91*

### test_multiple_paths_would_cycle

**Category**: workflow  
**Description**: Workflow:     ┌─┐     ┌─┐                  ┌─┐     ┌─┐
 ┌3─┤c│     │e├─5┐            ┌──┤c│     │e├──┐
 │  └▲┘     └▲┘  │            │  └▲┘     └▲┘  │
┌▼┐  2  ┌─┐  4  ┌▼┐           │   2  ┌─┐  4   │
│d│  └──┤b├──┘  │f│   ───►    │   └──┤b├──┘   │
└─┘     └▲┘     └─┘           3      └▲┘      5
         1                    │       1       │
        ┌┴┐                   │      ┌┴┐      │
        │a│                   └─────►│m│◄─────┘
        └─┘                          └─┘  
**Expected**: self.assertEqual({(node_b, node_c), (node_c, node_m), (node_e, node_m), (node_b, node_e), (node_m, node_b)}, set(dag.edge_list()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n            ┌─┐     ┌─┐                  ┌─┐     ┌─┐\n         ┌3─┤c│     │e├─5┐            ┌──┤c│     │e├──┐\n         │  └▲┘     └▲┘  │            │  └▲┘     └▲┘  │\n        ┌▼┐  2  ┌─┐  4  ┌▼┐           │   2  ┌─┐  4   │\n        │d│  └──┤b├──┘  │f│   ───►    │   └──┤b├──┘   │\n        └─┘     └▲┘     └─┘           3      └▲┘      5\n                 1                    │       1       │\n                ┌┴┐                   │      ┌┴┐      │\n                │a│                   └─────►│m│◄─────┘\n                └─┘                          └─┘\n        '
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 1)
node_c = dag.add_child(node_b, 'c', 2)
node_d = dag.add_child(node_c, 'd', 3)
node_e = dag.add_child(node_b, 'e', 4)
node_f = dag.add_child(node_e, 'f', 5)
with self.assertRaises(rustworkx.DAGWouldCycle):
    dag.contract_nodes([node_a, node_d, node_f], 'm', check_cycle=True)
node_m = dag.contract_nodes([node_a, node_d, node_f], 'm')
self.assertEqual([node_b, node_c, node_e, node_m], dag.node_indexes())
self.assertEqual({(node_b, node_c), (node_c, node_m), (node_e, node_m), (node_b, node_e), (node_m, node_b)}, set(dag.edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_contract_nodes.py:122*

### test_keep_edges_multigraph

**Category**: workflow  
**Description**: Workflow:    ┌─┐            ┌─┐
 ┌─┤a│◄┐        ┌─┤a│◄┐
 │ └─┘ │        │ └─┘ │
 1     2   ──►  1     2
┌▼┐   ┌┴┐       │ ┌─┐ │
│b│   │c│       └►│m├─┘
└─┘   └─┘         └─┘  
**Expected**: self.assertEqual({(node_a, node_m, 1), (node_m, node_a, 2)}, set(dag.weighted_edge_list()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n           ┌─┐            ┌─┐\n         ┌─┤a│◄┐        ┌─┤a│◄┐\n         │ └─┘ │        │ └─┘ │\n         1     2   ──►  1     2\n        ┌▼┐   ┌┴┐       │ ┌─┐ │\n        │b│   │c│       └►│m├─┘\n        └─┘   └─┘         └─┘\n        '
dag = rustworkx.PyDiGraph()
node_a = dag.add_node('a')
node_b = dag.add_node('b')
node_c = dag.add_node('c')
dag.add_edge(node_a, node_b, 1)
dag.add_edge(node_c, node_a, 2)
with self.assertRaises(rustworkx.DAGWouldCycle):
    dag.contract_nodes([node_b, node_c], 'm', check_cycle=True)
node_m = dag.contract_nodes([node_b, node_c], 'm')
self.assertEqual([node_a, node_m], dag.node_indexes())
self.assertEqual({(node_a, node_m, 1), (node_m, node_a, 2)}, set(dag.weighted_edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_contract_nodes.py:168*

### test_can_contract_without_cycle_true

**Category**: workflow  
**Description**: Workflow: test can contract without cycle true  
**Expected**: self.assertTrue(graph.can_contract_without_cycle([b, c]))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
a = graph.add_node('a')
b = graph.add_node('b')
c = graph.add_node('c')
graph.add_edge(a, b, 0)
graph.add_edge(b, c, 0)
self.assertTrue(graph.can_contract_without_cycle([b, c]))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_contract_nodes.py:269*

### test_can_contract_without_cycle_false

**Category**: workflow  
**Description**: Workflow: test can contract without cycle false  
**Expected**: self.assertFalse(graph.can_contract_without_cycle([a, c]))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
a = graph.add_node('a')
b = graph.add_node('b')
c = graph.add_node('c')
graph.add_edge(a, b, 0)
graph.add_edge(b, c, 0)
graph.add_edge(c, a, 0)
self.assertFalse(graph.can_contract_without_cycle([a, c]))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_contract_nodes.py:279*

### test_cycle_path_len_gt_1

**Category**: workflow  
**Description**: Workflow:     ┌─┐              ┌─┐
 ┌4─┤a├─1┐           │m├──1───┐
 │  └─┘  │           └▲┘      │
┌▼┐     ┌▼┐           │      ┌▼┐
│d│     │b│   ───►    │      │b│
└▲┘     └┬┘           │      └┬┘
 │  ┌─┐  2            │  ┌─┐  2
 └3─┤c│◄─┘            └3─┤c│◄─┘
    └─┘                  └─┘  
**Expected**: self.assertEqual({(node_b, node_c), (node_c, node_m), (node_m, node_b)}, set(dag.edge_list()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n            ┌─┐              ┌─┐\n         ┌4─┤a├─1┐           │m├──1───┐\n         │  └─┘  │           └▲┘      │\n        ┌▼┐     ┌▼┐           │      ┌▼┐\n        │d│     │b│   ───►    │      │b│\n        └▲┘     └┬┘           │      └┬┘\n         │  ┌─┐  2            │  ┌─┐  2\n         └3─┤c│◄─┘            └3─┤c│◄─┘\n            └─┘                  └─┘\n        '
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 1)
node_c = dag.add_child(node_b, 'c', 2)
node_d = dag.add_child(node_c, 'c', 3)
dag.add_edge(node_a, node_d, 4)
with self.assertRaises(rustworkx.DAGWouldCycle):
    dag.contract_nodes([node_a, node_d], 'm', check_cycle=True)
node_m = dag.contract_nodes([node_a, node_d], 'm')
self.assertEqual([node_b, node_c, node_m], dag.node_indexes())
self.assertEqual({(node_b, node_c), (node_c, node_m), (node_m, node_b)}, set(dag.edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_contract_nodes.py:91*

### test_multiple_paths_would_cycle

**Category**: workflow  
**Description**: Workflow:     ┌─┐     ┌─┐                  ┌─┐     ┌─┐
 ┌3─┤c│     │e├─5┐            ┌──┤c│     │e├──┐
 │  └▲┘     └▲┘  │            │  └▲┘     └▲┘  │
┌▼┐  2  ┌─┐  4  ┌▼┐           │   2  ┌─┐  4   │
│d│  └──┤b├──┘  │f│   ───►    │   └──┤b├──┘   │
└─┘     └▲┘     └─┘           3      └▲┘      5
         1                    │       1       │
        ┌┴┐                   │      ┌┴┐      │
        │a│                   └─────►│m│◄─────┘
        └─┘                          └─┘  
**Expected**: self.assertEqual({(node_b, node_c), (node_c, node_m), (node_e, node_m), (node_b, node_e), (node_m, node_b)}, set(dag.edge_list()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n            ┌─┐     ┌─┐                  ┌─┐     ┌─┐\n         ┌3─┤c│     │e├─5┐            ┌──┤c│     │e├──┐\n         │  └▲┘     └▲┘  │            │  └▲┘     └▲┘  │\n        ┌▼┐  2  ┌─┐  4  ┌▼┐           │   2  ┌─┐  4   │\n        │d│  └──┤b├──┘  │f│   ───►    │   └──┤b├──┘   │\n        └─┘     └▲┘     └─┘           3      └▲┘      5\n                 1                    │       1       │\n                ┌┴┐                   │      ┌┴┐      │\n                │a│                   └─────►│m│◄─────┘\n                └─┘                          └─┘\n        '
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 1)
node_c = dag.add_child(node_b, 'c', 2)
node_d = dag.add_child(node_c, 'd', 3)
node_e = dag.add_child(node_b, 'e', 4)
node_f = dag.add_child(node_e, 'f', 5)
with self.assertRaises(rustworkx.DAGWouldCycle):
    dag.contract_nodes([node_a, node_d, node_f], 'm', check_cycle=True)
node_m = dag.contract_nodes([node_a, node_d, node_f], 'm')
self.assertEqual([node_b, node_c, node_e, node_m], dag.node_indexes())
self.assertEqual({(node_b, node_c), (node_c, node_m), (node_e, node_m), (node_b, node_e), (node_m, node_b)}, set(dag.edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_contract_nodes.py:122*

### test_keep_edges_multigraph

**Category**: workflow  
**Description**: Workflow:    ┌─┐            ┌─┐
 ┌─┤a│◄┐        ┌─┤a│◄┐
 │ └─┘ │        │ └─┘ │
 1     2   ──►  1     2
┌▼┐   ┌┴┐       │ ┌─┐ │
│b│   │c│       └►│m├─┘
└─┘   └─┘         └─┘  
**Expected**: self.assertEqual({(node_a, node_m, 1), (node_m, node_a, 2)}, set(dag.weighted_edge_list()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n           ┌─┐            ┌─┐\n         ┌─┤a│◄┐        ┌─┤a│◄┐\n         │ └─┘ │        │ └─┘ │\n         1     2   ──►  1     2\n        ┌▼┐   ┌┴┐       │ ┌─┐ │\n        │b│   │c│       └►│m├─┘\n        └─┘   └─┘         └─┘\n        '
dag = rustworkx.PyDiGraph()
node_a = dag.add_node('a')
node_b = dag.add_node('b')
node_c = dag.add_node('c')
dag.add_edge(node_a, node_b, 1)
dag.add_edge(node_c, node_a, 2)
with self.assertRaises(rustworkx.DAGWouldCycle):
    dag.contract_nodes([node_b, node_c], 'm', check_cycle=True)
node_m = dag.contract_nodes([node_b, node_c], 'm')
self.assertEqual([node_a, node_m], dag.node_indexes())
self.assertEqual({(node_a, node_m, 1), (node_m, node_a, 2)}, set(dag.weighted_edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_contract_nodes.py:168*

### test_can_contract_without_cycle_true

**Category**: workflow  
**Description**: Workflow: test can contract without cycle true  
**Expected**: self.assertTrue(graph.can_contract_without_cycle([b, c]))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
a = graph.add_node('a')
b = graph.add_node('b')
c = graph.add_node('c')
graph.add_edge(a, b, 0)
graph.add_edge(b, c, 0)
self.assertTrue(graph.can_contract_without_cycle([b, c]))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_contract_nodes.py:269*

### test_can_contract_without_cycle_false

**Category**: workflow  
**Description**: Workflow: test can contract without cycle false  
**Expected**: self.assertFalse(graph.can_contract_without_cycle([a, c]))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
a = graph.add_node('a')
b = graph.add_node('b')
c = graph.add_node('c')
graph.add_edge(a, b, 0)
graph.add_edge(b, c, 0)
graph.add_edge(c, a, 0)
self.assertFalse(graph.can_contract_without_cycle([a, c]))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_contract_nodes.py:279*

### test_cycle_no_source

**Category**: workflow  
**Description**: Workflow: test cycle no source  
**Expected**: self.assertTrue(res[0] == res[1][::-1])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.add_nodes_from(list(range(10)))
self.graph.add_edges_from_no_data([(0, 1), (3, 0), (0, 5), (8, 0), (1, 2), (1, 6), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9)])

g = rustworkx.generators.directed_path_graph(1000)
a = g.add_node(1000)
b = g.node_indices()[-2]
g.add_edge(b, a, None)
g.add_edge(a, b, None)
res = rustworkx.digraph_find_cycle(g)
self.assertEqual(len(res), 2)
self.assertTrue(res[0] == res[1][::-1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_find_cycle.py:88*

### test_cycle_self_loop

**Category**: workflow  
**Description**: Workflow: test cycle self loop  
**Expected**: self.assertEqual(res, [(a, a)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.add_nodes_from(list(range(10)))
self.graph.add_edges_from_no_data([(0, 1), (3, 0), (0, 5), (8, 0), (1, 2), (1, 6), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9)])

g = rustworkx.generators.directed_path_graph(1000)
a = g.add_node(1000)
b = g.node_indices()[-1]
g.add_edge(b, a, None)
g.add_edge(a, a, None)
res = rustworkx.digraph_find_cycle(g)
self.assertEqual(res, [(a, a)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_find_cycle.py:98*

### test_cycle_no_source

**Category**: workflow  
**Description**: Workflow: test cycle no source  
**Expected**: self.assertTrue(res[0] == res[1][::-1])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.generators.directed_path_graph(1000)
a = g.add_node(1000)
b = g.node_indices()[-2]
g.add_edge(b, a, None)
g.add_edge(a, b, None)
res = rustworkx.digraph_find_cycle(g)
self.assertEqual(len(res), 2)
self.assertTrue(res[0] == res[1][::-1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_find_cycle.py:88*

### test_cycle_self_loop

**Category**: workflow  
**Description**: Workflow: test cycle self loop  
**Expected**: self.assertEqual(res, [(a, a)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.generators.directed_path_graph(1000)
a = g.add_node(1000)
b = g.node_indices()[-1]
g.add_edge(b, a, None)
g.add_edge(a, a, None)
res = rustworkx.digraph_find_cycle(g)
self.assertEqual(res, [(a, a)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_find_cycle.py:98*

### test_graph_dijkstra_tree_edges

**Category**: workflow  
**Description**: Workflow: test graph dijkstra tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

class DijkstraTreeEdgesRecorder(rustworkx.visit.DijkstraVisitor):

    def __init__(self):
        self.edges = []
        self.parents = dict()

    def discover_vertex(self, v, _):
        u = self.parents.get(v, None)
        if u is not None:
            self.edges.append((u, v))

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u
vis = DijkstraTreeEdgesRecorder()
rustworkx.graph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra_search.py:34*

### test_graph_dijkstra_tree_edges_no_starting_point

**Category**: workflow  
**Description**: Workflow: test graph dijkstra tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3), (4, 7)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

class DijkstraTreeEdgesRecorder(rustworkx.visit.DijkstraVisitor):

    def __init__(self):
        self.edges = []
        self.parents = dict()

    def discover_vertex(self, v, _):
        u = self.parents.get(v, None)
        if u is not None:
            self.edges.append((u, v))

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u
vis = DijkstraTreeEdgesRecorder()
rustworkx.graph_dijkstra_search(self.graph, None, float, vis)
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra_search.py:53*

### test_graph_dijkstra_goal_search_with_stop_search_exception

**Category**: workflow  
**Description**: Workflow: test graph dijkstra goal search with stop search exception  
**Expected**: self.assertEqual(vis.opt_goal_cost, 4.0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

class GoalSearch(rustworkx.visit.DijkstraVisitor):
    goal = 3

    def __init__(self):
        self.parents = {}
        self.opt_goal_cost = None

    def discover_vertex(self, v, score):
        if v == self.goal:
            self.opt_goal_cost = score
            raise rustworkx.visit.StopSearch

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u

    def reconstruct_path(self):
        v = self.goal
        path = [v]
        while v in self.parents:
            v = self.parents[v]
            path.append(v)
        path.reverse()
        return path
vis = GoalSearch()
rustworkx.graph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.reconstruct_path(), [0, 2, 5, 3])
self.assertEqual(vis.opt_goal_cost, 4.0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra_search.py:72*

### test_graph_dijkstra_tree_edges

**Category**: workflow  
**Description**: Workflow: test graph dijkstra tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
class DijkstraTreeEdgesRecorder(rustworkx.visit.DijkstraVisitor):

    def __init__(self):
        self.edges = []
        self.parents = dict()

    def discover_vertex(self, v, _):
        u = self.parents.get(v, None)
        if u is not None:
            self.edges.append((u, v))

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u
vis = DijkstraTreeEdgesRecorder()
rustworkx.graph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra_search.py:34*

### test_graph_dijkstra_tree_edges_no_starting_point

**Category**: workflow  
**Description**: Workflow: test graph dijkstra tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3), (4, 7)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
class DijkstraTreeEdgesRecorder(rustworkx.visit.DijkstraVisitor):

    def __init__(self):
        self.edges = []
        self.parents = dict()

    def discover_vertex(self, v, _):
        u = self.parents.get(v, None)
        if u is not None:
            self.edges.append((u, v))

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u
vis = DijkstraTreeEdgesRecorder()
rustworkx.graph_dijkstra_search(self.graph, None, float, vis)
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra_search.py:53*

### test_graph_dijkstra_goal_search_with_stop_search_exception

**Category**: workflow  
**Description**: Workflow: test graph dijkstra goal search with stop search exception  
**Expected**: self.assertEqual(vis.opt_goal_cost, 4.0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
class GoalSearch(rustworkx.visit.DijkstraVisitor):
    goal = 3

    def __init__(self):
        self.parents = {}
        self.opt_goal_cost = None

    def discover_vertex(self, v, score):
        if v == self.goal:
            self.opt_goal_cost = score
            raise rustworkx.visit.StopSearch

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u

    def reconstruct_path(self):
        v = self.goal
        path = [v]
        while v in self.parents:
            v = self.parents[v]
            path.append(v)
        path.reverse()
        return path
vis = GoalSearch()
rustworkx.graph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.reconstruct_path(), [0, 2, 5, 3])
self.assertEqual(vis.opt_goal_cost, 4.0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra_search.py:72*

### test_num_shortest_path_unweighted

**Category**: workflow  
**Description**: Workflow: test num shortest path unweighted  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
node_a = graph.add_node(0)
node_b = graph.add_node('end')
for i in range(3):
    node = graph.add_child(node_a, i, None)
    graph.add_edge(node, node_b, None)
res = rustworkx.digraph_num_shortest_paths_unweighted(graph, node_a)
expected = {2: 1, 4: 1, 3: 1, 1: 3}
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_num_shortest_path.py:19*

### test_node_with_no_path

**Category**: workflow  
**Description**: Workflow: test node with no path  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_path_graph(5)
graph.extend_from_edge_list([(6, 7), (7, 8), (8, 9), (9, 10), (10, 11)])
expected = {1: 1, 2: 1, 3: 1, 4: 1}
res = rustworkx.num_shortest_paths_unweighted(graph, 0)
self.assertEqual(expected, res)
res = rustworkx.num_shortest_paths_unweighted(graph, 6)
expected = {7: 1, 8: 1, 9: 1, 10: 1, 11: 1}
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_num_shortest_path.py:98*

### test_num_shortest_path_unweighted

**Category**: workflow  
**Description**: Workflow: test num shortest path unweighted  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
node_a = graph.add_node(0)
node_b = graph.add_node('end')
for i in range(3):
    node = graph.add_child(node_a, i, None)
    graph.add_edge(node, node_b, None)
res = rustworkx.digraph_num_shortest_paths_unweighted(graph, node_a)
expected = {2: 1, 4: 1, 3: 1, 1: 3}
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_num_shortest_path.py:19*

### test_node_with_no_path

**Category**: workflow  
**Description**: Workflow: test node with no path  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_path_graph(5)
graph.extend_from_edge_list([(6, 7), (7, 8), (8, 9), (9, 10), (10, 11)])
expected = {1: 1, 2: 1, 3: 1, 4: 1}
res = rustworkx.num_shortest_paths_unweighted(graph, 0)
self.assertEqual(expected, res)
res = rustworkx.num_shortest_paths_unweighted(graph, 6)
expected = {7: 1, 8: 1, 9: 1, 10: 1, 11: 1}
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_num_shortest_path.py:98*

### test_hexagonal_graph_periodic_subgraphs

**Category**: workflow  
**Description**: Workflow: Check that hexagonal subgraphs of the lattice are isomorphic
to C6 (idea copied from the networkx test suite).  
**Expected**: self.assertEqual(len(subGraph.edges()), 7)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Check that hexagonal subgraphs of the lattice are isomorphic\n        to C6 (idea copied from the networkx test suite).'
graph = rustworkx.generators.hexagonal_lattice_graph(2, 4, periodic=True)
hexagons = [[0, 1, 2, 6, 5, 4], [2, 3, 0, 4, 7, 6], [5, 6, 7, 11, 10, 9]]
C6 = rustworkx.generators.cycle_graph(6)
for h in hexagons:
    self.assertTrue(rustworkx.is_isomorphic(graph.subgraph(h), C6))
graph2cols = rustworkx.generators.hexagonal_lattice_graph(2, 2, periodic=True)
subGraph = graph2cols.subgraph(hexagons[0])
self.assertFalse(rustworkx.is_isomorphic(subGraph, C6))
self.assertEqual(len(subGraph.edges()), 7)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_hexagonal.py:423*

### test_hexagonal_graph_with_positions

**Category**: workflow  
**Description**: Workflow: test hexagonal graph with positions  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.hexagonal_lattice_graph(2, 2, with_positions=True)
positions = graph.nodes()
hexagons = [[0, 1, 2, 7, 6, 5], [2, 3, 4, 9, 8, 7], [6, 7, 8, 13, 12, 11], [8, 9, 10, 15, 14, 13]]
C6 = rustworkx.generators.cycle_graph(6)
for h in hexagons:
    self.assertTrue(rustworkx.is_isomorphic(graph.subgraph(h), C6))
    coordinates = np.array([positions[node] for node in h])
    vectors = [coordinates[(ii + 1) % 6] - coordinates[ii] for ii in range(6)]
    for v in vectors:
        self.assertAlmostEqual(np.linalg.norm(v), 1.0, 12)
    for ii in range(6):
        self.assertAlmostEqual(np.dot(vectors[ii], vectors[(ii + 1) % 6]), np.cos(np.pi / 3), 12)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_hexagonal.py:588*

### test_hexagonal_graph_with_positions_odd_number_of_columns

**Category**: workflow  
**Description**: Workflow: test hexagonal graph with positions odd number of columns  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.hexagonal_lattice_graph(2, 3, with_positions=True)
positions = graph.nodes()
hexagons = [[0, 1, 2, 7, 6, 5], [2, 3, 4, 9, 8, 7], [6, 7, 8, 14, 13, 12], [8, 9, 10, 16, 15, 14], [11, 12, 13, 19, 18, 17], [13, 14, 15, 21, 20, 19]]
C6 = rustworkx.generators.cycle_graph(6)
for h in hexagons:
    self.assertTrue(rustworkx.is_isomorphic(graph.subgraph(h), C6))
    coordinates = np.array([positions[node] for node in h])
    vectors = [coordinates[(ii + 1) % 6] - coordinates[ii] for ii in range(6)]
    for v in vectors:
        self.assertAlmostEqual(np.linalg.norm(v), 1.0, 12)
    for ii in range(6):
        self.assertAlmostEqual(np.dot(vectors[ii], vectors[(ii + 1) % 6]), np.cos(np.pi / 3), 12)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_hexagonal.py:612*

### test_hexagonal_graph_periodic_subgraphs

**Category**: workflow  
**Description**: Workflow: Check that hexagonal subgraphs of the lattice are isomorphic
to C6 (idea copied from the networkx test suite).  
**Expected**: self.assertEqual(len(subGraph.edges()), 7)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Check that hexagonal subgraphs of the lattice are isomorphic\n        to C6 (idea copied from the networkx test suite).'
graph = rustworkx.generators.hexagonal_lattice_graph(2, 4, periodic=True)
hexagons = [[0, 1, 2, 6, 5, 4], [2, 3, 0, 4, 7, 6], [5, 6, 7, 11, 10, 9]]
C6 = rustworkx.generators.cycle_graph(6)
for h in hexagons:
    self.assertTrue(rustworkx.is_isomorphic(graph.subgraph(h), C6))
graph2cols = rustworkx.generators.hexagonal_lattice_graph(2, 2, periodic=True)
subGraph = graph2cols.subgraph(hexagons[0])
self.assertFalse(rustworkx.is_isomorphic(subGraph, C6))
self.assertEqual(len(subGraph.edges()), 7)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_hexagonal.py:423*

### test_hexagonal_graph_with_positions

**Category**: workflow  
**Description**: Workflow: test hexagonal graph with positions  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.hexagonal_lattice_graph(2, 2, with_positions=True)
positions = graph.nodes()
hexagons = [[0, 1, 2, 7, 6, 5], [2, 3, 4, 9, 8, 7], [6, 7, 8, 13, 12, 11], [8, 9, 10, 15, 14, 13]]
C6 = rustworkx.generators.cycle_graph(6)
for h in hexagons:
    self.assertTrue(rustworkx.is_isomorphic(graph.subgraph(h), C6))
    coordinates = np.array([positions[node] for node in h])
    vectors = [coordinates[(ii + 1) % 6] - coordinates[ii] for ii in range(6)]
    for v in vectors:
        self.assertAlmostEqual(np.linalg.norm(v), 1.0, 12)
    for ii in range(6):
        self.assertAlmostEqual(np.dot(vectors[ii], vectors[(ii + 1) % 6]), np.cos(np.pi / 3), 12)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_hexagonal.py:588*

### test_hexagonal_graph_with_positions_odd_number_of_columns

**Category**: workflow  
**Description**: Workflow: test hexagonal graph with positions odd number of columns  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.hexagonal_lattice_graph(2, 3, with_positions=True)
positions = graph.nodes()
hexagons = [[0, 1, 2, 7, 6, 5], [2, 3, 4, 9, 8, 7], [6, 7, 8, 14, 13, 12], [8, 9, 10, 16, 15, 14], [11, 12, 13, 19, 18, 17], [13, 14, 15, 21, 20, 19]]
C6 = rustworkx.generators.cycle_graph(6)
for h in hexagons:
    self.assertTrue(rustworkx.is_isomorphic(graph.subgraph(h), C6))
    coordinates = np.array([positions[node] for node in h])
    vectors = [coordinates[(ii + 1) % 6] - coordinates[ii] for ii in range(6)]
    for v in vectors:
        self.assertAlmostEqual(np.linalg.norm(v), 1.0, 12)
    for ii in range(6):
        self.assertAlmostEqual(np.dot(vectors[ii], vectors[(ii + 1) % 6]), np.cos(np.pi / 3), 12)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_hexagonal.py:612*

### test_simple_graph_composition

**Category**: workflow  
**Description**: Workflow: test simple graph composition  
**Expected**: self.assertEqual([0, 1, 2, 3, 4], graph.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, {'a': 2})
graph_other = rustworkx.PyGraph()
node_d = graph_other.add_node('d')
node_e = graph_other.add_node('e')
graph_other.add_edge(node_d, node_e, {'a': 3})
res = graph.compose(graph_other, {node_c: (node_d, {'b': 1})})
self.assertEqual({0: 3, 1: 4}, res)
self.assertEqual([0, 1, 2, 3, 4], graph.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_compose.py:19*

### test_simple_graph_composition

**Category**: workflow  
**Description**: Workflow: test simple graph composition  
**Expected**: self.assertEqual([0, 1, 2, 3, 4], graph.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, {'a': 2})
graph_other = rustworkx.PyGraph()
node_d = graph_other.add_node('d')
node_e = graph_other.add_node('e')
graph_other.add_edge(node_d, node_e, {'a': 3})
res = graph.compose(graph_other, {node_c: (node_d, {'b': 1})})
self.assertEqual({0: 3, 1: 4}, res)
self.assertEqual([0, 1, 2, 3, 4], graph.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_compose.py:19*

### test_subgraph_isomorphic_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['b_1', 'b_2', 'b_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'b_1'), (nodes[1], nodes[2], 'b_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_subgraph_isomorphic(g_a, g_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph_isomorphic.py:51*

### test_subgraph_isomorphic_compare_nodes_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic compare nodes mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['b_1', 'b_2', 'b_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'b_1'), (nodes[1], nodes[2], 'b_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertFalse(rustworkx.is_subgraph_isomorphic(g_a, g_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph_isomorphic.py:70*

### test_subgraph_isomorphic_compare_nodes_identical

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic compare nodes identical  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_subgraph_isomorphic(g_a, g_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph_isomorphic.py:93*

### test_subgraph_isomorphic_compare_edges_identical

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic compare edges identical  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_subgraph_isomorphic(g_a, g_b, edge_matcher=lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph_isomorphic.py:130*

### test_subgraph_isomorphic_node_count_not_ge

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic node count not ge  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1')])
nodes = g_b.add_nodes_from(['a_0', 'a_1', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertFalse(rustworkx.is_subgraph_isomorphic(g_a, g_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph_isomorphic.py:156*

### test_non_induced_subgraph_isomorphic

**Category**: workflow  
**Description**: Workflow: test non induced subgraph isomorphic  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[2], nodes[0], 'a_3')])
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order, induced=True):
        self.assertFalse(rustworkx.is_subgraph_isomorphic(g_a, g_b, id_order=id_order, induced=True))
    with self.subTest(id_order=id_order, induced=False):
        self.assertTrue(rustworkx.is_subgraph_isomorphic(g_a, g_b, id_order=id_order, induced=False))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph_isomorphic.py:169*

### test_vf2pp_remapping

**Category**: workflow  
**Description**: Workflow: test vf2pp remapping  
**Expected**: self.assertEqual(next(mapping), {5: 0, 4: 2, 1: 3, 2: 1})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
temp = rustworkx.generators.grid_graph(3, 3)
graph = rustworkx.PyGraph()
dummy = graph.add_node(0)
graph.compose(temp, dict())
graph.remove_node(dummy)
second_graph = rustworkx.generators.grid_graph(2, 2)
mapping = rustworkx.graph_vf2_mapping(graph, second_graph, subgraph=True, id_order=False)
self.assertEqual(next(mapping), {5: 0, 4: 2, 1: 3, 2: 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph_isomorphic.py:265*

### test_subgraph_isomorphic_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['b_1', 'b_2', 'b_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'b_1'), (nodes[1], nodes[2], 'b_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_subgraph_isomorphic(g_a, g_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph_isomorphic.py:51*

### test_subgraph_isomorphic_compare_nodes_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic compare nodes mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['b_1', 'b_2', 'b_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'b_1'), (nodes[1], nodes[2], 'b_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertFalse(rustworkx.is_subgraph_isomorphic(g_a, g_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph_isomorphic.py:70*

### test_subgraph_isomorphic_compare_nodes_identical

**Category**: workflow  
**Description**: Workflow: test subgraph isomorphic compare nodes identical  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[0], nodes[3], 'a_3')])
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_subgraph_isomorphic(g_a, g_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph_isomorphic.py:93*

### test_digraph_bfs_tree_edges_restricted

**Category**: workflow  
**Description**: Workflow: test digraph bfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (1, 3)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

class TreeEdgesRecorderRestricted(rustworkx.visit.BFSVisitor):
    prohibited = [(0, 2), (1, 2)]

    def __init__(self):
        self.edges = []

    def tree_edge(self, edge):
        edge = (edge[0], edge[1])
        if edge in self.prohibited:
            raise rustworkx.visit.PruneSearch
        self.edges.append(edge)
vis = TreeEdgesRecorderRestricted()
rustworkx.digraph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 1), (1, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_search.py:58*

### test_digraph_bfs_goal_search_with_stop_search_exception

**Category**: workflow  
**Description**: Workflow: test digraph bfs goal search with stop search exception  
**Expected**: self.assertEqual(vis.reconstruct_path(), [0, 1, 3])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

class GoalSearch(rustworkx.visit.BFSVisitor):
    goal = 3

    def __init__(self):
        self.parents = {}

    def tree_edge(self, edge):
        u, v, _ = edge
        self.parents[v] = u
        if v == self.goal:
            raise rustworkx.visit.StopSearch

    def reconstruct_path(self):
        v = self.goal
        path = [v]
        while v in self.parents:
            v = self.parents[v]
            path.append(v)
        path.reverse()
        return path
vis = GoalSearch()
rustworkx.digraph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.reconstruct_path(), [0, 1, 3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_search.py:75*

### test_digraph_bfs_tree_edges_restricted

**Category**: workflow  
**Description**: Workflow: test digraph bfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (1, 3)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
class TreeEdgesRecorderRestricted(rustworkx.visit.BFSVisitor):
    prohibited = [(0, 2), (1, 2)]

    def __init__(self):
        self.edges = []

    def tree_edge(self, edge):
        edge = (edge[0], edge[1])
        if edge in self.prohibited:
            raise rustworkx.visit.PruneSearch
        self.edges.append(edge)
vis = TreeEdgesRecorderRestricted()
rustworkx.digraph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 1), (1, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_search.py:58*

### test_digraph_bfs_goal_search_with_stop_search_exception

**Category**: workflow  
**Description**: Workflow: test digraph bfs goal search with stop search exception  
**Expected**: self.assertEqual(vis.reconstruct_path(), [0, 1, 3])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
class GoalSearch(rustworkx.visit.BFSVisitor):
    goal = 3

    def __init__(self):
        self.parents = {}

    def tree_edge(self, edge):
        u, v, _ = edge
        self.parents[v] = u
        if v == self.goal:
            raise rustworkx.visit.StopSearch

    def reconstruct_path(self):
        v = self.goal
        path = [v]
        while v in self.parents:
            v = self.parents[v]
            path.append(v)
        path.reverse()
        return path
vis = GoalSearch()
rustworkx.digraph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.reconstruct_path(), [0, 1, 3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_search.py:75*

### test_random_gnp_directed_complete_graph

**Category**: workflow  
**Description**: Workflow: test random gnp directed complete graph  
**Expected**: self.assertEqual(len(graph.edges()), 20 * (20 - 1))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.directed_gnp_random_graph(20, 1)
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 20 * (20 - 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_random.py:42*

### test_random_gnp_undirected_complete_graph

**Category**: workflow  
**Description**: Workflow: test random gnp undirected complete graph  
**Expected**: self.assertEqual(len(graph.edges()), 20 * (20 - 1) / 2)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.undirected_gnp_random_graph(20, 1)
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 20 * (20 - 1) / 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_random.py:69*

### test_random_gnm_directed_complete_graph

**Category**: workflow  
**Description**: Workflow: test random gnm directed complete graph  
**Expected**: self.assertEqual(len(graph.edges()), max_m)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
n = 20
max_m = n * (n - 1)
graph = rustworkx.directed_gnm_random_graph(n, max_m)
self.assertEqual(len(graph), n)
self.assertEqual(len(graph.edges()), max_m)
graph = rustworkx.directed_gnm_random_graph(n, max_m + 1)
self.assertEqual(len(graph), n)
self.assertEqual(len(graph.edges()), max_m)
graph = rustworkx.directed_gnm_random_graph(n, max_m, 55)
self.assertEqual(len(graph), n)
self.assertEqual(len(graph.edges()), max_m)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_random.py:106*

### test_random_gnm_undirected_complete_graph

**Category**: workflow  
**Description**: Workflow: test random gnm undirected complete graph  
**Expected**: self.assertEqual(len(graph.edges()), max_m)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
n = 20
max_m = n * (n - 1) // 2
graph = rustworkx.undirected_gnm_random_graph(n, max_m)
self.assertEqual(len(graph), n)
self.assertEqual(len(graph.edges()), max_m)
graph = rustworkx.undirected_gnm_random_graph(n, max_m + 1)
self.assertEqual(len(graph), n)
self.assertEqual(len(graph.edges()), max_m)
graph = rustworkx.undirected_gnm_random_graph(n, max_m, 55)
self.assertEqual(len(graph), n)
self.assertEqual(len(graph.edges()), max_m)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_random.py:152*

### test_undirected_sbm_complete_blocks_loops

**Category**: workflow  
**Description**: Workflow: test undirected sbm complete blocks loops  
**Expected**: self.assertFalse(graph.has_edge(2, 2))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.undirected_sbm_random_graph([2, 1], np.array([[1, 1], [1, 0]], dtype=float), True)
self.assertEqual(len(graph), 3)
self.assertEqual(len(graph.edges()), 5)
for i in range(2):
    for j in range(i, 2):
        if (i, j) != (2, 2):
            self.assertTrue(graph.has_edge(i, j))
self.assertFalse(graph.has_edge(2, 2))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_random.py:182*

### test_directed_sbm_complete_blocks_loops

**Category**: workflow  
**Description**: Workflow: test directed sbm complete blocks loops  
**Expected**: self.assertEqual(set(graph.edge_list()), set([(2, 2), (2, 0), (2, 1)]))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.directed_sbm_random_graph([2, 1], np.array([[0, 0], [1, 1]], dtype=float), True)
self.assertEqual(len(graph), 3)
self.assertEqual(len(graph.edges()), 3)
self.assertEqual(set(graph.edge_list()), set([(2, 2), (2, 0), (2, 1)]))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_random.py:194*

### test_undirected_sbm_complete_blocks_noloops

**Category**: workflow  
**Description**: Workflow: test undirected sbm complete blocks noloops  
**Expected**: self.assertEqual(len(graph.edges()), 3)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.undirected_sbm_random_graph([2, 1], np.array([[1, 1], [1, 0]], dtype=float), False)
self.assertEqual(len(graph), 3)
self.assertEqual(len(graph.edges()), 3)
for i in range(2):
    for j in range(i, 2):
        if i != j:
            self.assertTrue(graph.has_edge(i, j))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_random.py:202*

### test_directed_sbm_complete_blocks_noloops

**Category**: workflow  
**Description**: Workflow: test directed sbm complete blocks noloops  
**Expected**: self.assertEqual(set(graph.edge_list()), set([(2, 0), (2, 1)]))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.directed_sbm_random_graph([2, 1], np.array([[0, 0], [1, 1]], dtype=float), False)
self.assertEqual(len(graph), 3)
self.assertEqual(len(graph.edges()), 2)
self.assertEqual(set(graph.edge_list()), set([(2, 0), (2, 1)]))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_random.py:213*

### test_random_geometric_complete

**Category**: workflow  
**Description**: Workflow: test random geometric complete  
**Expected**: self.assertEqual(len(graph.edges()), 45)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
r = 1.42
graph = rustworkx.random_geometric_graph(10, r)
self.assertEqual(len(graph), 10)
self.assertEqual(len(graph.edges()), 45)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_random.py:268*

### test_random_gnm_non_induced_subgraph_isomorphism

**Category**: workflow  
**Description**: Workflow: test random gnm non induced subgraph isomorphism  
**Expected**: self.assertTrue(rustworkx.is_subgraph_isomorphic(graph, subgraph, id_order=True, induced=False))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.undirected_gnm_random_graph(50, 150)
nodes = random.sample(range(50), 25)
subgraph = graph.subgraph(nodes)
indexes = list(subgraph.edge_indices())
for idx in random.sample(indexes, len(indexes) // 2):
    subgraph.remove_edge_from_index(idx)
self.assertTrue(rustworkx.is_subgraph_isomorphic(graph, subgraph, id_order=True, induced=False))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_random.py:370*

### test_subgraph_with_nodemap_edge_cases

**Category**: workflow  
**Description**: Workflow: test subgraph with nodemap edge cases  
**Expected**: self.assertEqual(dict(node_map), {0: 0, 1: 1, 2: 2})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
graph.add_nodes_from(['a', 'b', 'c'])
graph.add_edges_from([(0, 1, 1), (1, 2, 2)])
subgraph, node_map = graph.subgraph_with_nodemap([])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
self.assertEqual(dict(node_map), {})
subgraph, node_map = graph.subgraph_with_nodemap([42, 100])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
self.assertEqual(dict(node_map), {})
subgraph, node_map = graph.subgraph_with_nodemap([1])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(['b'], subgraph.nodes())
self.assertEqual(dict(node_map), {0: 1})
subgraph, node_map = graph.subgraph_with_nodemap([0, 1, 2])
self.assertEqual([(0, 1, 1), (1, 2, 2)], subgraph.weighted_edge_list())
self.assertEqual(['a', 'b', 'c'], subgraph.nodes())
self.assertEqual(dict(node_map), {0: 0, 1: 1, 2: 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph.py:169*

### test_subgraph_with_nodemap_edge_cases

**Category**: workflow  
**Description**: Workflow: test subgraph with nodemap edge cases  
**Expected**: self.assertEqual(dict(node_map), {0: 0, 1: 1, 2: 2})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
graph.add_nodes_from(['a', 'b', 'c'])
graph.add_edges_from([(0, 1, 1), (1, 2, 2)])
subgraph, node_map = graph.subgraph_with_nodemap([])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
self.assertEqual(dict(node_map), {})
subgraph, node_map = graph.subgraph_with_nodemap([42, 100])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
self.assertEqual(dict(node_map), {})
subgraph, node_map = graph.subgraph_with_nodemap([1])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(['b'], subgraph.nodes())
self.assertEqual(dict(node_map), {0: 1})
subgraph, node_map = graph.subgraph_with_nodemap([0, 1, 2])
self.assertEqual([(0, 1, 1), (1, 2, 2)], subgraph.weighted_edge_list())
self.assertEqual(['a', 'b', 'c'], subgraph.nodes())
self.assertEqual(dict(node_map), {0: 0, 1: 1, 2: 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph.py:169*

### test_metric_closure

**Category**: workflow  
**Description**: Workflow: test metric closure  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph(multigraph=False)
self.graph.add_node(None)
self.graph.extend_from_weighted_edge_list([(1, 2, 10), (2, 3, 10), (3, 4, 10), (4, 5, 10), (5, 6, 10), (2, 7, 1), (7, 5, 1)])
self.graph.remove_node(0)

closure_graph = rustworkx.metric_closure(self.graph, weight_fn=float)
expected_edges = [(1, 2, (10.0, [1, 2])), (1, 3, (20.0, [1, 2, 3])), (1, 4, (22.0, [1, 2, 7, 5, 4])), (1, 5, (12.0, [1, 2, 7, 5])), (1, 6, (22.0, [1, 2, 7, 5, 6])), (1, 7, (11.0, [1, 2, 7])), (2, 3, (10.0, [2, 3])), (2, 4, (12.0, [2, 7, 5, 4])), (2, 5, (2.0, [2, 7, 5])), (2, 6, (12, [2, 7, 5, 6])), (2, 7, (1.0, [2, 7])), (3, 4, (10.0, [3, 4])), (3, 5, (12.0, [3, 2, 7, 5])), (3, 6, (22.0, [3, 2, 7, 5, 6])), (3, 7, (11.0, [3, 2, 7])), (4, 5, (10.0, [4, 5])), (4, 6, (20.0, [4, 5, 6])), (4, 7, (11.0, [4, 5, 7])), (5, 6, (10.0, [5, 6])), (5, 7, (1.0, [5, 7])), (6, 7, (11.0, [6, 5, 7]))]
edges = list(closure_graph.weighted_edge_list())
for edge in expected_edges:
    found = False
    if edge in edges:
        found = True
    if not found:
        if (edge[1], edge[0], (edge[2][0], list(reversed(edge[2][1])))) in edges:
            found = True
    if not found:
        self.fail(f'edge: {edge} nor its reverse not found in metric closure output:\n{pprint.pformat(edges)}')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_steiner_tree.py:36*

### test_steiner_graph_multigraph

**Category**: workflow  
**Description**: Workflow: test steiner graph multigraph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph(multigraph=False)
self.graph.add_node(None)
self.graph.extend_from_weighted_edge_list([(1, 2, 10), (2, 3, 10), (3, 4, 10), (4, 5, 10), (5, 6, 10), (2, 7, 1), (7, 5, 1)])
self.graph.remove_node(0)

edge_list = [(1, 2, 1), (2, 3, 999), (2, 3, 1), (3, 4, 1), (3, 5, 1)]
graph = rustworkx.PyGraph()
graph.extend_from_weighted_edge_list(edge_list)
graph.remove_node(0)
terminal_nodes = [2, 4, 5]
tree = rustworkx.steiner_tree(graph, terminal_nodes, weight_fn=float)
expected_edges = [(2, 3, 1), (3, 4, 1), (3, 5, 1)]
steiner_tree_edge_list = tree.weighted_edge_list()
for edge in expected_edges:
    self.assertIn(edge, steiner_tree_edge_list)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_steiner_tree.py:128*

### test_equal_distance_graph

**Category**: workflow  
**Description**: Workflow: test equal distance graph  
**Expected**: self.assertEqual(tree.weighted_edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph(multigraph=False)
self.graph.add_node(None)
self.graph.extend_from_weighted_edge_list([(1, 2, 10), (2, 3, 10), (3, 4, 10), (4, 5, 10), (5, 6, 10), (2, 7, 1), (7, 5, 1)])
self.graph.remove_node(0)

n = 3
graph = rustworkx.PyGraph()
graph.add_nodes_from(range(n + 5))
graph.add_edges_from([(n, n + 1, 0.5), (n, n + 2, 0.5), (n + 1, n + 2, 0.5), (n, n + 3, 0.5), (n + 1, n + 4, 0.5)])
graph.add_edges_from([(i, n + 2, 2) for i in range(n)])
terminals = list(range(5)) + [n + 3, n + 4]
tree = rustworkx.steiner_tree(graph, terminals, weight_fn=float)
self.assertEqual(rustworkx.cycle_basis(tree), [])
expected_edges = [(3, 4, 0.5), (4, 5, 0.5), (3, 6, 0.5), (4, 7, 0.5), (0, 5, 2), (1, 5, 2), (2, 5, 2)]
self.assertEqual(tree.weighted_edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_steiner_tree.py:160*

### test_metric_closure

**Category**: workflow  
**Description**: Workflow: test metric closure  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
closure_graph = rustworkx.metric_closure(self.graph, weight_fn=float)
expected_edges = [(1, 2, (10.0, [1, 2])), (1, 3, (20.0, [1, 2, 3])), (1, 4, (22.0, [1, 2, 7, 5, 4])), (1, 5, (12.0, [1, 2, 7, 5])), (1, 6, (22.0, [1, 2, 7, 5, 6])), (1, 7, (11.0, [1, 2, 7])), (2, 3, (10.0, [2, 3])), (2, 4, (12.0, [2, 7, 5, 4])), (2, 5, (2.0, [2, 7, 5])), (2, 6, (12, [2, 7, 5, 6])), (2, 7, (1.0, [2, 7])), (3, 4, (10.0, [3, 4])), (3, 5, (12.0, [3, 2, 7, 5])), (3, 6, (22.0, [3, 2, 7, 5, 6])), (3, 7, (11.0, [3, 2, 7])), (4, 5, (10.0, [4, 5])), (4, 6, (20.0, [4, 5, 6])), (4, 7, (11.0, [4, 5, 7])), (5, 6, (10.0, [5, 6])), (5, 7, (1.0, [5, 7])), (6, 7, (11.0, [6, 5, 7]))]
edges = list(closure_graph.weighted_edge_list())
for edge in expected_edges:
    found = False
    if edge in edges:
        found = True
    if not found:
        if (edge[1], edge[0], (edge[2][0], list(reversed(edge[2][1])))) in edges:
            found = True
    if not found:
        self.fail(f'edge: {edge} nor its reverse not found in metric closure output:\n{pprint.pformat(edges)}')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_steiner_tree.py:36*

### test_steiner_graph_multigraph

**Category**: workflow  
**Description**: Workflow: test steiner graph multigraph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
edge_list = [(1, 2, 1), (2, 3, 999), (2, 3, 1), (3, 4, 1), (3, 5, 1)]
graph = rustworkx.PyGraph()
graph.extend_from_weighted_edge_list(edge_list)
graph.remove_node(0)
terminal_nodes = [2, 4, 5]
tree = rustworkx.steiner_tree(graph, terminal_nodes, weight_fn=float)
expected_edges = [(2, 3, 1), (3, 4, 1), (3, 5, 1)]
steiner_tree_edge_list = tree.weighted_edge_list()
for edge in expected_edges:
    self.assertIn(edge, steiner_tree_edge_list)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_steiner_tree.py:128*

### test_equal_distance_graph

**Category**: workflow  
**Description**: Workflow: test equal distance graph  
**Expected**: self.assertEqual(tree.weighted_edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
n = 3
graph = rustworkx.PyGraph()
graph.add_nodes_from(range(n + 5))
graph.add_edges_from([(n, n + 1, 0.5), (n, n + 2, 0.5), (n + 1, n + 2, 0.5), (n, n + 3, 0.5), (n + 1, n + 4, 0.5)])
graph.add_edges_from([(i, n + 2, 2) for i in range(n)])
terminals = list(range(5)) + [n + 3, n + 4]
tree = rustworkx.steiner_tree(graph, terminals, weight_fn=float)
self.assertEqual(rustworkx.cycle_basis(tree), [])
expected_edges = [(3, 4, 0.5), (4, 5, 0.5), (3, 6, 0.5), (4, 7, 0.5), (0, 5, 2), (1, 5, 2), (2, 5, 2)]
self.assertEqual(tree.weighted_edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_steiner_tree.py:160*

### test_multiple_mapping

**Category**: workflow  
**Description**: Workflow: test multiple mapping  
**Expected**: self.assertEqual(sorted(expected), sorted(graph.edge_list()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.path_graph(5)

graph = rustworkx.generators.star_graph(5)
in_graph = rustworkx.generators.star_graph(3)

def map_function(_source, target, _weight):
    if target > 2:
        return 2
    return 1
res = graph.substitute_node_with_subgraph(0, in_graph, map_function)
self.assertEqual({0: 5, 1: 6, 2: 7}, res)
expected = [(5, 6), (5, 7), (7, 4), (7, 3), (6, 2), (6, 1)]
self.assertEqual(sorted(expected), sorted(graph.edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_substitute_node_with_subgraph.py:92*

### test_multiple_mapping_full

**Category**: workflow  
**Description**: Workflow: test multiple mapping full  
**Expected**: self.assertEqual(expected, graph.weighted_edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.path_graph(5)

graph = rustworkx.generators.star_graph(5)
in_graph = rustworkx.generators.star_graph(weights=list(range(3)))
in_graph.add_edge(1, 2, None)

def map_function(source, target, _weight):
    if target > 2:
        return 2
    return 1

def filter_fn(node):
    return node > 0

def map_weight(_):
    return 'migrated'
res = graph.substitute_node_with_subgraph(0, in_graph, map_function, filter_fn, map_weight)
self.assertEqual({1: 5, 2: 6}, res)
expected = [(5, 6, 'migrated'), (6, 4, None), (6, 3, None), (5, 2, None), (5, 1, None)]
self.assertEqual(expected, graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_substitute_node_with_subgraph.py:106*

### test_multiple_mapping

**Category**: workflow  
**Description**: Workflow: test multiple mapping  
**Expected**: self.assertEqual(sorted(expected), sorted(graph.edge_list()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.star_graph(5)
in_graph = rustworkx.generators.star_graph(3)

def map_function(_source, target, _weight):
    if target > 2:
        return 2
    return 1
res = graph.substitute_node_with_subgraph(0, in_graph, map_function)
self.assertEqual({0: 5, 1: 6, 2: 7}, res)
expected = [(5, 6), (5, 7), (7, 4), (7, 3), (6, 2), (6, 1)]
self.assertEqual(sorted(expected), sorted(graph.edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_substitute_node_with_subgraph.py:92*

### test_multiple_mapping_full

**Category**: workflow  
**Description**: Workflow: test multiple mapping full  
**Expected**: self.assertEqual(expected, graph.weighted_edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.star_graph(5)
in_graph = rustworkx.generators.star_graph(weights=list(range(3)))
in_graph.add_edge(1, 2, None)

def map_function(source, target, _weight):
    if target > 2:
        return 2
    return 1

def filter_fn(node):
    return node > 0

def map_weight(_):
    return 'migrated'
res = graph.substitute_node_with_subgraph(0, in_graph, map_function, filter_fn, map_weight)
self.assertEqual({1: 5, 2: 6}, res)
expected = [(5, 6, 'migrated'), (6, 4, None), (6, 3, None), (5, 2, None), (5, 1, None)]
self.assertEqual(expected, graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_substitute_node_with_subgraph.py:106*

### test_single_neighbor

**Category**: workflow  
**Description**: Workflow: test single neighbor  
**Expected**: self.assertTrue(np.array_equal(np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]], dtype=np.float64), res))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'edge_a')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'edge_b')
res = rustworkx.graph_adjacency_matrix(graph, lambda x: 1)
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]], dtype=np.float64), res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adjacency_matrix.py:20*

### test_no_weight_fn

**Category**: workflow  
**Description**: Workflow: test no weight fn  
**Expected**: self.assertTrue(np.array_equal(np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]], dtype=np.float64), res))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'edge_a')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'edge_b')
res = rustworkx.graph_adjacency_matrix(graph)
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]], dtype=np.float64), res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adjacency_matrix.py:39*

### test_default_weight

**Category**: workflow  
**Description**: Workflow: test default weight  
**Expected**: self.assertTrue(np.array_equal(np.array([[0.0, 4.0, 0.0], [4.0, 0.0, 4.0], [0.0, 4.0, 0.0]], dtype=np.float64), res))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'edge_a')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'edge_b')
res = rustworkx.graph_adjacency_matrix(graph, default_weight=4)
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[0.0, 4.0, 0.0], [4.0, 0.0, 4.0], [0.0, 4.0, 0.0]], dtype=np.float64), res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adjacency_matrix.py:58*

### test_float_cast_weight_func

**Category**: workflow  
**Description**: Workflow: test float cast weight func  
**Expected**: self.assertTrue(np.array_equal(np.array([[0.0, 7.0], [7.0, 0.0]]), res))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 7.0)
res = rustworkx.graph_adjacency_matrix(graph, lambda x: float(x))
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[0.0, 7.0], [7.0, 0.0]]), res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adjacency_matrix.py:77*

### test_multigraph_sum_cast_weight_func

**Category**: workflow  
**Description**: Workflow: test multigraph sum cast weight func  
**Expected**: self.assertTrue(np.array_equal(np.array([[0.0, 7.5], [7.5, 0.0]]), res))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 7.0)
graph.add_edge(node_a, node_b, 0.5)
res = rustworkx.graph_adjacency_matrix(graph, lambda x: float(x))
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[0.0, 7.5], [7.5, 0.0]]), res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adjacency_matrix.py:86*

### test_multigraph_sum_cast_weight_func_non_zero_null

**Category**: workflow  
**Description**: Workflow: test multigraph sum cast weight func non zero null  
**Expected**: self.assertTrue(np.array_equal(np.array([[np.inf, 7.5], [7.5, np.inf]]), res))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 7.0)
graph.add_edge(node_a, node_b, 0.5)
res = rustworkx.graph_adjacency_matrix(graph, lambda x: float(x), null_value=np.inf)
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[np.inf, 7.5], [7.5, np.inf]]), res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adjacency_matrix.py:96*

### test_graph_with_index_holes

**Category**: workflow  
**Description**: Workflow: test graph with index holes  
**Expected**: self.assertTrue(np.array_equal(np.array([[0, 1], [1, 0]]), res))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 1)
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, 1)
graph.remove_node(node_b)
res = rustworkx.graph_adjacency_matrix(graph, lambda x: 1)
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[0, 1], [1, 0]]), res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adjacency_matrix.py:117*

### test_random_graph_full_path

**Category**: workflow  
**Description**: Workflow: test random graph full path  
**Expected**: self.assertTrue(np.array_equal(adjacency_matrix, new_adjacency_matrix))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.undirected_gnp_random_graph(100, 0.95, seed=42)
adjacency_matrix = rustworkx.graph_adjacency_matrix(graph)
new_graph = rustworkx.PyGraph.from_adjacency_matrix(adjacency_matrix)
new_adjacency_matrix = rustworkx.graph_adjacency_matrix(new_graph)
self.assertTrue(np.array_equal(adjacency_matrix, new_adjacency_matrix))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adjacency_matrix.py:138*

### test_non_zero_null

**Category**: workflow  
**Description**: Workflow: test non zero null  
**Expected**: self.assertTrue(np.array_equal(adj_matrix, expected_matrix))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
input_matrix = np.array([[np.inf, 1, np.inf], [1, np.inf, 1], [np.inf, 1, np.inf]], dtype=np.float64)
graph = rustworkx.PyGraph.from_adjacency_matrix(input_matrix, null_value=np.inf)
adj_matrix = rustworkx.adjacency_matrix(graph, float)
expected_matrix = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=np.float64)
self.assertTrue(np.array_equal(adj_matrix, expected_matrix))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adjacency_matrix.py:166*

### test_nan_null

**Category**: workflow  
**Description**: Workflow: test nan null  
**Expected**: self.assertTrue(np.array_equal(adj_matrix, expected_matrix))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
input_matrix = np.array([[np.nan, 1, np.nan], [1, np.nan, 1], [np.nan, 1, np.nan]], dtype=np.float64)
graph = rustworkx.PyGraph.from_adjacency_matrix(input_matrix, null_value=np.nan)
adj_matrix = rustworkx.adjacency_matrix(graph, float)
expected_matrix = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=np.float64)
self.assertTrue(np.array_equal(adj_matrix, expected_matrix))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adjacency_matrix.py:183*

### test_filter_nodes

**Category**: workflow  
**Description**: Workflow: test filter nodes  
**Expected**: self.assertEqual(list(human_indices), [])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
def my_filter_function1(node):
    return node == 'cat'

def my_filter_function2(node):
    return node == 'lizard'

def my_filter_function3(node):
    return node == 'human'
graph = rx.PyDiGraph()
graph.add_node('cat')
graph.add_node('cat')
graph.add_node('dog')
graph.add_node('lizard')
graph.add_node('cat')
cat_indices = graph.filter_nodes(my_filter_function1)
lizard_indices = graph.filter_nodes(my_filter_function2)
human_indices = graph.filter_nodes(my_filter_function3)
self.assertEqual(list(cat_indices), [0, 1, 4])
self.assertEqual(list(lizard_indices), [3])
self.assertEqual(list(human_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_filter.py:19*

### test_filter_edges

**Category**: workflow  
**Description**: Workflow: test filter edges  
**Expected**: self.assertEqual(list(frenemies_indices), [])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
def my_filter_function1(edge):
    return edge == 'friends'

def my_filter_function2(edge):
    return edge == 'enemies'

def my_filter_function3(node):
    return node == 'frenemies'
graph = rx.PyDiGraph()
graph.add_node('cat')
graph.add_node('cat')
graph.add_node('dog')
graph.add_node('lizard')
graph.add_node('cat')
graph.add_edge(0, 2, 'friends')
graph.add_edge(0, 1, 'friends')
graph.add_edge(0, 3, 'enemies')
friends_indices = graph.filter_edges(my_filter_function1)
enemies_indices = graph.filter_edges(my_filter_function2)
frenemies_indices = graph.filter_edges(my_filter_function3)
self.assertEqual(list(friends_indices), [0, 1])
self.assertEqual(list(enemies_indices), [2])
self.assertEqual(list(frenemies_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_filter.py:42*

### test_filter_nodes

**Category**: workflow  
**Description**: Workflow: test filter nodes  
**Expected**: self.assertEqual(list(human_indices), [])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
def my_filter_function1(node):
    return node == 'cat'

def my_filter_function2(node):
    return node == 'lizard'

def my_filter_function3(node):
    return node == 'human'
graph = rx.PyDiGraph()
graph.add_node('cat')
graph.add_node('cat')
graph.add_node('dog')
graph.add_node('lizard')
graph.add_node('cat')
cat_indices = graph.filter_nodes(my_filter_function1)
lizard_indices = graph.filter_nodes(my_filter_function2)
human_indices = graph.filter_nodes(my_filter_function3)
self.assertEqual(list(cat_indices), [0, 1, 4])
self.assertEqual(list(lizard_indices), [3])
self.assertEqual(list(human_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_filter.py:19*

### test_filter_edges

**Category**: workflow  
**Description**: Workflow: test filter edges  
**Expected**: self.assertEqual(list(frenemies_indices), [])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
def my_filter_function1(edge):
    return edge == 'friends'

def my_filter_function2(edge):
    return edge == 'enemies'

def my_filter_function3(node):
    return node == 'frenemies'
graph = rx.PyDiGraph()
graph.add_node('cat')
graph.add_node('cat')
graph.add_node('dog')
graph.add_node('lizard')
graph.add_node('cat')
graph.add_edge(0, 2, 'friends')
graph.add_edge(0, 1, 'friends')
graph.add_edge(0, 3, 'enemies')
friends_indices = graph.filter_edges(my_filter_function1)
enemies_indices = graph.filter_edges(my_filter_function2)
frenemies_indices = graph.filter_edges(my_filter_function3)
self.assertEqual(list(friends_indices), [0, 1])
self.assertEqual(list(enemies_indices), [2])
self.assertEqual(list(frenemies_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_filter.py:42*

### test_large_partial_random

**Category**: workflow  
**Description**: Workflow: Test a random (partial) mapping on a large randomly generated graph  
**Expected**: self.assertEqual({i: i for i in mapping.values()}, mapping)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test cases.'
super().setUp()
random.seed(0)

'Test a random (partial) mapping on a large randomly generated graph'
size = 100
graph = rx.undirected_gnm_random_graph(size, size ** 2 // 10)
for i in graph.node_indexes():
    try:
        graph.remove_edge(i, i)
    except rx.NoEdgeBetweenNodes:
        continue
graph.add_edges_from_no_data([(i, i + 1) for i in range(len(graph) - 1)])
rand_perm = random.permutation(graph.nodes())
permutation = dict(zip(graph.nodes(), rand_perm))
mapping = dict(itertools.islice(permutation.items(), 0, size, 2))
swaps = rx.graph_token_swapper(graph, permutation, 4, 4)
swap_permutation(mapping, swaps)
self.assertEqual({i: i for i in mapping.values()}, mapping)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_token_swapper.py:99*

### test_large_partial_random

**Category**: workflow  
**Description**: Workflow: Test a random (partial) mapping on a large randomly generated graph  
**Expected**: self.assertEqual({i: i for i in mapping.values()}, mapping)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test a random (partial) mapping on a large randomly generated graph'
size = 100
graph = rx.undirected_gnm_random_graph(size, size ** 2 // 10)
for i in graph.node_indexes():
    try:
        graph.remove_edge(i, i)
    except rx.NoEdgeBetweenNodes:
        continue
graph.add_edges_from_no_data([(i, i + 1) for i in range(len(graph) - 1)])
rand_perm = random.permutation(graph.nodes())
permutation = dict(zip(graph.nodes(), rand_perm))
mapping = dict(itertools.islice(permutation.items(), 0, size, 2))
swaps = rx.graph_token_swapper(graph, permutation, 4, 4)
swap_permutation(mapping, swaps)
self.assertEqual({i: i for i in mapping.values()}, mapping)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_token_swapper.py:99*

### test_shared_ref

**Category**: workflow  
**Description**: Workflow: test shared ref  
**Expected**: self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_weight = {'a': 1}
node_a = graph.add_node(node_weight)
edge_weight = {'a': 1}
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, edge_weight)
digraph = graph.to_directed()
self.assertEqual(digraph[node_a], {'a': 1})
self.assertEqual(graph[node_a], {'a': 1})
node_weight['b'] = 2
self.assertEqual(digraph[node_a], {'a': 1, 'b': 2})
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1})
edge_weight['b'] = 2
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1, 'b': 2})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_to_directed.py:62*

### test_shared_ref

**Category**: workflow  
**Description**: Workflow: test shared ref  
**Expected**: self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_weight = {'a': 1}
node_a = graph.add_node(node_weight)
edge_weight = {'a': 1}
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, edge_weight)
digraph = graph.to_directed()
self.assertEqual(digraph[node_a], {'a': 1})
self.assertEqual(graph[node_a], {'a': 1})
node_weight['b'] = 2
self.assertEqual(digraph[node_a], {'a': 1, 'b': 2})
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1})
edge_weight['b'] = 2
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1, 'b': 2})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_to_directed.py:62*

### test_bellman_ford_length_with_no_path_and_goal

**Category**: workflow  
**Description**: Workflow: test bellman ford length with no path and goal  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
path_lengths = rustworkx.graph_bellman_ford_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
expected = rustworkx.graph_dijkstra_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bellman_ford.py:80*

### test_bellman_ford_length_with_no_path

**Category**: workflow  
**Description**: Workflow: test bellman ford length with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

g = rustworkx.PyGraph()
a = g.add_node('A')
g.add_node('B')
path_lengths = rustworkx.graph_bellman_ford_shortest_path_lengths(g, a, edge_cost_fn=float)
expected = {}
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bellman_ford.py:90*

### test_bellman_ford_with_no_path

**Category**: workflow  
**Description**: Workflow: test bellman ford with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

g = rustworkx.PyGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.graph_bellman_ford_shortest_path_lengths(g, a, lambda x: float(x))
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bellman_ford.py:109*

### test_bellman_ford_path_with_no_path

**Category**: workflow  
**Description**: Workflow: test bellman ford path with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

g = rustworkx.PyGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.graph_bellman_ford_shortest_paths(g, a, weight_fn=lambda x: float(x))
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bellman_ford.py:117*

### test_bellman_ford_with_disconnected_nodes

**Category**: workflow  
**Description**: Workflow: test bellman ford with disconnected nodes  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
g.add_edge(a, b, 1.2)
g.add_node('C')
d = g.add_node('D')
g.add_edge(b, d, 2.4)
path = rustworkx.graph_bellman_ford_shortest_path_lengths(g, a, lambda x: round(x, 1))
expected = {1: 1.2, 3: 3.5999999999999996}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bellman_ford.py:125*

### test_bellman_ford_length_with_no_path_and_goal

**Category**: workflow  
**Description**: Workflow: test bellman ford length with no path and goal  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
path_lengths = rustworkx.graph_bellman_ford_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
expected = rustworkx.graph_dijkstra_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bellman_ford.py:80*

### test_bellman_ford_length_with_no_path

**Category**: workflow  
**Description**: Workflow: test bellman ford length with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
g.add_node('B')
path_lengths = rustworkx.graph_bellman_ford_shortest_path_lengths(g, a, edge_cost_fn=float)
expected = {}
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bellman_ford.py:90*

### test_bellman_ford_with_no_path

**Category**: workflow  
**Description**: Workflow: test bellman ford with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.graph_bellman_ford_shortest_path_lengths(g, a, lambda x: float(x))
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bellman_ford.py:109*

### test_bellman_ford_path_with_no_path

**Category**: workflow  
**Description**: Workflow: test bellman ford path with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.graph_bellman_ford_shortest_paths(g, a, weight_fn=lambda x: float(x))
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bellman_ford.py:117*

### test_bellman_ford_with_disconnected_nodes

**Category**: workflow  
**Description**: Workflow: test bellman ford with disconnected nodes  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
g.add_edge(a, b, 1.2)
g.add_node('C')
d = g.add_node('D')
g.add_edge(b, d, 2.4)
path = rustworkx.graph_bellman_ford_shortest_path_lengths(g, a, lambda x: round(x, 1))
expected = {1: 1.2, 3: 3.5999999999999996}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bellman_ford.py:125*

### test_qiskit_style_visualization

**Category**: workflow  
**Description**: Workflow: This test is to test visualizations like qiskit performs which regressed in 0.15.0.  
**Expected**: self.assertTrue(os.path.isfile('test_qiskit_style_visualization.png'))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'This test is to test visualizations like qiskit performs which regressed in 0.15.0.'
graph = rustworkx.generators.cycle_graph(4)
colors = ['#422952', '#492d58', '#4f305c', '#5e3767']
edge_colors = ['#4d2f5b', '#693d6f', '#995a88', '#382449']
pos = [(0, 0), (0, 1), (1, 0), (1, 1)]
for node in graph.node_indices():
    graph[node] = node
for edge in graph.edge_indices():
    graph.update_edge_by_index(edge, edge)

def color_node(node):
    out_dict = {'label': str(node), 'color': f'"{colors[node]}"', 'pos': f'"{pos[node][0]}, {pos[node][1]}"', 'fontname': '"DejaVu Sans"', 'pin': 'True', 'shape': 'circle', 'style': 'filled', 'fillcolor': f'"{colors[node]}"', 'fontcolor': 'white', 'fontsize': '10', 'height': '0.322', 'fixedsize': 'True'}
    return out_dict

def color_edge(edge):
    out_dict = {'color': f'"{edge_colors[edge]}"', 'fillcolor': f'"{edge_colors[edge]}"', 'penwidth': str(5)}
    return out_dict
graphviz_draw(graph, node_attr_fn=color_node, edge_attr_fn=color_edge, filename='test_qiskit_style_visualization.png', image_type='png', method='neato')
self.assertTrue(os.path.isfile('test_qiskit_style_visualization.png'))
if not SAVE_IMAGES:
    self.addCleanup(os.remove, 'test_qiskit_style_visualization.png')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_graphviz.py:153*

### test_escape_sequences

**Category**: workflow  
**Description**: Workflow: test escape sequences  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.path_graph(2)
escape_sequences = {'\\n': '\n', '\\t': '\t', "\\'": "'", '\\"': '"', '\\\\': '\\', '\\r': '\r', '\\b': '\x08', '\\f': '\x0c'}
for escaped_seq, raw_seq in escape_sequences.items():
    with self.subTest(chr=ord(raw_seq)):

        def node_attr(node):
            """
                    Define node attributes including escape sequences for labels and tooltips.
                    """
            label = f'label{escaped_seq}'
            tooltip = f'tooltip{escaped_seq}'
            return {'label': label, 'tooltip': tooltip}
        dot_str = graph.to_dot(node_attr)
        self.assertIn(escaped_seq, dot_str, f'Escape sequence {escaped_seq} not found in dot output')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_graphviz.py:202*

### test_qiskit_style_visualization

**Category**: workflow  
**Description**: Workflow: This test is to test visualizations like qiskit performs which regressed in 0.15.0.  
**Expected**: self.assertTrue(os.path.isfile('test_qiskit_style_visualization.png'))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'This test is to test visualizations like qiskit performs which regressed in 0.15.0.'
graph = rustworkx.generators.cycle_graph(4)
colors = ['#422952', '#492d58', '#4f305c', '#5e3767']
edge_colors = ['#4d2f5b', '#693d6f', '#995a88', '#382449']
pos = [(0, 0), (0, 1), (1, 0), (1, 1)]
for node in graph.node_indices():
    graph[node] = node
for edge in graph.edge_indices():
    graph.update_edge_by_index(edge, edge)

def color_node(node):
    out_dict = {'label': str(node), 'color': f'"{colors[node]}"', 'pos': f'"{pos[node][0]}, {pos[node][1]}"', 'fontname': '"DejaVu Sans"', 'pin': 'True', 'shape': 'circle', 'style': 'filled', 'fillcolor': f'"{colors[node]}"', 'fontcolor': 'white', 'fontsize': '10', 'height': '0.322', 'fixedsize': 'True'}
    return out_dict

def color_edge(edge):
    out_dict = {'color': f'"{edge_colors[edge]}"', 'fillcolor': f'"{edge_colors[edge]}"', 'penwidth': str(5)}
    return out_dict
graphviz_draw(graph, node_attr_fn=color_node, edge_attr_fn=color_edge, filename='test_qiskit_style_visualization.png', image_type='png', method='neato')
self.assertTrue(os.path.isfile('test_qiskit_style_visualization.png'))
if not SAVE_IMAGES:
    self.addCleanup(os.remove, 'test_qiskit_style_visualization.png')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_graphviz.py:153*

### test_escape_sequences

**Category**: workflow  
**Description**: Workflow: test escape sequences  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.path_graph(2)
escape_sequences = {'\\n': '\n', '\\t': '\t', "\\'": "'", '\\"': '"', '\\\\': '\\', '\\r': '\r', '\\b': '\x08', '\\f': '\x0c'}
for escaped_seq, raw_seq in escape_sequences.items():
    with self.subTest(chr=ord(raw_seq)):

        def node_attr(node):
            """
                    Define node attributes including escape sequences for labels and tooltips.
                    """
            label = f'label{escaped_seq}'
            tooltip = f'tooltip{escaped_seq}'
            return {'label': label, 'tooltip': tooltip}
        dot_str = graph.to_dot(node_attr)
        self.assertIn(escaped_seq, dot_str, f'Escape sequence {escaped_seq} not found in dot output')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_graphviz.py:202*

### test_get_edge_data

**Category**: workflow  
**Description**: Workflow: test get edge data  
**Expected**: self.assertEqual('Edgy', res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
res = graph.get_edge_data(node_a, node_b)
self.assertEqual('Edgy', res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edges.py:19*

### test_get_all_edge_data

**Category**: workflow  
**Description**: Workflow: test get all edge data  
**Expected**: self.assertIn('Edgy', res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
graph.add_edge(node_a, node_b, 'b')
res = graph.get_all_edge_data(node_a, node_b)
self.assertIn('b', res)
self.assertIn('Edgy', res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edges.py:27*

### test_update_edge_by_index

**Category**: workflow  
**Description**: Workflow: test update edge by index  
**Expected**: self.assertEqual([(0, 1, 'Edgy')], graph.weighted_edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
edge_index = graph.add_edge(node_a, node_b, 'not edgy')
graph.update_edge_by_index(edge_index, 'Edgy')
self.assertEqual([(0, 1, 'Edgy')], graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edges.py:71*

### test_update_edge_parallel_edges

**Category**: workflow  
**Description**: Workflow: test update edge parallel edges  
**Expected**: self.assertEqual([(0, 1, 'not edgy'), (0, 1, 'Edgy')], list(graph.weighted_edge_list()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'not edgy')
edge_index = graph.add_edge(node_a, node_b, 'not edgy')
graph.update_edge_by_index(edge_index, 'Edgy')
self.assertEqual([(0, 1, 'not edgy'), (0, 1, 'Edgy')], list(graph.weighted_edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edges.py:85*

### test_edges

**Category**: workflow  
**Description**: Workflow: test edges  
**Expected**: self.assertEqual(['Edgy', 'Super edgy'], graph.edges())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'Super edgy')
self.assertEqual(['Edgy', 'Super edgy'], graph.edges())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edges.py:117*

### test_edge_indices

**Category**: workflow  
**Description**: Workflow: test edge indices  
**Expected**: self.assertEqual([0, 1], graph.edge_indices())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'Super edgy')
self.assertEqual([0, 1], graph.edge_indices())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edges.py:131*

### test_remove_edges_from

**Category**: workflow  
**Description**: Workflow: test remove edges from  
**Expected**: self.assertEqual([], graph.edges())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
graph.add_edge(node_a, node_b, 'edgy')
graph.add_edge(node_a, node_c, 'super_edgy')
graph.remove_edges_from([(node_a, node_b), (node_a, node_c)])
self.assertEqual([], graph.edges())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edges.py:190*

### test_remove_edges_from_gen

**Category**: workflow  
**Description**: Workflow: test remove edges from gen  
**Expected**: self.assertEqual([], graph.edges())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
graph.add_edge(node_a, node_b, 'edgy')
graph.add_edge(node_a, node_c, 'super_edgy')
graph.remove_edges_from(((node_a, n) for n in (node_b, node_c)))
self.assertEqual([], graph.edges())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edges.py:200*

### test_remove_edges_from_invalid

**Category**: workflow  
**Description**: Workflow: test remove edges from invalid  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
graph.add_edge(node_a, node_b, 'edgy')
graph.add_edge(node_a, node_c, 'super_edgy')
with self.assertRaises(rustworkx.NoEdgeBetweenNodes):
    graph.remove_edges_from([(node_b, node_c), (node_a, node_c)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edges.py:210*

### test_degree

**Category**: workflow  
**Description**: Workflow: test degree  
**Expected**: self.assertEqual(2, graph.degree(node_b))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'Super edgy')
self.assertEqual(2, graph.degree(node_b))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edges.py:220*

### test_tr1

**Category**: workflow  
**Description**: Workflow: test tr1  
**Expected**: self.assertCountEqual(list(tr.edge_list()), [(0, 2), (0, 1), (1, 3), (2, 3), (3, 4)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
a = graph.add_node('a')
b = graph.add_node('b')
c = graph.add_node('c')
d = graph.add_node('d')
e = graph.add_node('e')
graph.add_edges_from([(a, b, 1), (a, d, 1), (a, c, 1), (a, e, 1), (b, d, 1), (c, d, 1), (c, e, 1), (d, e, 1)])
tr, _ = rustworkx.transitive_reduction(graph)
self.assertCountEqual(list(tr.edge_list()), [(0, 2), (0, 1), (1, 3), (2, 3), (3, 4)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitive_reduction.py:19*

### test_tr2

**Category**: workflow  
**Description**: Workflow: test tr2  
**Expected**: self.assertCountEqual(list(tr2.edge_list()), [(0, 1), (1, 2)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph2 = rustworkx.PyDiGraph()
a = graph2.add_node('a')
b = graph2.add_node('b')
c = graph2.add_node('c')
graph2.add_edges_from([(a, b, 1), (b, c, 1), (a, c, 1)])
tr2, _ = rustworkx.transitive_reduction(graph2)
self.assertCountEqual(list(tr2.edge_list()), [(0, 1), (1, 2)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitive_reduction.py:32*

### test_tr_with_deletion

**Category**: workflow  
**Description**: Workflow: test tr with deletion  
**Expected**: self.assertEqual(index_map[4], 3)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
a = graph.add_node('a')
b = graph.add_node('b')
c = graph.add_node('c')
d = graph.add_node('d')
e = graph.add_node('e')
graph.add_edges_from([(a, b, 1), (a, d, 1), (a, c, 1), (a, e, 1), (b, d, 1), (c, d, 1), (c, e, 1), (d, e, 1)])
graph.remove_node(3)
tr, index_map = rustworkx.transitive_reduction(graph)
self.assertCountEqual(list(tr.edge_list()), [(0, 1), (0, 2), (2, 3)])
self.assertEqual(index_map[4], 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitive_reduction.py:54*

### test_tr1

**Category**: workflow  
**Description**: Workflow: test tr1  
**Expected**: self.assertCountEqual(list(tr.edge_list()), [(0, 2), (0, 1), (1, 3), (2, 3), (3, 4)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
a = graph.add_node('a')
b = graph.add_node('b')
c = graph.add_node('c')
d = graph.add_node('d')
e = graph.add_node('e')
graph.add_edges_from([(a, b, 1), (a, d, 1), (a, c, 1), (a, e, 1), (b, d, 1), (c, d, 1), (c, e, 1), (d, e, 1)])
tr, _ = rustworkx.transitive_reduction(graph)
self.assertCountEqual(list(tr.edge_list()), [(0, 2), (0, 1), (1, 3), (2, 3), (3, 4)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitive_reduction.py:19*

### test_tr2

**Category**: workflow  
**Description**: Workflow: test tr2  
**Expected**: self.assertCountEqual(list(tr2.edge_list()), [(0, 1), (1, 2)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph2 = rustworkx.PyDiGraph()
a = graph2.add_node('a')
b = graph2.add_node('b')
c = graph2.add_node('c')
graph2.add_edges_from([(a, b, 1), (b, c, 1), (a, c, 1)])
tr2, _ = rustworkx.transitive_reduction(graph2)
self.assertCountEqual(list(tr2.edge_list()), [(0, 1), (1, 2)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitive_reduction.py:32*

### test_tr_with_deletion

**Category**: workflow  
**Description**: Workflow: test tr with deletion  
**Expected**: self.assertEqual(index_map[4], 3)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
a = graph.add_node('a')
b = graph.add_node('b')
c = graph.add_node('c')
d = graph.add_node('d')
e = graph.add_node('e')
graph.add_edges_from([(a, b, 1), (a, d, 1), (a, c, 1), (a, e, 1), (b, d, 1), (c, d, 1), (c, e, 1), (d, e, 1)])
graph.remove_node(3)
tr, index_map = rustworkx.transitive_reduction(graph)
self.assertCountEqual(list(tr.edge_list()), [(0, 1), (0, 2), (2, 3)])
self.assertEqual(index_map[4], 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitive_reduction.py:54*

### test_isomorphic_identical

**Category**: workflow  
**Description**: Workflow: test isomorphic identical  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_isomorphic(g_a, g_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isomorphic.py:42*

### test_isomorphic_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test isomorphic mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
nodes = g_b.add_nodes_from(['b_1', 'b_2', 'b_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'b_1'), (nodes[1], nodes[2], 'b_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_isomorphic(g_a, g_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isomorphic.py:55*

### test_isomorphic_compare_nodes_mismatch_node_data

**Category**: workflow  
**Description**: Workflow: test isomorphic compare nodes mismatch node data  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
nodes = g_b.add_nodes_from(['b_1', 'b_2', 'b_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'b_1'), (nodes[1], nodes[2], 'b_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertFalse(rustworkx.is_isomorphic(g_a, g_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isomorphic.py:68*

### test_is_isomorphic_nodes_compare_raises

**Category**: workflow  
**Description**: Workflow: test is isomorphic nodes compare raises  
**Expected**: self.assertRaises(TypeError, rustworkx.is_isomorphic, (g_a, g_b, compare_nodes))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
nodes = g_b.add_nodes_from(['b_1', 'b_2', 'b_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'b_1'), (nodes[1], nodes[2], 'b_2')])

def compare_nodes(a, b):
    raise TypeError('Failure')
self.assertRaises(TypeError, rustworkx.is_isomorphic, (g_a, g_b, compare_nodes))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isomorphic.py:83*

### test_isomorphic_compare_nodes_identical

**Category**: workflow  
**Description**: Workflow: test isomorphic compare nodes identical  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_isomorphic(g_a, g_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isomorphic.py:98*

### test_isomorphic_compare_edges_identical

**Category**: workflow  
**Description**: Workflow: test isomorphic compare edges identical  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_isomorphic(g_a, g_b, edge_matcher=lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isomorphic.py:113*

### test_isomorphic_removed_nodes_in_second_graph

**Category**: workflow  
**Description**: Workflow: test isomorphic removed nodes in second graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2')])
nodes = g_b.add_nodes_from(['a_0', 'a_2', 'a_1', 'a_3'])
g_b.add_edges_from([(nodes[0], nodes[1], 'e_01'), (nodes[0], nodes[3], 'e_03'), (nodes[2], nodes[1], 'a_1'), (nodes[1], nodes[3], 'a_2')])
g_b.remove_node(nodes[0])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertTrue(rustworkx.is_isomorphic(g_a, g_b, lambda x, y: x == y, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isomorphic.py:133*

### test_isomorphic_node_count_not_equal

**Category**: workflow  
**Description**: Workflow: test isomorphic node count not equal  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1')])
nodes = g_b.add_nodes_from(['a_0', 'a_1'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1')])
g_b.remove_node(nodes[0])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertFalse(rustworkx.is_isomorphic(g_a, g_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isomorphic.py:156*

### test_same_degrees_non_isomorphic

**Category**: workflow  
**Description**: Workflow: test same degrees non isomorphic  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g_a = rustworkx.PyGraph()
g_b = rustworkx.PyGraph()
nodes = g_a.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4', 'b_1', 'b_2', 'b_3', 'b_4'])
g_a.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[2], nodes[3], 'a_3'), (nodes[3], nodes[0], 'a_4'), (nodes[4], nodes[5], 'b_1'), (nodes[5], nodes[6], 'b_2'), (nodes[6], nodes[7], 'b_3'), (nodes[7], nodes[4], 'b_4'), (nodes[0], nodes[4], 'e_1'), (nodes[1], nodes[5], 'e_2')])
nodes = g_b.add_nodes_from(['a_1', 'a_2', 'a_3', 'a_4', 'b_1', 'b_2', 'b_3', 'b_4'])
g_b.add_edges_from([(nodes[0], nodes[1], 'a_1'), (nodes[1], nodes[2], 'a_2'), (nodes[2], nodes[3], 'a_3'), (nodes[3], nodes[0], 'a_4'), (nodes[4], nodes[5], 'b_1'), (nodes[5], nodes[6], 'b_2'), (nodes[6], nodes[7], 'b_3'), (nodes[7], nodes[4], 'b_4'), (nodes[0], nodes[4], 'e_1'), (nodes[2], nodes[6], 'e_2')])
for id_order in [False, True]:
    with self.subTest(id_order=id_order):
        self.assertFalse(rustworkx.is_isomorphic(g_a, g_b, id_order=id_order))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isomorphic.py:170*

### test_graph_vf2_number_of_valid_mappings

**Category**: workflow  
**Description**: Workflow: test graph vf2 number of valid mappings  
**Expected**: self.assertEqual(total, 6)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.mesh_graph(3)
mapping = rustworkx.graph_vf2_mapping(graph, graph, id_order=True)
total = 0
for _ in mapping:
    total += 1
self.assertEqual(total, 6)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isomorphic.py:299*

### test_digraph_dfs_edges_star

**Category**: workflow  
**Description**: Workflow: test digraph dfs edges star  
**Expected**: self.assertEqual(visited, set(spokes))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_star_graph(101)
hub = 0
spokes = list(range(1, 101))
edges = rustworkx.digraph_dfs_edges(graph, hub)
self.assertEqual(len(edges), 100)
for src, _ in edges:
    self.assertEqual(src, hub)
visited = {tgt for _, tgt in edges}
self.assertEqual(visited, set(spokes))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_edges.py:53*

### test_digraph_dfs_edges_star

**Category**: workflow  
**Description**: Workflow: test digraph dfs edges star  
**Expected**: self.assertEqual(visited, set(spokes))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_star_graph(101)
hub = 0
spokes = list(range(1, 101))
edges = rustworkx.digraph_dfs_edges(graph, hub)
self.assertEqual(len(edges), 100)
for src, _ in edges:
    self.assertEqual(src, hub)
visited = {tgt for _, tgt in edges}
self.assertEqual(visited, set(spokes))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_edges.py:53*

### test_slices_negatives

**Category**: workflow  
**Description**: Workflow: test slices negatives  
**Expected**: self.assertEqual([], indices[-1:-2])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.dag = rustworkx.PyDAG()
node_a = self.dag.add_node('a')
self.dag.add_child(node_a, 'b', 'Edgy')

graph = rustworkx.PyGraph()
graph.add_nodes_from(range(5))
indices = graph.node_indices()
slice_return = indices[-1:-3:-1]
self.assertEqual([4, 3], slice_return)
slice_return = indices[3:1:-2]
self.assertEqual([3], slice_return)
slice_return = indices[-3:-1]
self.assertEqual([2, 3], slice_return)
self.assertEqual([], indices[-1:-2])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_custom_return_types.py:175*

### test_iter_stable_for_same_obj

**Category**: workflow  
**Description**: Workflow: test iter stable for same obj  
**Expected**: self.assertEqual(first_iter, third_iter)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.dag = rustworkx.PyDAG()
self.dag.add_node('a')
self.in_dag = rustworkx.generators.directed_path_graph(1)

graph = rustworkx.PyDiGraph()
graph.add_node(0)
in_graph = rustworkx.generators.directed_path_graph(5)
res = self.dag.substitute_node_with_subgraph(0, in_graph, lambda *args: None)
first_iter = list(iter(res))
second_iter = list(iter(res))
third_iter = list(iter(res))
self.assertEqual(first_iter, second_iter)
self.assertEqual(first_iter, third_iter)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_custom_return_types.py:1367*

### test_slices_negatives

**Category**: workflow  
**Description**: Workflow: test slices negatives  
**Expected**: self.assertEqual([], indices[-1:-2])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
graph.add_nodes_from(range(5))
indices = graph.node_indices()
slice_return = indices[-1:-3:-1]
self.assertEqual([4, 3], slice_return)
slice_return = indices[3:1:-2]
self.assertEqual([3], slice_return)
slice_return = indices[-3:-1]
self.assertEqual([2, 3], slice_return)
self.assertEqual([], indices[-1:-2])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_custom_return_types.py:175*

### test_iter_stable_for_same_obj

**Category**: workflow  
**Description**: Workflow: test iter stable for same obj  
**Expected**: self.assertEqual(first_iter, third_iter)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
graph.add_node(0)
in_graph = rustworkx.generators.directed_path_graph(5)
res = self.dag.substitute_node_with_subgraph(0, in_graph, lambda *args: None)
first_iter = list(iter(res))
second_iter = list(iter(res))
third_iter = list(iter(res))
self.assertEqual(first_iter, second_iter)
self.assertEqual(first_iter, third_iter)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_custom_return_types.py:1367*

### test_empty_directed

**Category**: workflow  
**Description**: Workflow: test empty directed  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
N = 5
graph = rustworkx.PyDiGraph()
graph.add_nodes_from([i for i in range(N)])
expected_graph = rustworkx.PyDiGraph()
expected_graph.extend_from_edge_list([(i, j) for i in range(N) for j in range(N) if i != j])
complement_graph = rustworkx.complement(graph)
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_complement.py:34*

### test_complement_directed

**Category**: workflow  
**Description**: Workflow: test complement directed  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
N = 8
graph = rustworkx.PyDiGraph()
graph.extend_from_edge_list([(i, j) for i in range(N) for j in range(N) if i != j and (i + j) % 3 == 0])
expected_graph = rustworkx.PyDiGraph()
expected_graph.extend_from_edge_list([(i, j) for i in range(N) for j in range(N) if i != j and (i + j) % 3 != 0])
complement_graph = rustworkx.complement(graph)
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_complement.py:50*

### test_empty_directed

**Category**: workflow  
**Description**: Workflow: test empty directed  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
N = 5
graph = rustworkx.PyDiGraph()
graph.add_nodes_from([i for i in range(N)])
expected_graph = rustworkx.PyDiGraph()
expected_graph.extend_from_edge_list([(i, j) for i in range(N) for j in range(N) if i != j])
complement_graph = rustworkx.complement(graph)
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_complement.py:34*

### test_complement_directed

**Category**: workflow  
**Description**: Workflow: test complement directed  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
N = 8
graph = rustworkx.PyDiGraph()
graph.extend_from_edge_list([(i, j) for i in range(N) for j in range(N) if i != j and (i + j) % 3 == 0])
expected_graph = rustworkx.PyDiGraph()
expected_graph.extend_from_edge_list([(i, j) for i in range(N) for j in range(N) if i != j and (i + j) % 3 != 0])
complement_graph = rustworkx.complement(graph)
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_complement.py:50*

### test_isomorphic_to_networkx

**Category**: workflow  
**Description**: Workflow: test isomorphic to networkx  
**Expected**: self.assertTrue(rx.is_isomorphic(graph, expected, node_matcher=node_matcher, edge_matcher=edge_matcher))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
def node_matcher(a, b):
    if isinstance(a, dict):
        a, b = (b, a)
    return a == b['club']

def edge_matcher(a, b):
    if isinstance(a, dict):
        a, b = (b, a)
    return a == b['weight']
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(karate_xml)
    fd.flush()
    expected = rx.read_graphml(fd.name)[0]
graph = rx.generators.karate_club_graph()
self.assertTrue(rx.is_isomorphic(graph, expected, node_matcher=node_matcher, edge_matcher=edge_matcher))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_karate.py:20*

### test_isomorphic_to_networkx

**Category**: workflow  
**Description**: Workflow: test isomorphic to networkx  
**Expected**: self.assertTrue(rx.is_isomorphic(graph, expected, node_matcher=node_matcher, edge_matcher=edge_matcher))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
def node_matcher(a, b):
    if isinstance(a, dict):
        a, b = (b, a)
    return a == b['club']

def edge_matcher(a, b):
    if isinstance(a, dict):
        a, b = (b, a)
    return a == b['weight']
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(karate_xml)
    fd.flush()
    expected = rx.read_graphml(fd.name)[0]
graph = rx.generators.karate_club_graph()
self.assertTrue(rx.is_isomorphic(graph, expected, node_matcher=node_matcher, edge_matcher=edge_matcher))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_karate.py:20*

### test_ancestors

**Category**: workflow  
**Description**: Workflow: test ancestors  
**Expected**: self.assertEqual({node_a, node_b}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
res = rustworkx.ancestors(dag, node_c)
self.assertEqual({node_a, node_b}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_ancestors_descendants.py:19*

### test_ancestors_no_descendants

**Category**: workflow  
**Description**: Workflow: test ancestors no descendants  
**Expected**: self.assertEqual({node_a}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
dag.add_child(node_b, 'c', {'b': 1})
res = rustworkx.ancestors(dag, node_b)
self.assertEqual({node_a}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_ancestors_descendants.py:34*

### test_descendants

**Category**: workflow  
**Description**: Workflow: test descendants  
**Expected**: self.assertEqual({node_b, node_c}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
res = rustworkx.descendants(dag, node_a)
self.assertEqual({node_b, node_c}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_ancestors_descendants.py:49*

### test_descendants_no_ancestors

**Category**: workflow  
**Description**: Workflow: test descendants no ancestors  
**Expected**: self.assertEqual({node_c}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'b': 1})
res = rustworkx.descendants(dag, node_b)
self.assertEqual({node_c}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_ancestors_descendants.py:63*

### test_ancestors

**Category**: workflow  
**Description**: Workflow: test ancestors  
**Expected**: self.assertEqual({node_a, node_b}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
res = rustworkx.ancestors(dag, node_c)
self.assertEqual({node_a, node_b}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_ancestors_descendants.py:19*

### test_ancestors_no_descendants

**Category**: workflow  
**Description**: Workflow: test ancestors no descendants  
**Expected**: self.assertEqual({node_a}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
dag.add_child(node_b, 'c', {'b': 1})
res = rustworkx.ancestors(dag, node_b)
self.assertEqual({node_a}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_ancestors_descendants.py:34*

### test_descendants

**Category**: workflow  
**Description**: Workflow: test descendants  
**Expected**: self.assertEqual({node_b, node_c}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
res = rustworkx.descendants(dag, node_a)
self.assertEqual({node_b, node_c}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_ancestors_descendants.py:49*

### test_descendants_no_ancestors

**Category**: workflow  
**Description**: Workflow: test descendants no ancestors  
**Expected**: self.assertEqual({node_c}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'b': 1})
res = rustworkx.descendants(dag, node_b)
self.assertEqual({node_c}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_ancestors_descendants.py:63*

### test_simple_cycles

**Category**: workflow  
**Description**: Workflow: test simple cycles  
**Expected**: self.assertEqual(len(res), len(expected))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
edges = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]
graph = rustworkx.PyDiGraph()
graph.extend_from_edge_list(edges)
expected = [[0], [0, 1, 2], [0, 2], [1, 2], [2]]
res = list(rustworkx.simple_cycles(graph))
self.assertEqual(len(res), len(expected))
for cycle in res:
    self.assertIn(sorted(cycle), expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_simple_cycles.py:19*

### test_simple_cycles

**Category**: workflow  
**Description**: Workflow: test simple cycles  
**Expected**: self.assertEqual(len(res), len(expected))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
edges = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]
graph = rustworkx.PyDiGraph()
graph.extend_from_edge_list(edges)
expected = [[0], [0, 1, 2], [0, 2], [1, 2], [2]]
res = list(rustworkx.simple_cycles(graph))
self.assertEqual(len(res), len(expected))
for cycle in res:
    self.assertIn(sorted(cycle), expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_simple_cycles.py:19*

### test_single_neighbor

**Category**: workflow  
**Description**: Workflow: test single neighbor  
**Expected**: self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'a': 2})
res = graph.adj(node_a)
self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adj.py:19*

### test_single_neighbor

**Category**: workflow  
**Description**: Workflow: test single neighbor  
**Expected**: self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'a': 2})
res = graph.adj(node_a)
self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adj.py:19*

### test_partially_connected_graph

**Category**: workflow  
**Description**: Workflow: test partially connected graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_cycle_graph(32)
graph.add_nodes_from(list(range(32)))
with self.subTest(disconnected=False):
    res = rustworkx.unweighted_average_shortest_path_length(graph)
    self.assertTrue(math.isinf(res), 'Output is not infinity')
with self.subTest(disconnected=True):
    s = 15872
    den = 992
    res = rustworkx.unweighted_average_shortest_path_length(graph, disconnected=True)
    self.assertAlmostEqual(s / den, res, delta=1e-07)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_avg_shortest_path.py:74*

### test_connected_cycle_graph

**Category**: workflow  
**Description**: Workflow: test connected cycle graph  
**Expected**: self.assertAlmostEqual(s / den, res, delta=1e-07)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_cycle_graph(32)
res = rustworkx.unweighted_average_shortest_path_length(graph)
s = 15872
den = 992
self.assertAlmostEqual(s / den, res, delta=1e-07)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_avg_shortest_path.py:87*

### test_partially_connected_graph

**Category**: workflow  
**Description**: Workflow: test partially connected graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_cycle_graph(32)
graph.add_nodes_from(list(range(32)))
with self.subTest(disconnected=False):
    res = rustworkx.unweighted_average_shortest_path_length(graph, as_undirected=True)
    self.assertTrue(math.isinf(res), 'Output is not infinity')
with self.subTest(disconnected=True):
    s = 8192
    den = 992
    res = rustworkx.unweighted_average_shortest_path_length(graph, as_undirected=True, disconnected=True)
    self.assertAlmostEqual(s / den, res, delta=1e-07)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_avg_shortest_path.py:149*

### test_connected_cycle_graph

**Category**: workflow  
**Description**: Workflow: test connected cycle graph  
**Expected**: self.assertAlmostEqual(s / den, res, delta=1e-07)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_cycle_graph(32)
res = rustworkx.unweighted_average_shortest_path_length(graph, as_undirected=True)
s = 8192
den = 992
self.assertAlmostEqual(s / den, res, delta=1e-07)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_avg_shortest_path.py:164*

### test_partially_connected_graph

**Category**: workflow  
**Description**: Workflow: test partially connected graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_cycle_graph(32)
graph.add_nodes_from(list(range(32)))
with self.subTest(disconnected=False):
    res = rustworkx.unweighted_average_shortest_path_length(graph)
    self.assertTrue(math.isinf(res), 'Output is not infinity')
with self.subTest(disconnected=True):
    s = 15872
    den = 992
    res = rustworkx.unweighted_average_shortest_path_length(graph, disconnected=True)
    self.assertAlmostEqual(s / den, res, delta=1e-07)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_avg_shortest_path.py:74*

### test_connected_cycle_graph

**Category**: workflow  
**Description**: Workflow: test connected cycle graph  
**Expected**: self.assertAlmostEqual(s / den, res, delta=1e-07)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_cycle_graph(32)
res = rustworkx.unweighted_average_shortest_path_length(graph)
s = 15872
den = 992
self.assertAlmostEqual(s / den, res, delta=1e-07)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_avg_shortest_path.py:87*

### test_partially_connected_graph

**Category**: workflow  
**Description**: Workflow: test partially connected graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_cycle_graph(32)
graph.add_nodes_from(list(range(32)))
with self.subTest(disconnected=False):
    res = rustworkx.unweighted_average_shortest_path_length(graph, as_undirected=True)
    self.assertTrue(math.isinf(res), 'Output is not infinity')
with self.subTest(disconnected=True):
    s = 8192
    den = 992
    res = rustworkx.unweighted_average_shortest_path_length(graph, as_undirected=True, disconnected=True)
    self.assertAlmostEqual(s / den, res, delta=1e-07)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_avg_shortest_path.py:149*

### test_connected_cycle_graph

**Category**: workflow  
**Description**: Workflow: test connected cycle graph  
**Expected**: self.assertAlmostEqual(s / den, res, delta=1e-07)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_cycle_graph(32)
res = rustworkx.unweighted_average_shortest_path_length(graph, as_undirected=True)
s = 8192
den = 992
self.assertAlmostEqual(s / den, res, delta=1e-07)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_avg_shortest_path.py:164*

### test_two_colors

**Category**: workflow  
**Description**: Workflow: Input:
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
**Expected**: self.assertEqual([['cx', 'cz']], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_bicolor_runs.py:47*

### test_color_with_ignored_edge

**Category**: workflow  
**Description**: Workflow: Input:
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
**Expected**: self.assertEqual([], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_bicolor_runs.py:278*

### test_two_colors

**Category**: workflow  
**Description**: Workflow: Input:
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
**Expected**: self.assertEqual([['cx', 'cz']], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_bicolor_runs.py:47*

### test_color_with_ignored_edge

**Category**: workflow  
**Description**: Workflow: Input:
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
**Expected**: self.assertEqual([], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_bicolor_runs.py:278*

### test_directed_star_graph_bidirectional_inward

**Category**: workflow  
**Description**: Workflow: test directed star graph bidirectional inward  
**Expected**: self.assertEqual(graph.in_edges(0), inw[::-1])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_star_graph(20, bidirectional=True, inward=True)
outw = []
inw = []
for i in range(1, 20):
    outw.append((0, i, None))
    inw.append((i, 0, None))
    self.assertEqual(graph.out_edges(i), [(i, 0, None)])
    self.assertEqual(graph.in_edges(i), [(0, i, None)])
self.assertEqual(graph.out_edges(0), outw[::-1])
self.assertEqual(graph.in_edges(0), inw[::-1])
graph = rustworkx.generators.directed_star_graph(20, bidirectional=True, inward=False)
outw = []
inw = []
for i in range(1, 20):
    outw.append((0, i, None))
    inw.append((i, 0, None))
    self.assertEqual(graph.out_edges(i), [(i, 0, None)])
    self.assertEqual(graph.in_edges(i), [(0, i, None)])
self.assertEqual(graph.out_edges(0), outw[::-1])
self.assertEqual(graph.in_edges(0), inw[::-1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_star.py:53*

### test_directed_star_graph_bidirectional_inward

**Category**: workflow  
**Description**: Workflow: test directed star graph bidirectional inward  
**Expected**: self.assertEqual(graph.in_edges(0), inw[::-1])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_star_graph(20, bidirectional=True, inward=True)
outw = []
inw = []
for i in range(1, 20):
    outw.append((0, i, None))
    inw.append((i, 0, None))
    self.assertEqual(graph.out_edges(i), [(i, 0, None)])
    self.assertEqual(graph.in_edges(i), [(0, i, None)])
self.assertEqual(graph.out_edges(0), outw[::-1])
self.assertEqual(graph.in_edges(0), inw[::-1])
graph = rustworkx.generators.directed_star_graph(20, bidirectional=True, inward=False)
outw = []
inw = []
for i in range(1, 20):
    outw.append((0, i, None))
    inw.append((i, 0, None))
    self.assertEqual(graph.out_edges(i), [(i, 0, None)])
    self.assertEqual(graph.in_edges(i), [(0, i, None)])
self.assertEqual(graph.out_edges(0), outw[::-1])
self.assertEqual(graph.in_edges(0), inw[::-1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_star.py:53*

### test_num_shortest_path_unweighted

**Category**: workflow  
**Description**: Workflow: test num shortest path unweighted  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node(0)
node_b = graph.add_node('end')
for i in range(3):
    node = graph.add_node(i)
    graph.add_edge(node_a, node, None)
    graph.add_edge(node, node_b, None)
res = rustworkx.graph_num_shortest_paths_unweighted(graph, node_a)
expected = {2: 1, 4: 1, 3: 1, 1: 3}
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_num_shortest_path.py:19*

### test_node_with_no_path

**Category**: workflow  
**Description**: Workflow: test node with no path  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.path_graph(5)
graph.extend_from_edge_list([(6, 7), (7, 8), (8, 9), (9, 10), (10, 11)])
expected = {1: 1, 2: 1, 3: 1, 4: 1}
res = rustworkx.num_shortest_paths_unweighted(graph, 0)
self.assertEqual(expected, res)
res = rustworkx.num_shortest_paths_unweighted(graph, 6)
expected = {7: 1, 8: 1, 9: 1, 10: 1, 11: 1}
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_num_shortest_path.py:95*

### test_num_shortest_path_unweighted

**Category**: workflow  
**Description**: Workflow: test num shortest path unweighted  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node(0)
node_b = graph.add_node('end')
for i in range(3):
    node = graph.add_node(i)
    graph.add_edge(node_a, node, None)
    graph.add_edge(node, node_b, None)
res = rustworkx.graph_num_shortest_paths_unweighted(graph, node_a)
expected = {2: 1, 4: 1, 3: 1, 1: 3}
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_num_shortest_path.py:19*

### test_node_with_no_path

**Category**: workflow  
**Description**: Workflow: test node with no path  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.path_graph(5)
graph.extend_from_edge_list([(6, 7), (7, 8), (8, 9), (9, 10), (10, 11)])
expected = {1: 1, 2: 1, 3: 1, 4: 1}
res = rustworkx.num_shortest_paths_unweighted(graph, 0)
self.assertEqual(expected, res)
res = rustworkx.num_shortest_paths_unweighted(graph, 6)
expected = {7: 1, 8: 1, 9: 1, 10: 1, 11: 1}
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_num_shortest_path.py:95*

### test_complete_graph

**Category**: workflow  
**Description**: Workflow: test complete graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_mesh_graph(5)
centrality = rustworkx.eigenvector_centrality(graph)
expected_value = math.sqrt(1.0 / 5.0)
for value in centrality.values():
    self.assertAlmostEqual(value, expected_value)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_centrality.py:162*

### test_complete_graph

**Category**: workflow  
**Description**: Workflow: test complete graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_complete_graph(5)
centrality = rustworkx.digraph_katz_centrality(graph)
expected_value = math.sqrt(1.0 / 5.0)
for value in centrality.values():
    self.assertAlmostEqual(value, expected_value, delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_centrality.py:183*

### test_beta_scalar

**Category**: workflow  
**Description**: Workflow: test beta scalar  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.generators.directed_grid_graph(5, 2)
beta = 0.3
rx_centrality = rustworkx.katz_centrality(rx_graph, alpha=0.25, beta=beta)
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(rx_graph.edge_list())
nx_centrality = nx.katz_centrality(nx_graph, alpha=0.25, beta=beta)
for key in rx_centrality.keys():
    self.assertAlmostEqual(rx_centrality[key], nx_centrality[key], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_centrality.py:195*

### test_beta_dictionary

**Category**: workflow  
**Description**: Workflow: test beta dictionary  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.generators.directed_grid_graph(5, 2)
beta = {i: 0.1 * i ** 2 for i in range(10)}
rx_centrality = rustworkx.katz_centrality(rx_graph, alpha=0.25, beta=beta)
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(rx_graph.edge_list())
nx_centrality = nx.katz_centrality(nx_graph, alpha=0.25, beta=beta)
for key in rx_centrality.keys():
    self.assertAlmostEqual(rx_centrality[key], nx_centrality[key], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_centrality.py:208*

### test_complete_graph

**Category**: workflow  
**Description**: Workflow: test complete graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_mesh_graph(5)
centrality = rustworkx.edge_betweenness_centrality(graph)
for value in centrality.values():
    self.assertAlmostEqual(value, 0.05)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_centrality.py:228*

### test_degree_centrality_complete_digraph

**Category**: workflow  
**Description**: Workflow: test degree centrality complete digraph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
edge_list = [(self.a, self.b, 1), (self.b, self.c, 1), (self.c, self.d, 1), (self.a, self.c, 1)]
self.graph.add_edges_from(edge_list)

graph = rustworkx.generators.directed_complete_graph(5)
centrality = rustworkx.degree_centrality(graph)
expected = {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}
for k, v in centrality.items():
    self.assertAlmostEqual(v, expected[k])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_centrality.py:310*

### test_betweenness_complete_digraph

**Category**: workflow  
**Description**: Workflow: test betweenness complete digraph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_complete_graph(5)
cases = {(0,): 0.0, (0, 1): 0.0, (0, 2, 4): 0.0}
for group, expected in cases.items():
    result = rustworkx.digraph_group_betweenness_centrality(graph, list(group), normalized=True)
    self.assertAlmostEqual(result, expected, places=10)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_centrality.py:547*

### test_complete_graph

**Category**: workflow  
**Description**: Workflow: test complete graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_mesh_graph(5)
centrality = rustworkx.eigenvector_centrality(graph)
expected_value = math.sqrt(1.0 / 5.0)
for value in centrality.values():
    self.assertAlmostEqual(value, expected_value)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_centrality.py:162*

### test_complete_graph

**Category**: workflow  
**Description**: Workflow: test complete graph  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_complete_graph(5)
centrality = rustworkx.digraph_katz_centrality(graph)
expected_value = math.sqrt(1.0 / 5.0)
for value in centrality.values():
    self.assertAlmostEqual(value, expected_value, delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_centrality.py:183*

### test_beta_scalar

**Category**: workflow  
**Description**: Workflow: test beta scalar  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
rx_graph = rustworkx.generators.directed_grid_graph(5, 2)
beta = 0.3
rx_centrality = rustworkx.katz_centrality(rx_graph, alpha=0.25, beta=beta)
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(rx_graph.edge_list())
nx_centrality = nx.katz_centrality(nx_graph, alpha=0.25, beta=beta)
for key in rx_centrality.keys():
    self.assertAlmostEqual(rx_centrality[key], nx_centrality[key], delta=0.0001)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_centrality.py:195*

### test_single_predecessor

**Category**: workflow  
**Description**: Workflow: test single predecessor  
**Expected**: self.assertEqual(['a'], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res = dag.predecessors(node_c)
self.assertEqual(['a'], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pred_succ.py:19*

### test_single_predecessor_multiple_edges

**Category**: workflow  
**Description**: Workflow: test single predecessor multiple edges  
**Expected**: self.assertEqual(['a'], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
dag.add_edge(node_a, node_c, {'a': 3})
res = dag.predecessors(node_c)
self.assertEqual(['a'], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pred_succ.py:27*

### test_single_successor

**Category**: workflow  
**Description**: Workflow: test single successor  
**Expected**: self.assertEqual(['c'], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
dag.add_child(node_c, 'd', {'a': 1})
res = dag.successors(node_b)
self.assertEqual(['c'], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pred_succ.py:67*

### test_single_successor_multiple_edges

**Category**: workflow  
**Description**: Workflow: test single successor multiple edges  
**Expected**: self.assertEqual(['c'], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
dag.add_child(node_c, 'd', {'a': 1})
dag.add_edge(node_b, node_c, {'a': 3})
res = dag.successors(node_b)
self.assertEqual(['c'], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pred_succ.py:76*

### test_single_predecessor

**Category**: workflow  
**Description**: Workflow: test single predecessor  
**Expected**: self.assertEqual([], res_odd)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res_even = dag.find_predecessors_by_edge(node_c, lambda x: x['a'] % 2 == 0)
res_odd = dag.find_predecessors_by_edge(node_c, lambda x: x['a'] % 2 != 0)
self.assertEqual(['a'], res_even)
self.assertEqual([], res_odd)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pred_succ.py:117*

### test_single_predecessor_multiple_edges

**Category**: workflow  
**Description**: Workflow: test single predecessor multiple edges  
**Expected**: self.assertEqual(['a'], res_odd)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
dag.add_edge(node_a, node_c, {'a': 3})
res_even = dag.find_predecessors_by_edge(node_c, lambda x: x['a'] % 2 == 0)
res_odd = dag.find_predecessors_by_edge(node_c, lambda x: x['a'] % 2 == 0)
self.assertEqual(['a'], res_even)
self.assertEqual(['a'], res_odd)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pred_succ.py:130*

### test_many_parents

**Category**: workflow  
**Description**: Workflow: test many parents  
**Expected**: self.assertEqual([{'numeral': 9}, {'numeral': 7}, {'numeral': 5}, {'numeral': 3}, {'numeral': 1}], res_odd)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
for i in range(10):
    dag.add_parent(node_a, {'numeral': i}, {'edge': i})
res_even = dag.find_predecessors_by_edge(node_a, lambda x: x['edge'] % 2 == 0)
res_odd = dag.find_predecessors_by_edge(node_a, lambda x: x['edge'] % 2 != 0)
self.assertEqual([{'numeral': 8}, {'numeral': 6}, {'numeral': 4}, {'numeral': 2}, {'numeral': 0}], res_even)
self.assertEqual([{'numeral': 9}, {'numeral': 7}, {'numeral': 5}, {'numeral': 3}, {'numeral': 1}], res_odd)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pred_succ.py:144*

### test_single_successor

**Category**: workflow  
**Description**: Workflow: test single successor  
**Expected**: self.assertEqual([], res_odd)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
dag.add_child(node_c, 'd', {'a': 1})
res_even = dag.find_successors_by_edge(node_b, lambda x: x['a'] % 2 == 0)
res_odd = dag.find_successors_by_edge(node_b, lambda x: x['a'] % 2 != 0)
self.assertEqual(['c'], res_even)
self.assertEqual([], res_odd)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pred_succ.py:186*

### test_single_successor_multiple_edges

**Category**: workflow  
**Description**: Workflow: test single successor multiple edges  
**Expected**: self.assertEqual(['c'], res_odd)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
dag.add_child(node_c, 'd', {'a': 1})
dag.add_edge(node_b, node_c, {'a': 3})
res_even = dag.find_successors_by_edge(node_b, lambda x: x['a'] % 2 == 0)
res_odd = dag.find_successors_by_edge(node_b, lambda x: x['a'] % 2 != 0)
self.assertEqual(['c'], res_even)
self.assertEqual(['c'], res_odd)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pred_succ.py:199*

### test_many_children

**Category**: workflow  
**Description**: Workflow: test many children  
**Expected**: self.assertEqual([{'numeral': 9}, {'numeral': 7}, {'numeral': 5}, {'numeral': 3}, {'numeral': 1}], res_odd)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
for i in range(10):
    dag.add_child(node_a, {'numeral': i}, {'edge': i})
res_even = dag.find_successors_by_edge(node_a, lambda x: x['edge'] % 2 == 0)
res_odd = dag.find_successors_by_edge(node_a, lambda x: x['edge'] % 2 != 0)
self.assertEqual([{'numeral': 8}, {'numeral': 6}, {'numeral': 4}, {'numeral': 2}, {'numeral': 0}], res_even)
self.assertEqual([{'numeral': 9}, {'numeral': 7}, {'numeral': 5}, {'numeral': 3}, {'numeral': 1}], res_odd)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pred_succ.py:213*

### test_k_shortest_path_with_no_path

**Category**: workflow  
**Description**: Workflow: test k shortest path with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDiGraph()
a = g.add_node('A')
b = g.add_node('B')
path_lengths = rustworkx.digraph_k_shortest_path_lengths(g, start=a, k=1, edge_cost=float, goal=b)
expected = {}
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_k_shortest_path.py:88*

### test_k_shortest_path_with_no_path

**Category**: workflow  
**Description**: Workflow: test k shortest path with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDiGraph()
a = g.add_node('A')
b = g.add_node('B')
path_lengths = rustworkx.digraph_k_shortest_path_lengths(g, start=a, k=1, edge_cost=float, goal=b)
expected = {}
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_k_shortest_path.py:88*

### test_clique

**Category**: workflow  
**Description**: Workflow: test clique  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
N = 5
graph = rustworkx.generators.complete_graph(N, multigraph=False)
for node in range(0, N):
    expected_graph = rustworkx.PyGraph(multigraph=False)
    expected_graph.extend_from_edge_list([(i, node) for i in range(0, N) if i != node])
    complement_graph = rustworkx.local_complement(graph, node)
    self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_local_complement.py:31*

### test_empty

**Category**: workflow  
**Description**: Workflow: test empty  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
N = 5
graph = rustworkx.generators.empty_graph(N, multigraph=False)
expected_graph = rustworkx.generators.empty_graph(N, multigraph=False)
complement_graph = rustworkx.local_complement(graph, 0)
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_local_complement.py:48*

### test_clique

**Category**: workflow  
**Description**: Workflow: test clique  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
N = 5
graph = rustworkx.generators.complete_graph(N, multigraph=False)
for node in range(0, N):
    expected_graph = rustworkx.PyGraph(multigraph=False)
    expected_graph.extend_from_edge_list([(i, node) for i in range(0, N) if i != node])
    complement_graph = rustworkx.local_complement(graph, node)
    self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_local_complement.py:31*

### test_empty

**Category**: workflow  
**Description**: Workflow: test empty  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
N = 5
graph = rustworkx.generators.empty_graph(N, multigraph=False)
expected_graph = rustworkx.generators.empty_graph(N, multigraph=False)
complement_graph = rustworkx.local_complement(graph, 0)
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_local_complement.py:48*

### test_union_mismatch_edge_weight

**Category**: workflow  
**Description**: Workflow: test union mismatch edge weight  
**Expected**: self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 1, 'b')])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.add_nodes_from(['a_1', 'a_2', 'a_3'])
self.graph.extend_from_weighted_edge_list([(0, 1, 'e_1'), (1, 2, 'e_2')])

first = rustworkx.PyGraph()
nodes = first.add_nodes_from([0, 1])
first.add_edges_from([(nodes[0], nodes[1], 'a')])
second = rustworkx.PyGraph()
nodes = second.add_nodes_from([0, 1])
second.add_edges_from([(nodes[0], nodes[1], 'b')])
final = rustworkx.graph_union(first, second, merge_nodes=True, merge_edges=True)
self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 1, 'b')])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_union.py:38*

### test_union_node_hole

**Category**: workflow  
**Description**: Workflow: test union node hole  
**Expected**: self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a')])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.add_nodes_from(['a_1', 'a_2', 'a_3'])
self.graph.extend_from_weighted_edge_list([(0, 1, 'e_1'), (1, 2, 'e_2')])

first = rustworkx.PyGraph()
nodes = first.add_nodes_from([0, 1])
first.add_edges_from([(nodes[0], nodes[1], 'a')])
second = rustworkx.PyGraph()
dummy = second.add_node('dummy')
nodes = second.add_nodes_from([0, 1])
second.add_edges_from([(nodes[0], nodes[1], 'a')])
second.remove_node(dummy)
final = rustworkx.graph_union(first, second, merge_nodes=True, merge_edges=True)
self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a')])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_union.py:50*

### test_union_edge_between_merged_and_unmerged_nodes

**Category**: workflow  
**Description**: Workflow: test union edge between merged and unmerged nodes  
**Expected**: self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 2, 'b')])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.add_nodes_from(['a_1', 'a_2', 'a_3'])
self.graph.extend_from_weighted_edge_list([(0, 1, 'e_1'), (1, 2, 'e_2')])

first = rustworkx.PyGraph()
nodes = first.add_nodes_from([0, 1])
first.add_edges_from([(nodes[0], nodes[1], 'a')])
second = rustworkx.PyGraph()
nodes = second.add_nodes_from([0, 2])
second.add_edges_from([(nodes[0], nodes[1], 'b')])
final = rustworkx.graph_union(first, second, merge_nodes=True, merge_edges=True)
self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 2, 'b')])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_union.py:64*

### test_union_mismatch_edge_weight

**Category**: workflow  
**Description**: Workflow: test union mismatch edge weight  
**Expected**: self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 1, 'b')])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
first = rustworkx.PyGraph()
nodes = first.add_nodes_from([0, 1])
first.add_edges_from([(nodes[0], nodes[1], 'a')])
second = rustworkx.PyGraph()
nodes = second.add_nodes_from([0, 1])
second.add_edges_from([(nodes[0], nodes[1], 'b')])
final = rustworkx.graph_union(first, second, merge_nodes=True, merge_edges=True)
self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 1, 'b')])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_union.py:38*

### test_union_node_hole

**Category**: workflow  
**Description**: Workflow: test union node hole  
**Expected**: self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a')])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
first = rustworkx.PyGraph()
nodes = first.add_nodes_from([0, 1])
first.add_edges_from([(nodes[0], nodes[1], 'a')])
second = rustworkx.PyGraph()
dummy = second.add_node('dummy')
nodes = second.add_nodes_from([0, 1])
second.add_edges_from([(nodes[0], nodes[1], 'a')])
second.remove_node(dummy)
final = rustworkx.graph_union(first, second, merge_nodes=True, merge_edges=True)
self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a')])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_union.py:50*

### test_union_edge_between_merged_and_unmerged_nodes

**Category**: workflow  
**Description**: Workflow: test union edge between merged and unmerged nodes  
**Expected**: self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 2, 'b')])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
first = rustworkx.PyGraph()
nodes = first.add_nodes_from([0, 1])
first.add_edges_from([(nodes[0], nodes[1], 'a')])
second = rustworkx.PyGraph()
nodes = second.add_nodes_from([0, 2])
second.add_edges_from([(nodes[0], nodes[1], 'b')])
final = rustworkx.graph_union(first, second, merge_nodes=True, merge_edges=True)
self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a'), (0, 2, 'b')])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_union.py:64*

### test_forest

**Category**: workflow  
**Description**: Workflow: test forest  
**Expected**: self.assertEqualEdgeList(forest_expected_edges, msf_graph.weighted_edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 3), (self.a, self.d, 2), (self.b, self.c, 4), (self.c, self.d, 1), (self.a, self.f, 1), (self.b, self.f, 6), (self.d, self.e, 5), (self.c, self.e, 7)]
self.graph.add_edges_from(edge_list)
self.expected_edges = [(self.a, self.b, 3), (self.a, self.d, 2), (self.c, self.d, 1), (self.a, self.f, 1), (self.d, self.e, 5)]

s = self.graph.add_node('S')
t = self.graph.add_node('T')
u = self.graph.add_node('U')
self.graph.add_edges_from([(s, t, 10), (t, u, 9), (s, u, 8)])
forest_expected_edges = self.expected_edges + [(s, u, 8), (t, u, 9)]
msf_graph = rustworkx.minimum_spanning_tree(self.graph, weight_fn=lambda x: x)
self.assertEqual(self.graph.nodes(), msf_graph.nodes())
self.assertEqual(len(self.graph.nodes()) - 2, len(msf_graph.edge_list()))
self.assertEqualEdgeList(forest_expected_edges, msf_graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_mst.py:65*

### test_forest

**Category**: workflow  
**Description**: Workflow: test forest  
**Expected**: self.assertEqualEdgeList(forest_expected_edges, msf_graph.weighted_edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
s = self.graph.add_node('S')
t = self.graph.add_node('T')
u = self.graph.add_node('U')
self.graph.add_edges_from([(s, t, 10), (t, u, 9), (s, u, 8)])
forest_expected_edges = self.expected_edges + [(s, u, 8), (t, u, 9)]
msf_graph = rustworkx.minimum_spanning_tree(self.graph, weight_fn=lambda x: x)
self.assertEqual(self.graph.nodes(), msf_graph.nodes())
self.assertEqual(len(self.graph.nodes()) - 2, len(msf_graph.edge_list()))
self.assertEqualEdgeList(forest_expected_edges, msf_graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_mst.py:65*

### test_dijkstra_length_with_no_path

**Category**: workflow  
**Description**: Workflow: test dijkstra length with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)

g = rustworkx.PyDiGraph()
a = g.add_node('A')
b = g.add_node('B')
path_lengths = rustworkx.digraph_dijkstra_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
expected = {}
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra.py:47*

### test_dijkstra_has_path

**Category**: workflow  
**Description**: Workflow: test dijkstra has path  
**Expected**: self.assertFalse(rustworkx.digraph_has_path(g, a, c))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)

g = rustworkx.PyDiGraph()
a = g.add_node('A')
b = g.add_node('B')
c = g.add_node('C')
edge_list = [(a, b, 7), (c, b, 9), (c, b, 10)]
g.add_edges_from(edge_list)
self.assertFalse(rustworkx.digraph_has_path(g, a, c))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra.py:73*

### test_dijkstra_with_no_path

**Category**: workflow  
**Description**: Workflow: test dijkstra with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)

g = rustworkx.PyDiGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.digraph_dijkstra_shortest_path_lengths(g, a, lambda x: float(x))
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra.py:166*

### test_dijkstra_path_with_no_path

**Category**: workflow  
**Description**: Workflow: test dijkstra path with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)

g = rustworkx.PyDiGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.digraph_dijkstra_shortest_paths(g, a)
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra.py:174*

### test_dijkstra_with_disconnected_nodes

**Category**: workflow  
**Description**: Workflow: test dijkstra with disconnected nodes  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)

g = rustworkx.PyDiGraph()
a = g.add_node('A')
b = g.add_child(a, 'B', 1.2)
g.add_node('C')
g.add_parent(b, 'D', 2.4)
path = rustworkx.digraph_dijkstra_shortest_path_lengths(g, a, lambda x: x)
expected = {1: 1.2}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra.py:182*

### test_dijkstra_length_with_no_path

**Category**: workflow  
**Description**: Workflow: test dijkstra length with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDiGraph()
a = g.add_node('A')
b = g.add_node('B')
path_lengths = rustworkx.digraph_dijkstra_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
expected = {}
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra.py:47*

### test_dijkstra_has_path

**Category**: workflow  
**Description**: Workflow: test dijkstra has path  
**Expected**: self.assertFalse(rustworkx.digraph_has_path(g, a, c))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDiGraph()
a = g.add_node('A')
b = g.add_node('B')
c = g.add_node('C')
edge_list = [(a, b, 7), (c, b, 9), (c, b, 10)]
g.add_edges_from(edge_list)
self.assertFalse(rustworkx.digraph_has_path(g, a, c))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra.py:73*

### test_dijkstra_with_no_path

**Category**: workflow  
**Description**: Workflow: test dijkstra with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDiGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.digraph_dijkstra_shortest_path_lengths(g, a, lambda x: float(x))
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra.py:166*

### test_dijkstra_path_with_no_path

**Category**: workflow  
**Description**: Workflow: test dijkstra path with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDiGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.digraph_dijkstra_shortest_paths(g, a)
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra.py:174*

### test_dijkstra_with_disconnected_nodes

**Category**: workflow  
**Description**: Workflow: test dijkstra with disconnected nodes  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDiGraph()
a = g.add_node('A')
b = g.add_child(a, 'B', 1.2)
g.add_node('C')
g.add_parent(b, 'D', 2.4)
path = rustworkx.digraph_dijkstra_shortest_path_lengths(g, a, lambda x: x)
expected = {1: 1.2}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra.py:182*

### test_deepcopy_with_holes

**Category**: workflow  
**Description**: Workflow: test deepcopy with holes  
**Expected**: self.assertEqual([node_a, node_c], dag_b.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDAG()
node_a = dag_a.add_node('a_1')
node_b = dag_a.add_node('a_2')
dag_a.add_edge(node_a, node_b, 'edge_1')
node_c = dag_a.add_node('a_3')
dag_a.add_edge(node_b, node_c, 'edge_2')
dag_a.remove_node(node_b)
dag_b = copy.deepcopy(dag_a)
self.assertIsInstance(dag_b, rustworkx.PyDAG)
self.assertEqual([node_a, node_c], dag_b.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_deepcopy.py:28*

### test_deepcopy_check_cycle

**Category**: workflow  
**Description**: Workflow: test deepcopy check cycle  
**Expected**: self.assertFalse(graph_d.check_cycle)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph(check_cycle=True)
graph_b = copy.deepcopy(graph_a)
graph_c = rustworkx.PyDiGraph(check_cycle=False)
graph_d = copy.deepcopy(graph_c)
self.assertTrue(graph_b.check_cycle)
self.assertFalse(graph_d.check_cycle)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_deepcopy.py:50*

### test_deepcopy_different_objects

**Category**: workflow  
**Description**: Workflow: test deepcopy different objects  
**Expected**: self.assertIsNot(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph(attrs=[1])
node_a = graph_a.add_node([2])
node_b = graph_a.add_child(node_a, [3], [4])
graph_b = copy.deepcopy(graph_a)
self.assertEqual(graph_a.attrs, graph_b.attrs)
self.assertIsNot(graph_a.attrs, graph_b.attrs)
self.assertEqual(graph_a[node_a], graph_b[node_a])
self.assertIsNot(graph_a[node_a], graph_b[node_a])
self.assertEqual(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))
self.assertIsNot(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_deepcopy.py:58*

### test_deepcopy_with_holes

**Category**: workflow  
**Description**: Workflow: test deepcopy with holes  
**Expected**: self.assertEqual([node_a, node_c], dag_b.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag_a = rustworkx.PyDAG()
node_a = dag_a.add_node('a_1')
node_b = dag_a.add_node('a_2')
dag_a.add_edge(node_a, node_b, 'edge_1')
node_c = dag_a.add_node('a_3')
dag_a.add_edge(node_b, node_c, 'edge_2')
dag_a.remove_node(node_b)
dag_b = copy.deepcopy(dag_a)
self.assertIsInstance(dag_b, rustworkx.PyDAG)
self.assertEqual([node_a, node_c], dag_b.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_deepcopy.py:28*

### test_deepcopy_check_cycle

**Category**: workflow  
**Description**: Workflow: test deepcopy check cycle  
**Expected**: self.assertFalse(graph_d.check_cycle)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph(check_cycle=True)
graph_b = copy.deepcopy(graph_a)
graph_c = rustworkx.PyDiGraph(check_cycle=False)
graph_d = copy.deepcopy(graph_c)
self.assertTrue(graph_b.check_cycle)
self.assertFalse(graph_d.check_cycle)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_deepcopy.py:50*

### test_deepcopy_different_objects

**Category**: workflow  
**Description**: Workflow: test deepcopy different objects  
**Expected**: self.assertIsNot(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyDiGraph(attrs=[1])
node_a = graph_a.add_node([2])
node_b = graph_a.add_child(node_a, [3], [4])
graph_b = copy.deepcopy(graph_a)
self.assertEqual(graph_a.attrs, graph_b.attrs)
self.assertIsNot(graph_a.attrs, graph_b.attrs)
self.assertEqual(graph_a[node_a], graph_b[node_a])
self.assertIsNot(graph_a[node_a], graph_b[node_a])
self.assertEqual(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))
self.assertIsNot(graph_a.get_edge_data(node_a, node_b), graph_b.get_edge_data(node_a, node_b))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_deepcopy.py:58*

### test_condensation

**Category**: workflow  
**Description**: Workflow: test condensation  
**Expected**: self.assertIn('b->e', weight)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.node_a = self.graph.add_node('a')
self.node_b = self.graph.add_node('b')
self.node_c = self.graph.add_node('c')
self.node_d = self.graph.add_node('d')
self.node_e = self.graph.add_node('e')
self.node_f = self.graph.add_node('f')
self.node_g = self.graph.add_node('g')
self.node_h = self.graph.add_node('h')
self.graph.add_edge(self.node_a, self.node_b, 'a->b')
self.graph.add_edge(self.node_b, self.node_c, 'b->c')
self.graph.add_edge(self.node_c, self.node_d, 'c->d')
self.graph.add_edge(self.node_d, self.node_a, 'd->a')
self.graph.add_edge(self.node_b, self.node_e, 'b->e')
self.graph.add_edge(self.node_e, self.node_f, 'e->f')
self.graph.add_edge(self.node_f, self.node_g, 'f->g')
self.graph.add_edge(self.node_g, self.node_h, 'g->h')
self.graph.add_edge(self.node_h, self.node_e, 'h->e')

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

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_strongly_connected.py:131*

### test_condensation_with_sccs_argument

**Category**: workflow  
**Description**: Workflow: test condensation with sccs argument  
**Expected**: self.assertIn('b->e', weight)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.node_a = self.graph.add_node('a')
self.node_b = self.graph.add_node('b')
self.node_c = self.graph.add_node('c')
self.node_d = self.graph.add_node('d')
self.node_e = self.graph.add_node('e')
self.node_f = self.graph.add_node('f')
self.node_g = self.graph.add_node('g')
self.node_h = self.graph.add_node('h')
self.graph.add_edge(self.node_a, self.node_b, 'a->b')
self.graph.add_edge(self.node_b, self.node_c, 'b->c')
self.graph.add_edge(self.node_c, self.node_d, 'c->d')
self.graph.add_edge(self.node_d, self.node_a, 'd->a')
self.graph.add_edge(self.node_b, self.node_e, 'b->e')
self.graph.add_edge(self.node_e, self.node_f, 'e->f')
self.graph.add_edge(self.node_f, self.node_g, 'f->g')
self.graph.add_edge(self.node_g, self.node_h, 'g->h')
self.graph.add_edge(self.node_h, self.node_e, 'h->e')

sccs = rustworkx.strongly_connected_components(self.graph)
condensed_graph = rustworkx.condensation(self.graph, sccs=sccs)
condensed_graph.attrs['node_map']
self.assertEqual(len(condensed_graph.node_indices()), len(sccs))
self.assertEqual(len(condensed_graph.edge_indices()), 1)
nodes = list(condensed_graph.nodes())
scc_sets = [set(n) for n in nodes]
self.assertIn(set(['a', 'b', 'c', 'd']), scc_sets)
self.assertIn(set(['e', 'f', 'g', 'h']), scc_sets)
weight = condensed_graph.edges()[0]
self.assertIn('b->e', weight)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_strongly_connected.py:156*

### test_condensation

**Category**: workflow  
**Description**: Workflow: test condensation  
**Expected**: self.assertIn('b->e', weight)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_strongly_connected.py:131*

### test_condensation_with_sccs_argument

**Category**: workflow  
**Description**: Workflow: test condensation with sccs argument  
**Expected**: self.assertIn('b->e', weight)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
sccs = rustworkx.strongly_connected_components(self.graph)
condensed_graph = rustworkx.condensation(self.graph, sccs=sccs)
condensed_graph.attrs['node_map']
self.assertEqual(len(condensed_graph.node_indices()), len(sccs))
self.assertEqual(len(condensed_graph.edge_indices()), 1)
nodes = list(condensed_graph.nodes())
scc_sets = [set(n) for n in nodes]
self.assertIn(set(['a', 'b', 'c', 'd']), scc_sets)
self.assertIn(set(['e', 'f', 'g', 'h']), scc_sets)
weight = condensed_graph.edges()[0]
self.assertIn('b->e', weight)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_strongly_connected.py:156*

### test_remove_node

**Category**: workflow  
**Description**: Workflow: test remove node  
**Expected**: self.assertEqual([0, 2], dag.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'Edgy')
dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_node(node_b)
res = dag.nodes()
self.assertEqual(['a', 'c'], res)
self.assertEqual([0, 2], dag.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_nodes.py:39*

### test_remove_nodes_from

**Category**: workflow  
**Description**: Workflow: test remove nodes from  
**Expected**: self.assertEqual([0], dag.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'Edgy')
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_nodes_from([node_b, node_c])
res = dag.nodes()
self.assertEqual(['a'], res)
self.assertEqual([0], dag.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_nodes.py:59*

### test_remove_nodes_from_gen

**Category**: workflow  
**Description**: Workflow: test remove nodes from gen  
**Expected**: self.assertEqual([0], graph.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
node_a = graph.add_node('a')
node_b = graph.add_child(node_a, 'b', 'Edgy')
node_c = graph.add_child(node_b, 'c', 'Edgy_mk2')
graph.remove_nodes_from((n for n in [node_b, node_c]))
res = graph.nodes()
self.assertEqual(['a'], res)
self.assertEqual([0], graph.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_nodes.py:69*

### test_remove_nodes_from_with_invalid_index

**Category**: workflow  
**Description**: Workflow: test remove nodes from with invalid index  
**Expected**: self.assertEqual([0], dag.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'Edgy')
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_nodes_from([node_b, node_c, 76])
res = dag.nodes()
self.assertEqual(['a'], res)
self.assertEqual([0], dag.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_nodes.py:79*

### test_remove_nodes_retain_edges_single_edge

**Category**: workflow  
**Description**: Workflow: test remove nodes retain edges single edge  
**Expected**: self.assertEqual(dag.get_all_edge_data(node_a, node_c), ['Edgy'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'Edgy')
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_node_retain_edges(node_b)
res = dag.nodes()
self.assertEqual(['a', 'c'], res)
self.assertEqual([0, 2], dag.node_indexes())
self.assertTrue(dag.has_edge(node_a, node_c))
self.assertEqual(dag.get_all_edge_data(node_a, node_c), ['Edgy'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_nodes.py:95*

### test_remove_nodes_retain_edges_single_edge_outgoing_weight

**Category**: workflow  
**Description**: Workflow: test remove nodes retain edges single edge outgoing weight  
**Expected**: self.assertEqual(dag.get_all_edge_data(node_a, node_c), ['Edgy_mk2'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'Edgy')
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_node_retain_edges(node_b, use_outgoing=True)
res = dag.nodes()
self.assertEqual(['a', 'c'], res)
self.assertEqual([0, 2], dag.node_indexes())
self.assertTrue(dag.has_edge(node_a, node_c))
self.assertEqual(dag.get_all_edge_data(node_a, node_c), ['Edgy_mk2'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_nodes.py:107*

### test_remove_nodes_retain_edges_multiple_in_edges

**Category**: workflow  
**Description**: Workflow: test remove nodes retain edges multiple in edges  
**Expected**: self.assertTrue(dag.has_edge(node_d, node_c))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_d = dag.add_node('d')
node_b = dag.add_child(node_a, 'b', 'Edgy')
dag.add_edge(node_d, node_b, 'Multiple in edgy')
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_node_retain_edges(node_b)
res = dag.nodes()
self.assertEqual(['a', 'd', 'c'], res)
self.assertEqual([0, 1, 3], dag.node_indexes())
self.assertTrue(dag.has_edge(node_a, node_c))
self.assertTrue(dag.has_edge(node_d, node_c))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_nodes.py:119*

### test_remove_nodes_retain_edges_multiple_out_edges

**Category**: workflow  
**Description**: Workflow: test remove nodes retain edges multiple out edges  
**Expected**: self.assertTrue(dag.has_edge(node_a, node_d))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_d = dag.add_node('d')
node_b = dag.add_child(node_a, 'b', 'Edgy')
dag.add_edge(node_b, node_d, 'Multiple out edgy')
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_node_retain_edges(node_b)
res = dag.nodes()
self.assertEqual(['a', 'd', 'c'], res)
self.assertEqual([0, 1, 3], dag.node_indexes())
self.assertTrue(dag.has_edge(node_a, node_c))
self.assertTrue(dag.has_edge(node_a, node_d))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_nodes.py:133*

### test_remove_nodes_retain_edges_multiple_in_and_out_edges

**Category**: workflow  
**Description**: Workflow: test remove nodes retain edges multiple in and out edges  
**Expected**: self.assertTrue(dag.has_edge(node_e, node_d))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_d = dag.add_node('d')
node_e = dag.add_node('e')
node_b = dag.add_child(node_a, 'b', 'Edgy')
dag.add_edge(node_b, node_d, 'Multiple out edgy')
dag.add_edge(node_e, node_b, 'multiple in edgy')
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_node_retain_edges(node_b)
res = dag.nodes()
self.assertEqual(['a', 'd', 'e', 'c'], res)
self.assertEqual([0, 1, 2, 4], dag.node_indexes())
self.assertTrue(dag.has_edge(node_a, node_c))
self.assertTrue(dag.has_edge(node_a, node_d))
self.assertTrue(dag.has_edge(node_e, node_c))
self.assertTrue(dag.has_edge(node_e, node_d))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_nodes.py:147*

### test_remove_node_retain_edges_with_condition

**Category**: workflow  
**Description**: Workflow: test remove node retain edges with condition  
**Expected**: self.assertTrue(dag.has_edge(node_e, node_d))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_d = dag.add_node('d')
node_e = dag.add_node('e')
node_b = dag.add_child(node_a, 'b', 'Edgy')
dag.add_edge(node_b, node_d, 'Multiple out edgy')
dag.add_edge(node_e, node_b, 'multiple in edgy')
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_node_retain_edges(node_b, condition=lambda a, b: a == 'multiple in edgy')
res = dag.nodes()
self.assertEqual(['a', 'd', 'e', 'c'], res)
self.assertEqual([0, 1, 2, 4], dag.node_indexes())
self.assertFalse(dag.has_edge(node_a, node_c))
self.assertFalse(dag.has_edge(node_a, node_d))
self.assertTrue(dag.has_edge(node_e, node_c))
self.assertTrue(dag.has_edge(node_e, node_d))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_nodes.py:165*

### test_topo_sort

**Category**: workflow  
**Description**: Workflow: test topo sort  
**Expected**: self.assertEqual(nodes, [])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 2), (1, 2), (2, 3), (2, 4), (3, 5)])

sorter = rustworkx.TopologicalSorter(self.graph)
nodes = sorter.get_ready()
self.assertEqual(nodes, [0, 1])
sorter.done(nodes)
nodes = sorter.get_ready()
self.assertEqual(nodes, [2])
sorter.done(nodes)
nodes = sorter.get_ready()
self.assertEqual(nodes, [4, 3])
sorter.done(nodes)
nodes = sorter.get_ready()
self.assertEqual(nodes, [5])
sorter.done(nodes)
nodes = sorter.get_ready()
self.assertEqual(nodes, [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_toposort.py:31*

### test_topo_sort_single_indices

**Category**: workflow  
**Description**: Workflow: test topo sort single indices  
**Expected**: self.assertFalse(sorter.is_active())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 2), (1, 2), (2, 3), (2, 4), (3, 5)])

sorter = rustworkx.TopologicalSorter(self.graph)
nodes = sorter.get_ready()
self.assertEqual(set(nodes), {0, 1})
sorter.done(0)
sorter.done(1)
nodes = sorter.get_ready()
self.assertEqual(set(nodes), {2})
sorter.done(2)
nodes = sorter.get_ready()
self.assertEqual(set(nodes), {3, 4})
sorter.done(3)
self.assertEqual(set(sorter.get_ready()), {5})
sorter.done(5)
self.assertEqual(set(sorter.get_ready()), set())
self.assertTrue(sorter.is_active())
sorter.done(4)
self.assertEqual(set(sorter.get_ready()), set())
self.assertFalse(sorter.is_active())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_toposort.py:48*

### test_topo_sort_progress_if_graph_has_cycle_and_cycle_check_disabled

**Category**: workflow  
**Description**: Workflow: test topo sort progress if graph has cycle and cycle check disabled  
**Expected**: self.assertFalse(sorter.is_active())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 2), (1, 2), (2, 3), (2, 4), (3, 5)])

graph = rustworkx.generators.directed_cycle_graph(5)
starting_node = graph.add_node('starting node')
graph.add_edge(starting_node, 0, 'starting edge')
sorter = rustworkx.TopologicalSorter(graph, check_cycle=False)
nodes = sorter.get_ready()
self.assertEqual(nodes, [starting_node])
sorter.done(nodes)
self.assertFalse(sorter.is_active())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_toposort.py:95*

### test_initial

**Category**: workflow  
**Description**: Workflow: test initial  
**Expected**: self.assertFalse(sorter.is_active())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 2), (1, 2), (2, 3), (2, 4), (3, 5)])

dag = rustworkx.PyDiGraph()
dag.add_nodes_from(range(9))
dag.add_edges_from_no_data([(0, 1), (0, 2), (1, 3), (2, 4), (3, 4), (4, 5), (5, 6), (4, 7), (6, 8), (7, 8)])
sorter = rustworkx.TopologicalSorter(dag, initial=[6, 7])
self.assertEqual(set(sorter.get_ready()), {6, 7})
sorter.done([6, 7])
self.assertEqual(set(sorter.get_ready()), {8})
sorter.done([8])
self.assertFalse(sorter.is_active())
initial_sorter = rustworkx.TopologicalSorter(dag, initial=[0])
base_sorter = rustworkx.TopologicalSorter(dag)
bases = []
initials = []
while (base_ready := base_sorter.get_ready()):
    bases.append(base_ready)
    initials.append(initial_sorter.get_ready())
    base_sorter.done(bases[-1])
    initial_sorter.done(initials[-1])
self.assertEqual(bases, initials)
self.assertFalse(initial_sorter.is_active())
sorter = rustworkx.TopologicalSorter(dag, initial=[7])
self.assertEqual(set(sorter.get_ready()), {7})
sorter.done([7])
self.assertFalse(sorter.is_active())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_toposort.py:120*

### test_initial_reverse

**Category**: workflow  
**Description**: Workflow: test initial reverse  
**Expected**: self.assertFalse(sorter.is_active())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 2), (1, 2), (2, 3), (2, 4), (3, 5)])

dag = rustworkx.PyDiGraph()
dag.add_nodes_from(range(9))
dag.add_edges_from_no_data([(0, 1), (0, 2), (1, 3), (2, 4), (3, 4), (4, 5), (5, 6), (4, 7), (6, 8), (7, 8)])
sorter = rustworkx.TopologicalSorter(dag, reverse=True, initial=[1, 2])
self.assertEqual(set(sorter.get_ready()), {1, 2})
sorter.done([1, 2])
self.assertEqual(set(sorter.get_ready()), {0})
sorter.done([0])
self.assertFalse(sorter.is_active())
initial_sorter = rustworkx.TopologicalSorter(dag, reverse=True, initial=[8])
base_sorter = rustworkx.TopologicalSorter(dag, reverse=True)
bases = []
initials = []
while (base_ready := base_sorter.get_ready()):
    bases.append(base_ready)
    initials.append(initial_sorter.get_ready())
    base_sorter.done(bases[-1])
    initial_sorter.done(initials[-1])
self.assertEqual(bases, initials)
self.assertFalse(initial_sorter.is_active())
sorter = rustworkx.TopologicalSorter(dag, reverse=True, initial=[1])
self.assertEqual(set(sorter.get_ready()), {1})
sorter.done([1])
self.assertFalse(sorter.is_active())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_toposort.py:165*

### test_topo_sort

**Category**: workflow  
**Description**: Workflow: test topo sort  
**Expected**: self.assertEqual(nodes, [])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
sorter = rustworkx.TopologicalSorter(self.graph)
nodes = sorter.get_ready()
self.assertEqual(nodes, [0, 1])
sorter.done(nodes)
nodes = sorter.get_ready()
self.assertEqual(nodes, [2])
sorter.done(nodes)
nodes = sorter.get_ready()
self.assertEqual(nodes, [4, 3])
sorter.done(nodes)
nodes = sorter.get_ready()
self.assertEqual(nodes, [5])
sorter.done(nodes)
nodes = sorter.get_ready()
self.assertEqual(nodes, [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_toposort.py:31*

### test_topo_sort_single_indices

**Category**: workflow  
**Description**: Workflow: test topo sort single indices  
**Expected**: self.assertFalse(sorter.is_active())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
sorter = rustworkx.TopologicalSorter(self.graph)
nodes = sorter.get_ready()
self.assertEqual(set(nodes), {0, 1})
sorter.done(0)
sorter.done(1)
nodes = sorter.get_ready()
self.assertEqual(set(nodes), {2})
sorter.done(2)
nodes = sorter.get_ready()
self.assertEqual(set(nodes), {3, 4})
sorter.done(3)
self.assertEqual(set(sorter.get_ready()), {5})
sorter.done(5)
self.assertEqual(set(sorter.get_ready()), set())
self.assertTrue(sorter.is_active())
sorter.done(4)
self.assertEqual(set(sorter.get_ready()), set())
self.assertFalse(sorter.is_active())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_toposort.py:48*

### test_topo_sort_progress_if_graph_has_cycle_and_cycle_check_disabled

**Category**: workflow  
**Description**: Workflow: test topo sort progress if graph has cycle and cycle check disabled  
**Expected**: self.assertFalse(sorter.is_active())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.directed_cycle_graph(5)
starting_node = graph.add_node('starting node')
graph.add_edge(starting_node, 0, 'starting edge')
sorter = rustworkx.TopologicalSorter(graph, check_cycle=False)
nodes = sorter.get_ready()
self.assertEqual(nodes, [starting_node])
sorter.done(nodes)
self.assertFalse(sorter.is_active())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_toposort.py:95*

### test_initial

**Category**: workflow  
**Description**: Workflow: test initial  
**Expected**: self.assertFalse(sorter.is_active())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDiGraph()
dag.add_nodes_from(range(9))
dag.add_edges_from_no_data([(0, 1), (0, 2), (1, 3), (2, 4), (3, 4), (4, 5), (5, 6), (4, 7), (6, 8), (7, 8)])
sorter = rustworkx.TopologicalSorter(dag, initial=[6, 7])
self.assertEqual(set(sorter.get_ready()), {6, 7})
sorter.done([6, 7])
self.assertEqual(set(sorter.get_ready()), {8})
sorter.done([8])
self.assertFalse(sorter.is_active())
initial_sorter = rustworkx.TopologicalSorter(dag, initial=[0])
base_sorter = rustworkx.TopologicalSorter(dag)
bases = []
initials = []
while (base_ready := base_sorter.get_ready()):
    bases.append(base_ready)
    initials.append(initial_sorter.get_ready())
    base_sorter.done(bases[-1])
    initial_sorter.done(initials[-1])
self.assertEqual(bases, initials)
self.assertFalse(initial_sorter.is_active())
sorter = rustworkx.TopologicalSorter(dag, initial=[7])
self.assertEqual(set(sorter.get_ready()), {7})
sorter.done([7])
self.assertFalse(sorter.is_active())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_toposort.py:120*

### test_initial_reverse

**Category**: workflow  
**Description**: Workflow: test initial reverse  
**Expected**: self.assertFalse(sorter.is_active())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDiGraph()
dag.add_nodes_from(range(9))
dag.add_edges_from_no_data([(0, 1), (0, 2), (1, 3), (2, 4), (3, 4), (4, 5), (5, 6), (4, 7), (6, 8), (7, 8)])
sorter = rustworkx.TopologicalSorter(dag, reverse=True, initial=[1, 2])
self.assertEqual(set(sorter.get_ready()), {1, 2})
sorter.done([1, 2])
self.assertEqual(set(sorter.get_ready()), {0})
sorter.done([0])
self.assertFalse(sorter.is_active())
initial_sorter = rustworkx.TopologicalSorter(dag, reverse=True, initial=[8])
base_sorter = rustworkx.TopologicalSorter(dag, reverse=True)
bases = []
initials = []
while (base_ready := base_sorter.get_ready()):
    bases.append(base_ready)
    initials.append(initial_sorter.get_ready())
    base_sorter.done(bases[-1])
    initial_sorter.done(initials[-1])
self.assertEqual(bases, initials)
self.assertFalse(initial_sorter.is_active())
sorter = rustworkx.TopologicalSorter(dag, reverse=True, initial=[1])
self.assertEqual(set(sorter.get_ready()), {1})
sorter.done([1])
self.assertFalse(sorter.is_active())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_toposort.py:165*

### test_astar_null_heuristic

**Category**: workflow  
**Description**: Workflow: test astar null heuristic  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDAG()
a = g.add_node('A')
b = g.add_node('B')
c = g.add_node('C')
d = g.add_node('D')
e = g.add_node('E')
f = g.add_node('F')
g.add_edge(a, b, 7)
g.add_edge(c, a, 9)
g.add_edge(a, d, 14)
g.add_edge(b, c, 10)
g.add_edge(d, c, 2)
g.add_edge(d, e, 9)
g.add_edge(b, f, 15)
g.add_edge(c, f, 11)
g.add_edge(e, f, 6)
path = rustworkx.digraph_astar_shortest_path(g, a, lambda goal: goal == 'E', lambda x: float(x), lambda y: 0)
expected = [a, d, e]
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_astar.py:19*

### test_astar_manhattan_heuristic

**Category**: workflow  
**Description**: Workflow: test astar manhattan heuristic  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDAG()
a = g.add_node((0.0, 0.0))
b = g.add_node((2.0, 0.0))
c = g.add_node((1.0, 1.0))
d = g.add_node((0.0, 2.0))
e = g.add_node((3.0, 3.0))
f = g.add_node((4.0, 2.0))
no_path = g.add_node((5.0, 5.0))
g.add_edge(a, b, 2.0)
g.add_edge(a, d, 4.0)
g.add_edge(b, c, 1.0)
g.add_edge(b, f, 7.0)
g.add_edge(c, e, 5.0)
g.add_edge(e, f, 1.0)
g.add_edge(d, e, 1.0)

def heuristic_func(f):
    x1, x2 = f
    return abs(x2 - x1)

def finish_func(node, x):
    return x == g.get_node_data(node)
expected = [[0], [0, 1], [0, 1, 2], [0, 3], [0, 3, 4], [0, 3, 4, 5]]
for index, end in enumerate([a, b, c, d, e, f]):
    path = rustworkx.digraph_astar_shortest_path(g, a, lambda finish: finish_func(end, finish), lambda x: float(x), heuristic_func)
    self.assertEqual(expected[index], path)
with self.assertRaises(rustworkx.NoPathFound):
    rustworkx.digraph_astar_shortest_path(g, a, lambda finish: finish_func(no_path, finish), lambda x: float(x), heuristic_func)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_astar.py:42*

### test_astar_null_heuristic

**Category**: workflow  
**Description**: Workflow: test astar null heuristic  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDAG()
a = g.add_node('A')
b = g.add_node('B')
c = g.add_node('C')
d = g.add_node('D')
e = g.add_node('E')
f = g.add_node('F')
g.add_edge(a, b, 7)
g.add_edge(c, a, 9)
g.add_edge(a, d, 14)
g.add_edge(b, c, 10)
g.add_edge(d, c, 2)
g.add_edge(d, e, 9)
g.add_edge(b, f, 15)
g.add_edge(c, f, 11)
g.add_edge(e, f, 6)
path = rustworkx.digraph_astar_shortest_path(g, a, lambda goal: goal == 'E', lambda x: float(x), lambda y: 0)
expected = [a, d, e]
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_astar.py:19*

### test_astar_manhattan_heuristic

**Category**: workflow  
**Description**: Workflow: test astar manhattan heuristic  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyDAG()
a = g.add_node((0.0, 0.0))
b = g.add_node((2.0, 0.0))
c = g.add_node((1.0, 1.0))
d = g.add_node((0.0, 2.0))
e = g.add_node((3.0, 3.0))
f = g.add_node((4.0, 2.0))
no_path = g.add_node((5.0, 5.0))
g.add_edge(a, b, 2.0)
g.add_edge(a, d, 4.0)
g.add_edge(b, c, 1.0)
g.add_edge(b, f, 7.0)
g.add_edge(c, e, 5.0)
g.add_edge(e, f, 1.0)
g.add_edge(d, e, 1.0)

def heuristic_func(f):
    x1, x2 = f
    return abs(x2 - x1)

def finish_func(node, x):
    return x == g.get_node_data(node)
expected = [[0], [0, 1], [0, 1, 2], [0, 3], [0, 3, 4], [0, 3, 4, 5]]
for index, end in enumerate([a, b, c, d, e, f]):
    path = rustworkx.digraph_astar_shortest_path(g, a, lambda finish: finish_func(end, finish), lambda x: float(x), heuristic_func)
    self.assertEqual(expected[index], path)
with self.assertRaises(rustworkx.NoPathFound):
    rustworkx.digraph_astar_shortest_path(g, a, lambda finish: finish_func(no_path, finish), lambda x: float(x), heuristic_func)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_astar.py:42*

### test_digraph_to_dot_to_file

**Category**: workflow  
**Description**: Workflow: test digraph to dot to file  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

graph = rustworkx.PyDiGraph()
graph.add_node({'color': 'black', 'fillcolor': 'green', 'label': 'a', 'style': 'filled'})
graph.add_node({'color': 'black', 'fillcolor': 'red', 'label': 'a', 'style': 'filled'})
graph.add_edge(0, 1, dict(label='1', name='1'))
expected = 'digraph {\n0 [color=black, fillcolor=green, label="a", style=filled];\n1 [color=black, fillcolor=red, label="a", style=filled];\n0 -> 1 [label="1", name=1];\n}\n'
res = graph.to_dot(lambda node: node, lambda edge: edge, filename=self.path)
self.addCleanup(os.remove, self.path)
self.assertIsNone(res)
with open(self.path) as fd:
    res = fd.read()
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dot.py:26*

### test_digraph_to_dot_to_file

**Category**: workflow  
**Description**: Workflow: test digraph to dot to file  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
graph.add_node({'color': 'black', 'fillcolor': 'green', 'label': 'a', 'style': 'filled'})
graph.add_node({'color': 'black', 'fillcolor': 'red', 'label': 'a', 'style': 'filled'})
graph.add_edge(0, 1, dict(label='1', name='1'))
expected = 'digraph {\n0 [color=black, fillcolor=green, label="a", style=filled];\n1 [color=black, fillcolor=red, label="a", style=filled];\n0 -> 1 [label="1", name=1];\n}\n'
res = graph.to_dot(lambda node: node, lambda edge: edge, filename=self.path)
self.addCleanup(os.remove, self.path)
self.assertIsNone(res)
with open(self.path) as fd:
    res = fd.read()
self.assertEqual(expected, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dot.py:26*

### test_vs_dijkstra_all_pairs

**Category**: workflow  
**Description**: Workflow: test vs dijkstra all pairs  
**Expected**: self.assertEqual(result, expected)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
a = graph.add_node('A')
b = graph.add_node('B')
c = graph.add_node('C')
d = graph.add_node('D')
e = graph.add_node('E')
f = graph.add_node('F')
edge_list = [(a, b, 7), (c, a, 9), (a, d, 14), (b, c, 10), (d, c, 2), (d, e, 9), (b, f, 15), (c, f, 11), (e, f, 6)]
graph.add_edges_from(edge_list)
dijkstra_lengths = rustworkx.graph_all_pairs_dijkstra_path_lengths(graph, float)
expected = {k: {**v, k: 0.0} for k, v in dijkstra_lengths.items()}
result = rustworkx.graph_floyd_warshall(graph, float, parallel_threshold=self.parallel_threshold)
self.assertEqual(result, expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_floyd_warshall.py:23*

### test_vs_dijkstra_all_pairs_with_node_removal

**Category**: workflow  
**Description**: Workflow: test vs dijkstra all pairs with node removal  
**Expected**: self.assertEqual(result, expected)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
a = graph.add_node('A')
b = graph.add_node('B')
c = graph.add_node('C')
d = graph.add_node('D')
e = graph.add_node('E')
f = graph.add_node('F')
edge_list = [(a, b, 7), (c, a, 9), (a, d, 14), (b, c, 10), (d, c, 2), (d, e, 9), (b, f, 15), (c, f, 11), (e, f, 6)]
graph.add_edges_from(edge_list)
graph.remove_node(d)
dijkstra_lengths = rustworkx.graph_all_pairs_dijkstra_path_lengths(graph, float)
expected = {k: {**v, k: 0.0} for k, v in dijkstra_lengths.items()}
result = rustworkx.graph_floyd_warshall(graph, float, parallel_threshold=self.parallel_threshold)
self.assertEqual(result, expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_floyd_warshall.py:54*

### test_vs_dijkstra_all_pairs

**Category**: workflow  
**Description**: Workflow: test vs dijkstra all pairs  
**Expected**: self.assertEqual(result, expected)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
a = graph.add_node('A')
b = graph.add_node('B')
c = graph.add_node('C')
d = graph.add_node('D')
e = graph.add_node('E')
f = graph.add_node('F')
edge_list = [(a, b, 7), (c, a, 9), (a, d, 14), (b, c, 10), (d, c, 2), (d, e, 9), (b, f, 15), (c, f, 11), (e, f, 6)]
graph.add_edges_from(edge_list)
dijkstra_lengths = rustworkx.graph_all_pairs_dijkstra_path_lengths(graph, float)
expected = {k: {**v, k: 0.0} for k, v in dijkstra_lengths.items()}
result = rustworkx.graph_floyd_warshall(graph, float, parallel_threshold=self.parallel_threshold)
self.assertEqual(result, expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_floyd_warshall.py:23*

### test_vs_dijkstra_all_pairs_with_node_removal

**Category**: workflow  
**Description**: Workflow: test vs dijkstra all pairs with node removal  
**Expected**: self.assertEqual(result, expected)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
a = graph.add_node('A')
b = graph.add_node('B')
c = graph.add_node('C')
d = graph.add_node('D')
e = graph.add_node('E')
f = graph.add_node('F')
edge_list = [(a, b, 7), (c, a, 9), (a, d, 14), (b, c, 10), (d, c, 2), (d, e, 9), (b, f, 15), (c, f, 11), (e, f, 6)]
graph.add_edges_from(edge_list)
graph.remove_node(d)
dijkstra_lengths = rustworkx.graph_all_pairs_dijkstra_path_lengths(graph, float)
expected = {k: {**v, k: 0.0} for k, v in dijkstra_lengths.items()}
result = rustworkx.graph_floyd_warshall(graph, float, parallel_threshold=self.parallel_threshold)
self.assertEqual(result, expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_floyd_warshall.py:54*

### test_write_edge_list_round_trip

**Category**: workflow  
**Description**: Workflow: test write edge list round trip  
**Expected**: self.assertEqual(expected, new_graph.weighted_edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
path = os.path.join(tempfile.gettempdir(), 'round_trip.txt')
graph = rustworkx.generators.directed_star_graph(5)
count = iter(range(5))

def weight_fn(edge):
    return str(next(count))
graph.write_edge_list(path, weight_fn=weight_fn)
self.addCleanup(os.remove, path)
new_graph = rustworkx.PyDiGraph.read_edge_list(path)
expected = [(0, 1, '0'), (0, 2, '1'), (0, 3, '2'), (0, 4, '3')]
self.assertEqual(expected, new_graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edgelist.py:189*

### test_write_edge_list_round_trip

**Category**: workflow  
**Description**: Workflow: test write edge list round trip  
**Expected**: self.assertEqual(expected, new_graph.weighted_edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
path = os.path.join(tempfile.gettempdir(), 'round_trip.txt')
graph = rustworkx.generators.directed_star_graph(5)
count = iter(range(5))

def weight_fn(edge):
    return str(next(count))
graph.write_edge_list(path, weight_fn=weight_fn)
self.addCleanup(os.remove, path)
new_graph = rustworkx.PyDiGraph.read_edge_list(path)
expected = [(0, 1, '0'), (0, 2, '1'), (0, 3, '2'), (0, 4, '3')]
self.assertEqual(expected, new_graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edgelist.py:189*

### test_invalid_positions_error

**Category**: workflow  
**Description**: Workflow: test invalid positions error  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rx.PyGraph()
graph.add_nodes_from([0, 1])
positions = [[0.0, 0.0]]
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_routing(graph, positions, 0, 1)
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_success_rate(graph, positions)
positions = [[0.0, 0.0], [0.0, 0.0, 0.0]]
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_routing(graph, positions, 0, 1)
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_success_rate(graph, positions)
positions = [[0.0, 0.0], [0.0]]
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_routing(graph, positions, 0, 1)
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_success_rate(graph, positions)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_geometry.py:41*

### test_correct_successful_path

**Category**: workflow  
**Description**: Workflow: test correct successful path  
**Expected**: self.assertAlmostEqual(dist, total_length(path))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rx.PyGraph()
graph.add_nodes_from(range(7))
graph.add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (1, 4), (4, 5), (2, 5), (5, 6)])
positions = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [2.5, 0.0], [1.0, 1.0], [2.0, 1.0], [3.0, 1.0]]
path, dist = rx.hyperbolic_greedy_routing(graph, positions, 0, 3)

def hyperbolic_dist(x, y):
    x_array = np.asarray(x)
    y_array = np.asarray(y)
    dot = np.sum(x_array * y_array)
    arg = np.sqrt(1 + np.sum(x_array * x_array)) * np.sqrt(1 + np.sum(y_array * y_array)) - dot
    return 0 if arg < 0 else np.arccosh(arg)

def total_length(path):
    return sum((hyperbolic_dist(positions[i], positions[j]) for i, j in zip(path[:-1], np.roll(path, -1)[:-1])))
self.assertEqual(path, [0, 1, 2, 3])
self.assertAlmostEqual(dist, total_length(path))
path, dist = rx.hyperbolic_greedy_routing(graph, positions, 0, 6)
self.assertEqual(path, [0, 1, 2, 5, 6])
self.assertAlmostEqual(dist, total_length(path))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_geometry.py:80*

### test_invalid_positions_error

**Category**: workflow  
**Description**: Workflow: test invalid positions error  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rx.PyGraph()
graph.add_nodes_from([0, 1])
positions = [[0.0, 0.0]]
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_routing(graph, positions, 0, 1)
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_success_rate(graph, positions)
positions = [[0.0, 0.0], [0.0, 0.0, 0.0]]
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_routing(graph, positions, 0, 1)
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_success_rate(graph, positions)
positions = [[0.0, 0.0], [0.0]]
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_routing(graph, positions, 0, 1)
with self.assertRaises(ValueError):
    rx.hyperbolic_greedy_success_rate(graph, positions)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_geometry.py:41*

### test_correct_successful_path

**Category**: workflow  
**Description**: Workflow: test correct successful path  
**Expected**: self.assertAlmostEqual(dist, total_length(path))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rx.PyGraph()
graph.add_nodes_from(range(7))
graph.add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (1, 4), (4, 5), (2, 5), (5, 6)])
positions = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [2.5, 0.0], [1.0, 1.0], [2.0, 1.0], [3.0, 1.0]]
path, dist = rx.hyperbolic_greedy_routing(graph, positions, 0, 3)

def hyperbolic_dist(x, y):
    x_array = np.asarray(x)
    y_array = np.asarray(y)
    dot = np.sum(x_array * y_array)
    arg = np.sqrt(1 + np.sum(x_array * x_array)) * np.sqrt(1 + np.sum(y_array * y_array)) - dot
    return 0 if arg < 0 else np.arccosh(arg)

def total_length(path):
    return sum((hyperbolic_dist(positions[i], positions[j]) for i, j in zip(path[:-1], np.roll(path, -1)[:-1])))
self.assertEqual(path, [0, 1, 2, 3])
self.assertAlmostEqual(dist, total_length(path))
path, dist = rx.hyperbolic_greedy_routing(graph, positions, 0, 6)
self.assertEqual(path, [0, 1, 2, 5, 6])
self.assertAlmostEqual(dist, total_length(path))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_geometry.py:80*

### test_digraph_dijkstra_tree_edges

**Category**: workflow  
**Description**: Workflow: test digraph dijkstra tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

class DijkstraTreeEdgesRecorder(rustworkx.visit.DijkstraVisitor):

    def __init__(self):
        self.edges = []
        self.parents = dict()

    def discover_vertex(self, v, _):
        u = self.parents.get(v, None)
        if u is not None:
            self.edges.append((u, v))

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u
vis = DijkstraTreeEdgesRecorder()
rustworkx.digraph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra_search.py:34*

### test_digraph_dijkstra_tree_edges_no_starting_point

**Category**: workflow  
**Description**: Workflow: test digraph dijkstra tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3), (4, 7)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

class DijkstraTreeEdgesRecorder(rustworkx.visit.DijkstraVisitor):

    def __init__(self):
        self.edges = []
        self.parents = dict()

    def discover_vertex(self, v, _):
        u = self.parents.get(v, None)
        if u is not None:
            self.edges.append((u, v))

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u
vis = DijkstraTreeEdgesRecorder()
rustworkx.digraph_dijkstra_search(self.graph, None, float, vis)
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra_search.py:53*

### test_digraph_dijkstra_goal_search_with_stop_search_exception

**Category**: workflow  
**Description**: Workflow: test digraph dijkstra goal search with stop search exception  
**Expected**: self.assertEqual(vis.opt_goal_cost, 4.0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

class GoalSearch(rustworkx.visit.DijkstraVisitor):
    goal = 3

    def __init__(self):
        self.parents = {}
        self.opt_goal_cost = None

    def discover_vertex(self, v, score):
        if v == self.goal:
            self.opt_goal_cost = score
            raise rustworkx.visit.StopSearch

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u

    def reconstruct_path(self):
        v = self.goal
        path = [v]
        while v in self.parents:
            v = self.parents[v]
            path.append(v)
        path.reverse()
        return path
vis = GoalSearch()
rustworkx.digraph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.reconstruct_path(), [0, 2, 5, 3])
self.assertEqual(vis.opt_goal_cost, 4.0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra_search.py:72*

### test_digraph_dijkstra_tree_edges

**Category**: workflow  
**Description**: Workflow: test digraph dijkstra tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
class DijkstraTreeEdgesRecorder(rustworkx.visit.DijkstraVisitor):

    def __init__(self):
        self.edges = []
        self.parents = dict()

    def discover_vertex(self, v, _):
        u = self.parents.get(v, None)
        if u is not None:
            self.edges.append((u, v))

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u
vis = DijkstraTreeEdgesRecorder()
rustworkx.digraph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra_search.py:34*

### test_digraph_dijkstra_tree_edges_no_starting_point

**Category**: workflow  
**Description**: Workflow: test digraph dijkstra tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3), (4, 7)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
class DijkstraTreeEdgesRecorder(rustworkx.visit.DijkstraVisitor):

    def __init__(self):
        self.edges = []
        self.parents = dict()

    def discover_vertex(self, v, _):
        u = self.parents.get(v, None)
        if u is not None:
            self.edges.append((u, v))

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u
vis = DijkstraTreeEdgesRecorder()
rustworkx.digraph_dijkstra_search(self.graph, None, float, vis)
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra_search.py:53*

### test_digraph_dijkstra_goal_search_with_stop_search_exception

**Category**: workflow  
**Description**: Workflow: test digraph dijkstra goal search with stop search exception  
**Expected**: self.assertEqual(vis.opt_goal_cost, 4.0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
class GoalSearch(rustworkx.visit.DijkstraVisitor):
    goal = 3

    def __init__(self):
        self.parents = {}
        self.opt_goal_cost = None

    def discover_vertex(self, v, score):
        if v == self.goal:
            self.opt_goal_cost = score
            raise rustworkx.visit.StopSearch

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u

    def reconstruct_path(self):
        v = self.goal
        path = [v]
        while v in self.parents:
            v = self.parents[v]
            path.append(v)
        path.reverse()
        return path
vis = GoalSearch()
rustworkx.digraph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.reconstruct_path(), [0, 2, 5, 3])
self.assertEqual(vis.opt_goal_cost, 4.0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra_search.py:72*

### test_simple_graph

**Category**: workflow  
**Description**: Workflow: test simple graph  
**Expected**: self.assertEqual({0: 0, 1: 1, 2: 1}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 1)
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, 1)
res = rustworkx.graph_greedy_color(graph)
self.assertEqual({0: 0, 1: 1, 2: 1}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_coloring.py:24*

### test_simple_graph_large_degree

**Category**: workflow  
**Description**: Workflow: test simple graph large degree  
**Expected**: self.assertEqual({0: 0, 1: 1, 2: 1}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 1)
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, 1)
graph.add_edge(node_a, node_c, 1)
graph.add_edge(node_a, node_c, 1)
graph.add_edge(node_a, node_c, 1)
graph.add_edge(node_a, node_c, 1)
res = rustworkx.graph_greedy_color(graph)
self.assertEqual({0: 0, 1: 1, 2: 1}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_coloring.py:34*

### test_simple_graph_with_preset

**Category**: workflow  
**Description**: Workflow: test simple graph with preset  
**Expected**: self.assertEqual({0: 1, 1: 0, 2: 0}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
def preset(node_idx):
    if node_idx == 0:
        return 1
    return None
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 1)
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, 1)
res = rustworkx.graph_greedy_color(graph, preset)
self.assertEqual({0: 1, 1: 0, 2: 0}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_coloring.py:48*

### test_simple_graph_large_degree_with_preset

**Category**: workflow  
**Description**: Workflow: test simple graph large degree with preset  
**Expected**: self.assertEqual({0: 1, 1: 0, 2: 0}, res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
def preset(node_idx):
    if node_idx == 0:
        return 1
    return None
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 1)
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, 1)
graph.add_edge(node_a, node_c, 1)
graph.add_edge(node_a, node_c, 1)
graph.add_edge(node_a, node_c, 1)
graph.add_edge(node_a, node_c, 1)
res = rustworkx.graph_greedy_color(graph, preset)
self.assertEqual({0: 1, 1: 0, 2: 0}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_coloring.py:63*

### test_greedy_strategies

**Category**: workflow  
**Description**: Workflow: test greedy strategies  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
[a, b, c, d, e, f, g, h] = graph.add_nodes_from(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
graph.add_edges_from([(a, b, 1), (a, c, 1), (a, d, 1), (d, e, 1), (e, f, 1), (f, g, 1), (f, h, 1)])
with self.subTest():
    res = rustworkx.graph_greedy_color(graph)
    self.assertEqual({a: 0, b: 1, c: 1, d: 1, e: 2, f: 0, g: 1, h: 1}, res)
with self.subTest(strategy=rustworkx.ColoringStrategy.Degree):
    res = rustworkx.graph_greedy_color(graph, strategy=rustworkx.ColoringStrategy.Degree)
    self.assertEqual({a: 0, b: 1, c: 1, d: 1, e: 2, f: 0, g: 1, h: 1}, res)
with self.subTest(strategy=rustworkx.ColoringStrategy.Saturation):
    res = rustworkx.graph_greedy_color(graph, strategy=rustworkx.ColoringStrategy.Saturation)
    self.assertEqual({a: 0, b: 1, c: 1, d: 1, e: 0, f: 1, g: 0, h: 0}, res)
with self.subTest(strategy=rustworkx.ColoringStrategy.IndependentSet):
    res = rustworkx.graph_greedy_color(graph, strategy=rustworkx.ColoringStrategy.IndependentSet)
    self.assertEqual({a: 0, b: 1, c: 1, d: 1, e: 0, f: 1, g: 0, h: 0}, res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_coloring.py:90*

### test_graph

**Category**: workflow  
**Description**: Workflow: test graph  
**Expected**: self.assertEqual({0: 1, 1: 2, 2: 0, 3: 1}, edge_colors)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
node_d = graph.add_node('d')
node_e = graph.add_node('e')
graph.add_edge(node_a, node_b, 1)
graph.add_edge(node_a, node_c, 1)
graph.add_edge(node_a, node_d, 1)
graph.add_edge(node_d, node_e, 1)
edge_colors = rustworkx.graph_greedy_edge_color(graph)
self.assertEqual({0: 1, 1: 2, 2: 0, 3: 1}, edge_colors)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_coloring.py:119*

### test_graph_with_holes

**Category**: workflow  
**Description**: Workflow: Graph with missing node and edge indices.  
**Expected**: self.assertEqual({0: 0, 3: 0}, edge_colors)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Graph with missing node and edge indices.'
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
node_d = graph.add_node('d')
node_e = graph.add_node('e')
graph.add_edge(node_a, node_b, 1)
graph.add_edge(node_b, node_c, 1)
graph.add_edge(node_c, node_d, 1)
graph.add_edge(node_d, node_e, 1)
graph.remove_node(node_c)
edge_colors = rustworkx.graph_greedy_edge_color(graph)
self.assertEqual({0: 0, 3: 0}, edge_colors)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_coloring.py:135*

### test_graph_multiple_edges

**Category**: workflow  
**Description**: Workflow: Graph with multiple edges between two nodes.  
**Expected**: self.assertEqual({0: 0, 1: 1, 2: 2, 3: 3}, edge_colors)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Graph with multiple edges between two nodes.'
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 1)
graph.add_edge(node_a, node_b, 1)
graph.add_edge(node_a, node_b, 1)
graph.add_edge(node_a, node_b, 1)
edge_colors = rustworkx.graph_greedy_edge_color(graph)
self.assertEqual({0: 0, 1: 1, 2: 2, 3: 3}, edge_colors)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_coloring.py:162*

### test_greedy_strategies

**Category**: workflow  
**Description**: Workflow: test greedy strategies  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.complete_graph(4)
with self.subTest():
    edge_colors = rustworkx.graph_greedy_edge_color(graph)
    self.assertEqual({0: 0, 1: 1, 2: 2, 3: 2, 4: 1, 5: 0}, edge_colors)
with self.subTest(strategy=rustworkx.ColoringStrategy.Degree):
    edge_colors = rustworkx.graph_greedy_edge_color(graph, strategy=rustworkx.ColoringStrategy.Degree)
    self.assertEqual({0: 0, 1: 1, 2: 2, 3: 2, 4: 1, 5: 0}, edge_colors)
with self.subTest(strategy=rustworkx.ColoringStrategy.Saturation):
    edge_colors = rustworkx.graph_greedy_edge_color(graph, strategy=rustworkx.ColoringStrategy.Saturation)
    self.assertEqual({0: 0, 1: 2, 2: 1, 3: 1, 4: 2, 5: 0}, edge_colors)
with self.subTest(strategy=rustworkx.ColoringStrategy.IndependentSet):
    edge_colors = rustworkx.graph_greedy_edge_color(graph, strategy=rustworkx.ColoringStrategy.IndependentSet)
    self.assertEqual({0: 0, 1: 2, 2: 1, 3: 1, 4: 2, 5: 0}, edge_colors)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_coloring.py:179*

### test_greedy_strategies_with_preset

**Category**: workflow  
**Description**: Workflow: test greedy strategies with preset  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
def preset(edge_idx):
    if edge_idx == 0:
        return 1
    elif edge_idx == 3:
        return 0
    else:
        return None
graph = rustworkx.generators.complete_graph(4)
with self.subTest():
    edge_colors = rustworkx.graph_greedy_edge_color(graph, preset_color_fn=preset)
    self.assertEqual({0: 1, 1: 2, 2: 0, 3: 0, 4: 2, 5: 1}, edge_colors)
with self.subTest(strategy=rustworkx.ColoringStrategy.Degree):
    edge_colors = rustworkx.graph_greedy_edge_color(graph, preset_color_fn=preset, strategy=rustworkx.ColoringStrategy.Degree)
    self.assertEqual({0: 1, 1: 2, 2: 0, 3: 0, 4: 2, 5: 1}, edge_colors)
with self.subTest(strategy=rustworkx.ColoringStrategy.Saturation):
    edge_colors = rustworkx.graph_greedy_edge_color(graph, preset_color_fn=preset, strategy=rustworkx.ColoringStrategy.Saturation)
    self.assertEqual({0: 1, 1: 2, 2: 0, 3: 0, 4: 2, 5: 1}, edge_colors)
with self.subTest(strategy=rustworkx.ColoringStrategy.IndependentSet):
    edge_colors = rustworkx.graph_greedy_edge_color(graph, preset_color_fn=preset, strategy=rustworkx.ColoringStrategy.IndependentSet)
    self.assertEqual({0: 1, 1: 2, 2: 0, 3: 0, 4: 2, 5: 1}, edge_colors)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_coloring.py:204*

### test_simple_dag_composition

**Category**: workflow  
**Description**: Workflow: test simple dag composition  
**Expected**: self.assertEqual([0, 1, 2, 3, 4], rustworkx.topological_sort(dag))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
dag.check_cycle = True
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
dag_other = rustworkx.PyDAG()
node_d = dag_other.add_node('d')
dag_other.add_child(node_d, 'e', {'a': 3})
res = dag.compose(dag_other, {node_c: (node_d, {'b': 1})})
self.assertEqual({0: 3, 1: 4}, res)
self.assertEqual([0, 1, 2, 3, 4], rustworkx.topological_sort(dag))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_compose.py:19*

### test_simple_dag_composition

**Category**: workflow  
**Description**: Workflow: test simple dag composition  
**Expected**: self.assertEqual([0, 1, 2, 3, 4], rustworkx.topological_sort(dag))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
dag.check_cycle = True
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
dag_other = rustworkx.PyDAG()
node_d = dag_other.add_node('d')
dag_other.add_child(node_d, 'e', {'a': 3})
res = dag.compose(dag_other, {node_c: (node_d, {'b': 1})})
self.assertEqual({0: 3, 1: 4}, res)
self.assertEqual([0, 1, 2, 3, 4], rustworkx.topological_sort(dag))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_compose.py:19*

### test_graph

**Category**: workflow  
**Description**: Workflow: test graph  
**Expected**: self.assertEqual(expected, chains)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])
return super().setUp()

edges = [(0, 2), (0, 3), (1, 4), (4, 9), (5, 7), (0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 8), (5, 6), (6, 7), (8, 9)]
graph = rustworkx.PyGraph()
graph.extend_from_edge_list(edges)
chains = rustworkx.chain_decomposition(graph, source=0)
expected = [[(0, 3), (3, 2), (2, 1), (1, 0)], [(0, 2)], [(1, 4), (4, 2)], [(4, 9), (9, 8), (8, 4)], [(5, 7), (7, 6), (6, 5)]]
self.assertEqual(expected, chains)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_chain_decomposition.py:34*

### test_graph

**Category**: workflow  
**Description**: Workflow: test graph  
**Expected**: self.assertEqual(expected, chains)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
edges = [(0, 2), (0, 3), (1, 4), (4, 9), (5, 7), (0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 8), (5, 6), (6, 7), (8, 9)]
graph = rustworkx.PyGraph()
graph.extend_from_edge_list(edges)
chains = rustworkx.chain_decomposition(graph, source=0)
expected = [[(0, 3), (3, 2), (2, 1), (1, 0)], [(0, 2)], [(1, 4), (4, 2)], [(4, 9), (9, 8), (8, 4)], [(5, 7), (7, 6), (6, 5)]]
self.assertEqual(expected, chains)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_chain_decomposition.py:34*

### test_write

**Category**: workflow  
**Description**: Workflow: test write  
**Expected**: self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_xml = self.graphml_xml_example()
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(graph_xml)
    fd.flush()
    graphml = rustworkx.read_graphml(fd.name)
graph = graphml[0]
with tempfile.NamedTemporaryFile('wt') as fd:
    keys = [rustworkx.GraphMLKey('d0', rustworkx.GraphMLDomain.Node, 'color', rustworkx.GraphMLType.String, 'yellow'), rustworkx.GraphMLKey('d1', rustworkx.GraphMLDomain.Edge, 'fidelity', rustworkx.GraphMLType.Float, 0.95)]
    rustworkx.write_graphml(graph, fd.name, keys=keys)
    graphml = rustworkx.read_graphml(fd.name)
graph_reread = graphml[0]
edges = [(graph[s]['id'], graph[t]['id'], weight) for s, t, weight in graph.weighted_edge_list()]
self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_graphml.py:103*

### test_write_without_keys

**Category**: workflow  
**Description**: Workflow: test write without keys  
**Expected**: self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_xml = self.graphml_xml_example()
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(graph_xml)
    fd.flush()
    graphml = rustworkx.read_graphml(fd.name)
graph = graphml[0]
with tempfile.NamedTemporaryFile('wt') as fd:
    rustworkx.write_graphml(graph, fd.name)
    graphml = rustworkx.read_graphml(fd.name)
graph_reread = graphml[0]
edges = [(graph[s]['id'], graph[t]['id'], weight) for s, t, weight in graph.weighted_edge_list()]
self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_graphml.py:135*

### test_write_gzipped

**Category**: workflow  
**Description**: Workflow: test write gzipped  
**Expected**: self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_xml = self.graphml_xml_example()
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(graph_xml)
    fd.flush()
    graphml = rustworkx.read_graphml(fd.name)
graph = graphml[0]
with tempfile.NamedTemporaryFile('wt') as fd:
    newname = f'{fd.name}.gz'
    rustworkx.write_graphml(graph, newname)
    graphml = rustworkx.read_graphml(newname)
graph_reread = graphml[0]
edges = [(graph[s]['id'], graph[t]['id'], weight) for s, t, weight in graph.weighted_edge_list()]
self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_graphml.py:198*

### test_write_key_for_graph

**Category**: workflow  
**Description**: Workflow: test write key for graph  
**Expected**: self.assertGraphEqual(graph, nodes, edges, directed=True, attrs={'id': 'G', 'test': True})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_xml = self.HEADER.format('\n            <key id="d0" for="graph" attr.name="test" attr.type="boolean"/>\n            <graph id="G" edgedefault="directed">\n            <data key="d0">true</data>\n            <node id="n0"/>\n            </graph>\n            ')
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(graph_xml)
    fd.flush()
    graphml = rustworkx.read_graphml(fd.name)
with tempfile.NamedTemporaryFile('wt') as fd:
    rustworkx.write_graphml(graphml[0], fd.name)
    graphml = rustworkx.read_graphml(fd.name)
graph = graphml[0]
nodes = [{'id': 'n0'}]
edges = []
self.assertGraphEqual(graph, nodes, edges, directed=True, attrs={'id': 'G', 'test': True})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_graphml.py:292*

### test_write_key_for_all

**Category**: workflow  
**Description**: Workflow: test write key for all  
**Expected**: self.assertGraphEqual(graph, nodes, edges, directed=True, attrs={'id': 'G', 'test': "I'm a graph."})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_xml = self.HEADER.format('\n            <key id="d0" for="all" attr.name="test" attr.type="string"/>\n            <graph id="G" edgedefault="directed">\n            <data key="d0">I\'m a graph.</data>\n            <node id="n0">\n                <data key="d0">I\'m a node.</data>\n            </node>\n            <node id="n1">\n                <data key="d0">I\'m a node.</data>\n            </node>\n            <edge source="n0" target="n1">\n                <data key="d0">I\'m an edge.</data>\n            </edge>\n            </graph>\n            ')
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(graph_xml)
    fd.flush()
    graphml = rustworkx.read_graphml(fd.name)
keys = [rustworkx.GraphMLKey('d0', rustworkx.GraphMLDomain.All, 'test', rustworkx.GraphMLType.String, None)]
with tempfile.NamedTemporaryFile('wt') as fd:
    rustworkx.write_graphml(graphml[0], fd.name, keys=keys)
    graphml = rustworkx.read_graphml(fd.name)
graph = graphml[0]
nodes = [{'id': 'n0', 'test': "I'm a node."}, {'id': 'n1', 'test': "I'm a node."}]
edges = [('n0', 'n1', {'test': "I'm an edge."})]
self.assertGraphEqual(graph, nodes, edges, directed=True, attrs={'id': 'G', 'test': "I'm a graph."})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_graphml.py:348*

### test_write_key_undefined

**Category**: workflow  
**Description**: Workflow: test write key undefined  
**Expected**: self.assertGraphEqual(graph, nodes, edges, directed=True, attrs={'id': 'G'})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_xml = self.HEADER.format('\n            <key id="d0" for="node" attr.name="test" attr.type="boolean"/>\n            <graph id="G" edgedefault="directed">\n            <node id="n0">\n                <data key="d0">true</data>\n            </node>\n            <node id="n1"/>\n            </graph>\n            ')
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(graph_xml)
    fd.flush()
    graphml = rustworkx.read_graphml(fd.name)
with tempfile.NamedTemporaryFile('wt') as fd:
    rustworkx.write_graphml(graphml[0], fd.name)
    graphml = rustworkx.read_graphml(fd.name)
graph = graphml[0]
nodes = [{'id': 'n0', 'test': True}, {'id': 'n1', 'test': None}]
edges = []
self.assertGraphEqual(graph, nodes, edges, directed=True, attrs={'id': 'G'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_graphml.py:418*

### test_write

**Category**: workflow  
**Description**: Workflow: test write  
**Expected**: self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_xml = self.graphml_xml_example()
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(graph_xml)
    fd.flush()
    graphml = rustworkx.read_graphml(fd.name)
graph = graphml[0]
with tempfile.NamedTemporaryFile('wt') as fd:
    keys = [rustworkx.GraphMLKey('d0', rustworkx.GraphMLDomain.Node, 'color', rustworkx.GraphMLType.String, 'yellow'), rustworkx.GraphMLKey('d1', rustworkx.GraphMLDomain.Edge, 'fidelity', rustworkx.GraphMLType.Float, 0.95)]
    rustworkx.write_graphml(graph, fd.name, keys=keys)
    graphml = rustworkx.read_graphml(fd.name)
graph_reread = graphml[0]
edges = [(graph[s]['id'], graph[t]['id'], weight) for s, t, weight in graph.weighted_edge_list()]
self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_graphml.py:103*

### test_write_without_keys

**Category**: workflow  
**Description**: Workflow: test write without keys  
**Expected**: self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_xml = self.graphml_xml_example()
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(graph_xml)
    fd.flush()
    graphml = rustworkx.read_graphml(fd.name)
graph = graphml[0]
with tempfile.NamedTemporaryFile('wt') as fd:
    rustworkx.write_graphml(graph, fd.name)
    graphml = rustworkx.read_graphml(fd.name)
graph_reread = graphml[0]
edges = [(graph[s]['id'], graph[t]['id'], weight) for s, t, weight in graph.weighted_edge_list()]
self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_graphml.py:135*

### test_write_gzipped

**Category**: workflow  
**Description**: Workflow: test write gzipped  
**Expected**: self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_xml = self.graphml_xml_example()
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(graph_xml)
    fd.flush()
    graphml = rustworkx.read_graphml(fd.name)
graph = graphml[0]
with tempfile.NamedTemporaryFile('wt') as fd:
    newname = f'{fd.name}.gz'
    rustworkx.write_graphml(graph, newname)
    graphml = rustworkx.read_graphml(newname)
graph_reread = graphml[0]
edges = [(graph[s]['id'], graph[t]['id'], weight) for s, t, weight in graph.weighted_edge_list()]
self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_graphml.py:198*

### test_write_key_for_graph

**Category**: workflow  
**Description**: Workflow: test write key for graph  
**Expected**: self.assertGraphEqual(graph, nodes, edges, directed=True, attrs={'id': 'G', 'test': True})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_xml = self.HEADER.format('\n            <key id="d0" for="graph" attr.name="test" attr.type="boolean"/>\n            <graph id="G" edgedefault="directed">\n            <data key="d0">true</data>\n            <node id="n0"/>\n            </graph>\n            ')
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(graph_xml)
    fd.flush()
    graphml = rustworkx.read_graphml(fd.name)
with tempfile.NamedTemporaryFile('wt') as fd:
    rustworkx.write_graphml(graphml[0], fd.name)
    graphml = rustworkx.read_graphml(fd.name)
graph = graphml[0]
nodes = [{'id': 'n0'}]
edges = []
self.assertGraphEqual(graph, nodes, edges, directed=True, attrs={'id': 'G', 'test': True})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_graphml.py:292*

### test_linear

**Category**: workflow  
**Description**: Workflow: Longest depth for a simple dag.

a
|
b
|        c d
|        e |
| |
f g  
**Expected**: self.assertEqual([node_a, node_b, node_c, node_e, node_f], rustworkx.dag_longest_path(dag))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Longest depth for a simple dag.\n\n        a\n        |\n        b\n        |        c d\n        |        e |\n        | |\n        f g\n        '
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {})
node_c = dag.add_child(node_b, 'c', {})
dag.add_child(node_b, 'd', {})
node_e = dag.add_child(node_c, 'e', {})
node_f = dag.add_child(node_e, 'f', {})
dag.add_child(node_c, 'g', {})
self.assertEqual(4, rustworkx.dag_longest_path_length(dag))
self.assertEqual([node_a, node_b, node_c, node_e, node_f], rustworkx.dag_longest_path(dag))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_depth.py:19*

### test_less_linear

**Category**: workflow  
**Description**: Workflow: test less linear  
**Expected**: self.assertEqual([node_a, node_b, node_c, node_d, node_e], rustworkx.dag_longest_path(dag))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {})
node_c = dag.add_child(node_b, 'c', {})
node_d = dag.add_child(node_c, 'd', {})
node_e = dag.add_child(node_d, 'e', {})
dag.add_edge(node_a, node_c, {})
dag.add_edge(node_a, node_e, {})
dag.add_edge(node_c, node_e, {})
self.assertEqual(4, rustworkx.dag_longest_path_length(dag))
self.assertEqual([node_a, node_b, node_c, node_d, node_e], rustworkx.dag_longest_path(dag))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_depth.py:46*

### test_linear_with_weight

**Category**: workflow  
**Description**: Workflow: Longest depth for a simple dag.

a
|
b
|        c d
|        e |
| |
f g  
**Expected**: self.assertEqual(23, rustworkx.dag_longest_path_length(dag, lambda _, __, weight: weight))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Longest depth for a simple dag.\n\n        a\n        |\n        b\n        |        c d\n        |        e |\n        | |\n        f g\n        '
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 4)
node_c = dag.add_child(node_b, 'c', 4)
dag.add_child(node_b, 'd', 5)
node_e = dag.add_child(node_c, 'e', 2)
dag.add_child(node_e, 'f', 2)
node_g = dag.add_child(node_c, 'g', 15)
self.assertEqual([node_a, node_b, node_c, node_g], rustworkx.dag_longest_path(dag, lambda _, __, weight: weight))
self.assertEqual(23, rustworkx.dag_longest_path_length(dag, lambda _, __, weight: weight))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_depth.py:90*

### test_less_linear_with_weight

**Category**: workflow  
**Description**: Workflow: test less linear with weight  
**Expected**: self.assertEqual([node_a, node_c, node_e], rustworkx.dag_longest_path(dag, weight_fn=lambda _, __, weight: weight))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 1)
node_c = dag.add_child(node_b, 'c', 1)
node_d = dag.add_child(node_c, 'd', 1)
node_e = dag.add_child(node_d, 'e', 1)
dag.add_edge(node_a, node_c, 3)
dag.add_edge(node_a, node_e, 3)
dag.add_edge(node_c, node_e, 3)
self.assertEqual(6, rustworkx.dag_longest_path_length(dag, weight_fn=lambda _, __, weight: weight))
self.assertEqual([node_a, node_c, node_e], rustworkx.dag_longest_path(dag, weight_fn=lambda _, __, weight: weight))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_depth.py:141*

### test_linear_with_weight

**Category**: workflow  
**Description**: Workflow: Longest depth for a simple dag.

a
|
b
|        c d
|        e |
| |
f g  
**Expected**: self.assertEqual([node_a, node_b, node_c, node_g], rustworkx.dag_weighted_longest_path(dag, lambda _, __, weight: float(weight)))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Longest depth for a simple dag.\n\n        a\n        |\n        b\n        |        c d\n        |        e |\n        | |\n        f g\n        '
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 4)
node_c = dag.add_child(node_b, 'c', 4)
dag.add_child(node_b, 'd', 5)
node_e = dag.add_child(node_c, 'e', 2)
dag.add_child(node_e, 'f', 2)
node_g = dag.add_child(node_c, 'g', 15)
self.assertEqual(23.0, rustworkx.dag_weighted_longest_path_length(dag, lambda _, __, weight: float(weight)))
self.assertEqual([node_a, node_b, node_c, node_g], rustworkx.dag_weighted_longest_path(dag, lambda _, __, weight: float(weight)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_depth.py:184*

### test_less_linear_with_weight

**Category**: workflow  
**Description**: Workflow: test less linear with weight  
**Expected**: self.assertEqual([node_a, node_c, node_e], rustworkx.dag_weighted_longest_path(dag, weight_fn=lambda _, __, weight: float(weight)))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 1)
node_c = dag.add_child(node_b, 'c', 1)
node_d = dag.add_child(node_c, 'd', 1)
node_e = dag.add_child(node_d, 'e', 1)
dag.add_edge(node_a, node_c, 3)
dag.add_edge(node_a, node_e, 3)
dag.add_edge(node_c, node_e, 3)
self.assertEqual(6.0, rustworkx.dag_weighted_longest_path_length(dag, weight_fn=lambda _, __, weight: float(weight)))
self.assertEqual([node_a, node_c, node_e], rustworkx.dag_weighted_longest_path(dag, weight_fn=lambda _, __, weight: float(weight)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_depth.py:237*

### test_linear

**Category**: workflow  
**Description**: Workflow: Longest depth for a simple dag.

a
|
b
|        c d
|        e |
| |
f g  
**Expected**: self.assertEqual([node_a, node_b, node_c, node_e, node_f], rustworkx.dag_longest_path(dag))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Longest depth for a simple dag.\n\n        a\n        |\n        b\n        |        c d\n        |        e |\n        | |\n        f g\n        '
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {})
node_c = dag.add_child(node_b, 'c', {})
dag.add_child(node_b, 'd', {})
node_e = dag.add_child(node_c, 'e', {})
node_f = dag.add_child(node_e, 'f', {})
dag.add_child(node_c, 'g', {})
self.assertEqual(4, rustworkx.dag_longest_path_length(dag))
self.assertEqual([node_a, node_b, node_c, node_e, node_f], rustworkx.dag_longest_path(dag))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_depth.py:19*

### test_less_linear

**Category**: workflow  
**Description**: Workflow: test less linear  
**Expected**: self.assertEqual([node_a, node_b, node_c, node_d, node_e], rustworkx.dag_longest_path(dag))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {})
node_c = dag.add_child(node_b, 'c', {})
node_d = dag.add_child(node_c, 'd', {})
node_e = dag.add_child(node_d, 'e', {})
dag.add_edge(node_a, node_c, {})
dag.add_edge(node_a, node_e, {})
dag.add_edge(node_c, node_e, {})
self.assertEqual(4, rustworkx.dag_longest_path_length(dag))
self.assertEqual([node_a, node_b, node_c, node_d, node_e], rustworkx.dag_longest_path(dag))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_depth.py:46*

### test_linear_with_weight

**Category**: workflow  
**Description**: Workflow: Longest depth for a simple dag.

a
|
b
|        c d
|        e |
| |
f g  
**Expected**: self.assertEqual(23, rustworkx.dag_longest_path_length(dag, lambda _, __, weight: weight))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Longest depth for a simple dag.\n\n        a\n        |\n        b\n        |        c d\n        |        e |\n        | |\n        f g\n        '
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 4)
node_c = dag.add_child(node_b, 'c', 4)
dag.add_child(node_b, 'd', 5)
node_e = dag.add_child(node_c, 'e', 2)
dag.add_child(node_e, 'f', 2)
node_g = dag.add_child(node_c, 'g', 15)
self.assertEqual([node_a, node_b, node_c, node_g], rustworkx.dag_longest_path(dag, lambda _, __, weight: weight))
self.assertEqual(23, rustworkx.dag_longest_path_length(dag, lambda _, __, weight: weight))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_depth.py:90*

### test_less_linear_with_weight

**Category**: workflow  
**Description**: Workflow: test less linear with weight  
**Expected**: self.assertEqual([node_a, node_c, node_e], rustworkx.dag_longest_path(dag, weight_fn=lambda _, __, weight: weight))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 1)
node_c = dag.add_child(node_b, 'c', 1)
node_d = dag.add_child(node_c, 'd', 1)
node_e = dag.add_child(node_d, 'e', 1)
dag.add_edge(node_a, node_c, 3)
dag.add_edge(node_a, node_e, 3)
dag.add_edge(node_c, node_e, 3)
self.assertEqual(6, rustworkx.dag_longest_path_length(dag, weight_fn=lambda _, __, weight: weight))
self.assertEqual([node_a, node_c, node_e], rustworkx.dag_longest_path(dag, weight_fn=lambda _, __, weight: weight))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_depth.py:141*

### test_filter_nodes

**Category**: workflow  
**Description**: Workflow: test filter nodes  
**Expected**: self.assertEqual(list(human_indices), [])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
def my_filter_function1(node):
    return node == 'cat'

def my_filter_function2(node):
    return node == 'lizard'

def my_filter_function3(node):
    return node == 'human'
graph = rx.PyGraph()
graph.add_node('cat')
graph.add_node('cat')
graph.add_node('dog')
graph.add_node('lizard')
graph.add_node('cat')
cat_indices = graph.filter_nodes(my_filter_function1)
lizard_indices = graph.filter_nodes(my_filter_function2)
human_indices = graph.filter_nodes(my_filter_function3)
self.assertEqual(list(cat_indices), [0, 1, 4])
self.assertEqual(list(lizard_indices), [3])
self.assertEqual(list(human_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_filter.py:19*

### test_filter_edges

**Category**: workflow  
**Description**: Workflow: test filter edges  
**Expected**: self.assertEqual(list(frenemies_indices), [])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
def my_filter_function1(edge):
    return edge == 'friends'

def my_filter_function2(edge):
    return edge == 'enemies'

def my_filter_function3(node):
    return node == 'frenemies'
graph = rx.PyGraph()
graph.add_node('cat')
graph.add_node('cat')
graph.add_node('dog')
graph.add_node('lizard')
graph.add_node('cat')
graph.add_edge(0, 2, 'friends')
graph.add_edge(0, 1, 'friends')
graph.add_edge(0, 3, 'enemies')
friends_indices = graph.filter_edges(my_filter_function1)
enemies_indices = graph.filter_edges(my_filter_function2)
frenemies_indices = graph.filter_edges(my_filter_function3)
self.assertEqual(list(friends_indices), [0, 1])
self.assertEqual(list(enemies_indices), [2])
self.assertEqual(list(frenemies_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_filter.py:42*

### test_filter_nodes

**Category**: workflow  
**Description**: Workflow: test filter nodes  
**Expected**: self.assertEqual(list(human_indices), [])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
def my_filter_function1(node):
    return node == 'cat'

def my_filter_function2(node):
    return node == 'lizard'

def my_filter_function3(node):
    return node == 'human'
graph = rx.PyGraph()
graph.add_node('cat')
graph.add_node('cat')
graph.add_node('dog')
graph.add_node('lizard')
graph.add_node('cat')
cat_indices = graph.filter_nodes(my_filter_function1)
lizard_indices = graph.filter_nodes(my_filter_function2)
human_indices = graph.filter_nodes(my_filter_function3)
self.assertEqual(list(cat_indices), [0, 1, 4])
self.assertEqual(list(lizard_indices), [3])
self.assertEqual(list(human_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_filter.py:19*

### test_filter_edges

**Category**: workflow  
**Description**: Workflow: test filter edges  
**Expected**: self.assertEqual(list(frenemies_indices), [])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
def my_filter_function1(edge):
    return edge == 'friends'

def my_filter_function2(edge):
    return edge == 'enemies'

def my_filter_function3(node):
    return node == 'frenemies'
graph = rx.PyGraph()
graph.add_node('cat')
graph.add_node('cat')
graph.add_node('dog')
graph.add_node('lizard')
graph.add_node('cat')
graph.add_edge(0, 2, 'friends')
graph.add_edge(0, 1, 'friends')
graph.add_edge(0, 3, 'enemies')
friends_indices = graph.filter_edges(my_filter_function1)
enemies_indices = graph.filter_edges(my_filter_function2)
frenemies_indices = graph.filter_edges(my_filter_function3)
self.assertEqual(list(friends_indices), [0, 1])
self.assertEqual(list(enemies_indices), [2])
self.assertEqual(list(frenemies_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_filter.py:42*

### test_path_graph_node_attrs

**Category**: workflow  
**Description**: Workflow: test path graph node attrs  
**Expected**: self.assertEqual(json.loads(res), expected)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.path_graph(3)
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
res = rustworkx.node_link_json(graph, node_attrs=dict)
expected = {'attrs': None, 'directed': False, 'links': [{'data': None, 'id': 0, 'source': 0, 'target': 1}, {'data': None, 'id': 1, 'source': 1, 'target': 2}], 'multigraph': True, 'nodes': [{'data': {'nodeLabel': 'node=0'}, 'id': 0}, {'data': {'nodeLabel': 'node=1'}, 'id': 1}, {'data': {'nodeLabel': 'node=2'}, 'id': 2}]}
self.assertEqual(json.loads(res), expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_node_link_json.py:44*

### test_file_output

**Category**: workflow  
**Description**: Workflow: test file output  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.path_graph(3)
graph.attrs = 'path_graph'
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
for edge, (source, target, _weight) in graph.edge_index_map().items():
    graph.update_edge_by_index(edge, {'edgeLabel': f'{source}->{target}'})
expected = {'attrs': {'label': 'path_graph'}, 'directed': False, 'links': [{'data': {'edgeLabel': '0->1'}, 'id': 0, 'source': 0, 'target': 1}, {'data': {'edgeLabel': '1->2'}, 'id': 1, 'source': 1, 'target': 2}], 'multigraph': True, 'nodes': [{'data': {'nodeLabel': 'node=0'}, 'id': 0}, {'data': {'nodeLabel': 'node=1'}, 'id': 1}, {'data': {'nodeLabel': 'node=2'}, 'id': 2}]}
with tempfile.NamedTemporaryFile() as fd:
    res = rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
    self.assertIsNone(res)
    json_dict = json.load(fd)
    self.assertEqual(json_dict, expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_node_link_json.py:95*

### test_round_trip_with_file

**Category**: workflow  
**Description**: Workflow: test round trip with file  
**Expected**: self.assertEqual(new.attrs, graph.attrs)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.path_graph(3)
graph.attrs = 'path_graph'
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
for edge, (source, target, _weight) in graph.edge_index_map().items():
    graph.update_edge_by_index(edge, {'edgeLabel': f'{source}->{target}'})
with tempfile.NamedTemporaryFile() as fd:
    rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
    new = rustworkx.from_node_link_json_file(fd.name, graph_attrs=lambda x: x['label'])
self.assertIsInstance(new, type(graph))
self.assertEqual(new.nodes(), graph.nodes())
self.assertEqual(new.weighted_edge_list(), graph.weighted_edge_list())
self.assertEqual(new.attrs, graph.attrs)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_node_link_json.py:154*

### test_round_trip_networkx

**Category**: workflow  
**Description**: Workflow: test round trip networkx  
**Expected**: self.assertEqual(new.edge_list(), list(graph.edges()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = nx.generators.path_graph(5)
try:
    node_link_str = json.dumps(nx.node_link_data(graph, edges='links'))
except TypeError:
    node_link_str = json.dumps(nx.node_link_data(graph))
new = rustworkx.parse_node_link_json(node_link_str)
self.assertIsInstance(new, rustworkx.PyGraph)
self.assertEqual(new.num_nodes(), graph.number_of_nodes())
self.assertEqual(new.edge_list(), list(graph.edges()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_node_link_json.py:175*

### test_round_trip_with_file_no_graph_attr

**Category**: workflow  
**Description**: Workflow: test round trip with file no graph attr  
**Expected**: self.assertEqual(new.attrs, {'label': graph.attrs})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.path_graph(3)
graph.attrs = 'path_graph'
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
for edge, (source, target, _weight) in graph.edge_index_map().items():
    graph.update_edge_by_index(edge, {'edgeLabel': f'{source}->{target}'})
with tempfile.NamedTemporaryFile() as fd:
    rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
    new = rustworkx.from_node_link_json_file(fd.name)
self.assertIsInstance(new, type(graph))
self.assertEqual(new.nodes(), graph.nodes())
self.assertEqual(new.weighted_edge_list(), graph.weighted_edge_list())
self.assertEqual(new.attrs, {'label': graph.attrs})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_node_link_json.py:187*

### test_node_indices_preserved_with_contraction

**Category**: workflow  
**Description**: Workflow: Test that node indices are preserved after contraction (issue #1503)  
**Expected**: self.assertEqual(graph.edge_list(), restored.edge_list())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test that node indices are preserved after contraction (issue #1503)'
graph = rustworkx.PyGraph()
graph.add_node(None)
graph.add_node(None)
graph.add_node(None)
contracted_idx = graph.contract_nodes([0, 1], None)
graph.add_edge(2, contracted_idx, None)
self.assertEqual([2, contracted_idx], graph.node_indices())
json_str = rustworkx.node_link_json(graph)
restored = rustworkx.parse_node_link_json(json_str)
self.assertEqual(graph.node_indices(), restored.node_indices())
self.assertEqual(graph.edge_list(), restored.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_node_link_json.py:228*

### test_path_graph_node_attrs

**Category**: workflow  
**Description**: Workflow: test path graph node attrs  
**Expected**: self.assertEqual(json.loads(res), expected)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.path_graph(3)
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
res = rustworkx.node_link_json(graph, node_attrs=dict)
expected = {'attrs': None, 'directed': False, 'links': [{'data': None, 'id': 0, 'source': 0, 'target': 1}, {'data': None, 'id': 1, 'source': 1, 'target': 2}], 'multigraph': True, 'nodes': [{'data': {'nodeLabel': 'node=0'}, 'id': 0}, {'data': {'nodeLabel': 'node=1'}, 'id': 1}, {'data': {'nodeLabel': 'node=2'}, 'id': 2}]}
self.assertEqual(json.loads(res), expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_node_link_json.py:44*

### test_file_output

**Category**: workflow  
**Description**: Workflow: test file output  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.path_graph(3)
graph.attrs = 'path_graph'
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
for edge, (source, target, _weight) in graph.edge_index_map().items():
    graph.update_edge_by_index(edge, {'edgeLabel': f'{source}->{target}'})
expected = {'attrs': {'label': 'path_graph'}, 'directed': False, 'links': [{'data': {'edgeLabel': '0->1'}, 'id': 0, 'source': 0, 'target': 1}, {'data': {'edgeLabel': '1->2'}, 'id': 1, 'source': 1, 'target': 2}], 'multigraph': True, 'nodes': [{'data': {'nodeLabel': 'node=0'}, 'id': 0}, {'data': {'nodeLabel': 'node=1'}, 'id': 1}, {'data': {'nodeLabel': 'node=2'}, 'id': 2}]}
with tempfile.NamedTemporaryFile() as fd:
    res = rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
    self.assertIsNone(res)
    json_dict = json.load(fd)
    self.assertEqual(json_dict, expected)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_node_link_json.py:95*

### test_round_trip_with_file

**Category**: workflow  
**Description**: Workflow: test round trip with file  
**Expected**: self.assertEqual(new.attrs, graph.attrs)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.generators.path_graph(3)
graph.attrs = 'path_graph'
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
for edge, (source, target, _weight) in graph.edge_index_map().items():
    graph.update_edge_by_index(edge, {'edgeLabel': f'{source}->{target}'})
with tempfile.NamedTemporaryFile() as fd:
    rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
    new = rustworkx.from_node_link_json_file(fd.name, graph_attrs=lambda x: x['label'])
self.assertIsInstance(new, type(graph))
self.assertEqual(new.nodes(), graph.nodes())
self.assertEqual(new.weighted_edge_list(), graph.weighted_edge_list())
self.assertEqual(new.attrs, graph.attrs)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_node_link_json.py:154*

### test_round_trip_networkx

**Category**: workflow  
**Description**: Workflow: test round trip networkx  
**Expected**: self.assertEqual(new.edge_list(), list(graph.edges()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = nx.generators.path_graph(5)
try:
    node_link_str = json.dumps(nx.node_link_data(graph, edges='links'))
except TypeError:
    node_link_str = json.dumps(nx.node_link_data(graph))
new = rustworkx.parse_node_link_json(node_link_str)
self.assertIsInstance(new, rustworkx.PyGraph)
self.assertEqual(new.num_nodes(), graph.number_of_nodes())
self.assertEqual(new.edge_list(), list(graph.edges()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_node_link_json.py:175*

### test_clear

**Category**: workflow  
**Description**: Workflow: test clear  
**Expected**: self.assertEqual(graph.edges(), [])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'a': 2})
graph.clear()
self.assertEqual(graph.num_nodes(), 0)
self.assertEqual(graph.num_edges(), 0)
self.assertEqual(graph.nodes(), [])
self.assertEqual(graph.edges(), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_clear.py:19*

### test_clear_reuse

**Category**: workflow  
**Description**: Workflow: test clear reuse  
**Expected**: self.assertEqual(graph.edges(), [{'a': 1}, {'a': 2}])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'a': 2})
graph.clear()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'a': 2})
self.assertEqual(graph.num_nodes(), 3)
self.assertEqual(graph.num_edges(), 2)
self.assertEqual(graph.nodes(), ['a', 'b', 'c'])
self.assertEqual(graph.edges(), [{'a': 1}, {'a': 2}])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_clear.py:32*

### test_clear_edges

**Category**: workflow  
**Description**: Workflow: test clear edges  
**Expected**: self.assertEqual(graph.nodes(), ['a', 'b', 'c'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'e1', 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'e2', 2})
graph.clear_edges()
self.assertEqual(graph.num_edges(), 0)
self.assertEqual(graph.edges(), [])
self.assertEqual(graph.num_nodes(), 3)
self.assertEqual(graph.nodes(), ['a', 'b', 'c'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_clear.py:50*

### test_clear_edges_reuse

**Category**: workflow  
**Description**: Workflow: test clear edges reuse  
**Expected**: self.assertEqual(graph.edges(), [{'e1', 1}, {'e2', 2}])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'e1', 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'e2', 2})
graph.clear_edges()
graph.add_edge(node_a, node_b, {'e1', 1})
graph.add_edge(node_a, node_c, {'e2', 2})
self.assertEqual(graph.num_nodes(), 3)
self.assertEqual(graph.num_edges(), 2)
self.assertEqual(graph.nodes(), ['a', 'b', 'c'])
self.assertEqual(graph.edges(), [{'e1', 1}, {'e2', 2}])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_clear.py:63*

### test_clear

**Category**: workflow  
**Description**: Workflow: test clear  
**Expected**: self.assertEqual(graph.edges(), [])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'a': 2})
graph.clear()
self.assertEqual(graph.num_nodes(), 0)
self.assertEqual(graph.num_edges(), 0)
self.assertEqual(graph.nodes(), [])
self.assertEqual(graph.edges(), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_clear.py:19*

### test_clear_reuse

**Category**: workflow  
**Description**: Workflow: test clear reuse  
**Expected**: self.assertEqual(graph.edges(), [{'a': 1}, {'a': 2}])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'a': 2})
graph.clear()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'a': 2})
self.assertEqual(graph.num_nodes(), 3)
self.assertEqual(graph.num_edges(), 2)
self.assertEqual(graph.nodes(), ['a', 'b', 'c'])
self.assertEqual(graph.edges(), [{'a': 1}, {'a': 2}])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_clear.py:32*

### test_clear_edges

**Category**: workflow  
**Description**: Workflow: test clear edges  
**Expected**: self.assertEqual(graph.nodes(), ['a', 'b', 'c'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'e1', 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'e2', 2})
graph.clear_edges()
self.assertEqual(graph.num_edges(), 0)
self.assertEqual(graph.edges(), [])
self.assertEqual(graph.num_nodes(), 3)
self.assertEqual(graph.nodes(), ['a', 'b', 'c'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_clear.py:50*

### test_clear_edges_reuse

**Category**: workflow  
**Description**: Workflow: test clear edges reuse  
**Expected**: self.assertEqual(graph.edges(), [{'e1', 1}, {'e2', 2}])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'e1', 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'e2', 2})
graph.clear_edges()
graph.add_edge(node_a, node_b, {'e1', 1})
graph.add_edge(node_a, node_c, {'e2', 2})
self.assertEqual(graph.num_nodes(), 3)
self.assertEqual(graph.num_edges(), 2)
self.assertEqual(graph.nodes(), ['a', 'b', 'c'])
self.assertEqual(graph.edges(), [{'e1', 1}, {'e2', 2}])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_clear.py:63*

### test_copy_returns_graph

**Category**: workflow  
**Description**: Workflow: test copy returns graph  
**Expected**: self.assertIsInstance(graph_b, rustworkx.PyGraph)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyGraph()
node_a = graph_a.add_node('a_1')
node_b = graph_a.add_node('a_2')
graph_a.add_edge(node_a, node_b, 'edge_1')
node_c = graph_a.add_node('a_3')
graph_a.add_edge(node_b, node_c, 'edge_2')
graph_b = graph_a.copy()
self.assertIsInstance(graph_b, rustworkx.PyGraph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_copy.py:19*

### test_copy_with_holes_returns_graph

**Category**: workflow  
**Description**: Workflow: test copy with holes returns graph  
**Expected**: self.assertEqual([node_a, node_c], graph_b.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyGraph()
node_a = graph_a.add_node('a_1')
node_b = graph_a.add_node('a_2')
graph_a.add_edge(node_a, node_b, 'edge_1')
node_c = graph_a.add_node('a_3')
graph_a.add_edge(node_b, node_c, 'edge_2')
graph_a.remove_node(node_b)
graph_b = graph_a.copy()
self.assertIsInstance(graph_b, rustworkx.PyGraph)
self.assertEqual([node_a, node_c], graph_b.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_copy.py:29*

### test_copy_shared_ref

**Category**: workflow  
**Description**: Workflow: test copy shared ref  
**Expected**: self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyGraph()
node_a = graph_a.add_node({'a': 1})
node_b = graph_a.add_node({'b': 2})
graph_a.add_edge(node_a, node_b, {'edge': 1})
graph_b = graph_a.copy()
graph_a[0]['a'] = 42
graph_b.get_edge_data(0, 1)['edge'] = 162
self.assertEqual(graph_b[0]['a'], 42)
self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_copy.py:46*

### test_copy_returns_graph

**Category**: workflow  
**Description**: Workflow: test copy returns graph  
**Expected**: self.assertIsInstance(graph_b, rustworkx.PyGraph)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyGraph()
node_a = graph_a.add_node('a_1')
node_b = graph_a.add_node('a_2')
graph_a.add_edge(node_a, node_b, 'edge_1')
node_c = graph_a.add_node('a_3')
graph_a.add_edge(node_b, node_c, 'edge_2')
graph_b = graph_a.copy()
self.assertIsInstance(graph_b, rustworkx.PyGraph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_copy.py:19*

### test_copy_with_holes_returns_graph

**Category**: workflow  
**Description**: Workflow: test copy with holes returns graph  
**Expected**: self.assertEqual([node_a, node_c], graph_b.node_indexes())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyGraph()
node_a = graph_a.add_node('a_1')
node_b = graph_a.add_node('a_2')
graph_a.add_edge(node_a, node_b, 'edge_1')
node_c = graph_a.add_node('a_3')
graph_a.add_edge(node_b, node_c, 'edge_2')
graph_a.remove_node(node_b)
graph_b = graph_a.copy()
self.assertIsInstance(graph_b, rustworkx.PyGraph)
self.assertEqual([node_a, node_c], graph_b.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_copy.py:29*

### test_copy_shared_ref

**Category**: workflow  
**Description**: Workflow: test copy shared ref  
**Expected**: self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_a = rustworkx.PyGraph()
node_a = graph_a.add_node({'a': 1})
node_b = graph_a.add_node({'b': 2})
graph_a.add_edge(node_a, node_b, {'edge': 1})
graph_b = graph_a.copy()
graph_a[0]['a'] = 42
graph_b.get_edge_data(0, 1)['edge'] = 162
self.assertEqual(graph_b[0]['a'], 42)
self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_copy.py:46*

### test_single_neighbor

**Category**: workflow  
**Description**: Workflow: test single neighbor  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'a': 2})
res = graph.neighbors(node_a)
self.assertCountEqual([node_c, node_b], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_neighbors.py:19*

### test_unique_neighbors_on_graphs

**Category**: workflow  
**Description**: Workflow: test unique neighbors on graphs  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyGraph()
node_a = dag.add_node('a')
node_b = dag.add_node('b')
node_c = dag.add_node('c')
dag.add_edge(node_a, node_b, ['edge a->b'])
dag.add_edge(node_a, node_b, ['edge a->b bis'])
dag.add_edge(node_a, node_c, ['edge a->c'])
res = dag.neighbors(node_a)
self.assertCountEqual([node_c, node_b], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_neighbors.py:29*

### test_single_neighbor

**Category**: workflow  
**Description**: Workflow: test single neighbor  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'a': 2})
res = graph.neighbors(node_a)
self.assertCountEqual([node_c, node_b], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_neighbors.py:19*

### test_unique_neighbors_on_graphs

**Category**: workflow  
**Description**: Workflow: test unique neighbors on graphs  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyGraph()
node_a = dag.add_node('a')
node_b = dag.add_node('b')
node_c = dag.add_node('c')
dag.add_edge(node_a, node_b, ['edge a->b'])
dag.add_edge(node_a, node_b, ['edge a->b bis'])
dag.add_edge(node_a, node_c, ['edge a->c'])
res = dag.neighbors(node_a)
self.assertCountEqual([node_c, node_b], res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_neighbors.py:29*

### test_cycle_path_len_gt_1

**Category**: workflow  
**Description**: Workflow:     ┌─┐              ┌─┐
 ┌4─┤a├─1┐           │m├──1───┐
 │  └─┘  │           └┬┘      │
┌┴┐     ┌┴┐           │      ┌┴┐
│d│     │b│   ───►    │      │b│
└┬┘     └┬┘           │      └┬┘
 │  ┌─┐  2            │  ┌─┐  2
 └3─┤c├──┘            └3─┤c├──┘
    └─┘                  └─┘  
**Expected**: self.assertEqual({UndirectedEdge((node_b, node_c)), UndirectedEdge((node_c, node_m)), UndirectedEdge((node_b, node_m))}, set((UndirectedEdge(e) for e in dag.edge_list())))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_contract_nodes.py:57*

### test_multiple_paths_would_cycle

**Category**: workflow  
**Description**: Workflow:     ┌─┐     ┌─┐                  ┌─┐     ┌─┐
 ┌3─┤c│     │e├─5┐            ┌──┤c│     │e├──┐
 │  └┬┘     └┬┘  │            │  └┬┘     └┬┘  │
┌┴┐  2  ┌─┐  4  ┌┴┐           │   2  ┌─┐  4   │
│d│  └──┤b├──┘  │f│   ───►    │   └──┤b├──┘   │
└─┘     └┬┘     └─┘           3      └┬┘      5
         1                    │       1       │
        ┌┴┐                   │      ┌┴┐      │
        │a│                   └──────┤m├──────┘
        └─┘                          └─┘  
**Expected**: self.assertEqual({UndirectedEdge((node_b, node_c)), UndirectedEdge((node_c, node_m)), UndirectedEdge((node_e, node_m)), UndirectedEdge((node_b, node_e)), UndirectedEdge((node_b, node_m))}, set((UndirectedEdge(e) for e in dag.edge_list())))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_contract_nodes.py:92*

### test_keep_edges_multigraph

**Category**: workflow  
**Description**: Workflow:    ┌─┐            ┌─┐
 ┌─┤a├─┐        ┌─┤a├─┐
 │ └─┘ │        │ └─┘ │
 1     2   ──►  1     2
┌┴┐   ┌┴┐       │ ┌─┐ │
│b│   │c│       └─┤m├─┘
└─┘   └─┘         └─┘  
**Expected**: self.assertEqual({UndirectedEdge((node_a, node_m, 1)), UndirectedEdge((node_a, node_m, 2))}, set((UndirectedEdge(e) for e in dag.weighted_edge_list())))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n           ┌─┐            ┌─┐\n         ┌─┤a├─┐        ┌─┤a├─┐\n         │ └─┘ │        │ └─┘ │\n         1     2   ──►  1     2\n        ┌┴┐   ┌┴┐       │ ┌─┐ │\n        │b│   │c│       └─┤m├─┘\n        └─┘   └─┘         └─┘\n        '
dag = rustworkx.PyGraph()
node_a = dag.add_node('a')
node_b = dag.add_node('b')
node_c = dag.add_node('c')
dag.add_edge(node_a, node_b, 1)
dag.add_edge(node_c, node_a, 2)
node_m = dag.contract_nodes([node_b, node_c], 'm')
self.assertEqual([node_a, node_m], dag.node_indexes())
self.assertEqual({UndirectedEdge((node_a, node_m, 1)), UndirectedEdge((node_a, node_m, 2))}, set((UndirectedEdge(e) for e in dag.weighted_edge_list())))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_contract_nodes.py:140*

### test_cycle_path_len_gt_1

**Category**: workflow  
**Description**: Workflow:     ┌─┐              ┌─┐
 ┌4─┤a├─1┐           │m├──1───┐
 │  └─┘  │           └┬┘      │
┌┴┐     ┌┴┐           │      ┌┴┐
│d│     │b│   ───►    │      │b│
└┬┘     └┬┘           │      └┬┘
 │  ┌─┐  2            │  ┌─┐  2
 └3─┤c├──┘            └3─┤c├──┘
    └─┘                  └─┘  
**Expected**: self.assertEqual({UndirectedEdge((node_b, node_c)), UndirectedEdge((node_c, node_m)), UndirectedEdge((node_b, node_m))}, set((UndirectedEdge(e) for e in dag.edge_list())))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_contract_nodes.py:57*

### test_multiple_paths_would_cycle

**Category**: workflow  
**Description**: Workflow:     ┌─┐     ┌─┐                  ┌─┐     ┌─┐
 ┌3─┤c│     │e├─5┐            ┌──┤c│     │e├──┐
 │  └┬┘     └┬┘  │            │  └┬┘     └┬┘  │
┌┴┐  2  ┌─┐  4  ┌┴┐           │   2  ┌─┐  4   │
│d│  └──┤b├──┘  │f│   ───►    │   └──┤b├──┘   │
└─┘     └┬┘     └─┘           3      └┬┘      5
         1                    │       1       │
        ┌┴┐                   │      ┌┴┐      │
        │a│                   └──────┤m├──────┘
        └─┘                          └─┘  
**Expected**: self.assertEqual({UndirectedEdge((node_b, node_c)), UndirectedEdge((node_c, node_m)), UndirectedEdge((node_e, node_m)), UndirectedEdge((node_b, node_e)), UndirectedEdge((node_b, node_m))}, set((UndirectedEdge(e) for e in dag.edge_list())))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
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

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_contract_nodes.py:92*

### test_keep_edges_multigraph

**Category**: workflow  
**Description**: Workflow:    ┌─┐            ┌─┐
 ┌─┤a├─┐        ┌─┤a├─┐
 │ └─┘ │        │ └─┘ │
 1     2   ──►  1     2
┌┴┐   ┌┴┐       │ ┌─┐ │
│b│   │c│       └─┤m├─┘
└─┘   └─┘         └─┘  
**Expected**: self.assertEqual({UndirectedEdge((node_a, node_m, 1)), UndirectedEdge((node_a, node_m, 2))}, set((UndirectedEdge(e) for e in dag.weighted_edge_list())))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n           ┌─┐            ┌─┐\n         ┌─┤a├─┐        ┌─┤a├─┐\n         │ └─┘ │        │ └─┘ │\n         1     2   ──►  1     2\n        ┌┴┐   ┌┴┐       │ ┌─┐ │\n        │b│   │c│       └─┤m├─┘\n        └─┘   └─┘         └─┘\n        '
dag = rustworkx.PyGraph()
node_a = dag.add_node('a')
node_b = dag.add_node('b')
node_c = dag.add_node('c')
dag.add_edge(node_a, node_b, 1)
dag.add_edge(node_c, node_a, 2)
node_m = dag.contract_nodes([node_b, node_c], 'm')
self.assertEqual([node_a, node_m], dag.node_indexes())
self.assertEqual({UndirectedEdge((node_a, node_m, 1)), UndirectedEdge((node_a, node_m, 2))}, set((UndirectedEdge(e) for e in dag.weighted_edge_list())))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_contract_nodes.py:140*

### test_shared_ref

**Category**: workflow  
**Description**: Workflow: test shared ref  
**Expected**: self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
digraph = rustworkx.PyDiGraph()
node_weight = {'a': 1}
node_a = digraph.add_node(node_weight)
edge_weight = {'a': 1}
digraph.add_child(node_a, 'b', edge_weight)
graph = digraph.to_undirected()
self.assertEqual(digraph[node_a], {'a': 1})
self.assertEqual(graph[node_a], {'a': 1})
node_weight['b'] = 2
self.assertEqual(digraph[node_a], {'a': 1, 'b': 2})
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1})
edge_weight['b'] = 2
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1, 'b': 2})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_to_undirected.py:50*

### test_shared_ref

**Category**: workflow  
**Description**: Workflow: test shared ref  
**Expected**: self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
digraph = rustworkx.PyDiGraph()
node_weight = {'a': 1}
node_a = digraph.add_node(node_weight)
edge_weight = {'a': 1}
digraph.add_child(node_a, 'b', edge_weight)
graph = digraph.to_undirected()
self.assertEqual(digraph[node_a], {'a': 1})
self.assertEqual(graph[node_a], {'a': 1})
node_weight['b'] = 2
self.assertEqual(digraph[node_a], {'a': 1, 'b': 2})
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1})
edge_weight['b'] = 2
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1, 'b': 2})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_to_undirected.py:50*

### test_directed_path_2_tensor_path_2

**Category**: workflow  
**Description**: Workflow: test directed path 2 tensor path 2  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.directed_path_graph(2)
graph_2 = rustworkx.generators.directed_path_graph(2)
graph_product, node_map = rustworkx.digraph_tensor_product(graph_1, graph_2)
expected_node_map = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (1, 1): 3}
self.assertEqual(node_map, expected_node_map)
expected_edges = [(0, 3)]
self.assertEqual(graph_product.num_nodes(), 4)
self.assertEqual(graph_product.num_edges(), 1)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_tensor_product.py:26*

### test_directed_path_2_tensor_path_3

**Category**: workflow  
**Description**: Workflow: test directed path 2 tensor path 3  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.directed_path_graph(2)
graph_2 = rustworkx.generators.directed_path_graph(3)
graph_product, node_map = rustworkx.digraph_tensor_product(graph_1, graph_2)
expected_node_map = {(0, 1): 1, (1, 0): 3, (0, 0): 0, (1, 2): 5, (0, 2): 2, (1, 1): 4}
self.assertEqual(dict(node_map), expected_node_map)
expected_edges = [(0, 4), (1, 5)]
self.assertEqual(graph_product.num_nodes(), 6)
self.assertEqual(graph_product.num_edges(), 2)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_tensor_product.py:39*

### test_multi_graph_1

**Category**: workflow  
**Description**: Workflow: test multi graph 1  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.directed_path_graph(2)
graph_1.add_edge(0, 1, None)
graph_2 = rustworkx.generators.directed_path_graph(2)
graph_product, _ = rustworkx.digraph_tensor_product(graph_1, graph_2)
expected_edges = [(0, 3), (0, 3)]
self.assertEqual(graph_product.num_edges(), 2)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_tensor_product.py:72*

### test_multi_graph_2

**Category**: workflow  
**Description**: Workflow: test multi graph 2  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.directed_path_graph(2)
graph_1.add_edge(0, 0, None)
graph_2 = rustworkx.generators.directed_path_graph(2)
graph_product, _ = rustworkx.digraph_tensor_product(graph_1, graph_2)
expected_edges = [(0, 3), (0, 1)]
self.assertEqual(graph_product.num_edges(), 2)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_tensor_product.py:82*

### test_multi_graph_3

**Category**: workflow  
**Description**: Workflow: test multi graph 3  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.directed_path_graph(2)
graph_2 = rustworkx.generators.directed_path_graph(2)
graph_2.add_edge(0, 1, None)
graph_product, _ = rustworkx.digraph_tensor_product(graph_1, graph_2)
expected_edges = [(0, 3), (0, 3)]
self.assertEqual(graph_product.num_edges(), 2)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_tensor_product.py:92*

### test_multi_graph_4

**Category**: workflow  
**Description**: Workflow: test multi graph 4  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.directed_path_graph(2)
graph_2 = rustworkx.generators.directed_path_graph(2)
graph_2.add_edge(0, 0, None)
graph_product, _ = rustworkx.digraph_tensor_product(graph_1, graph_2)
expected_edges = [(0, 3), (0, 2)]
self.assertEqual(graph_product.num_edges(), 2)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_tensor_product.py:102*

### test_directed_path_2_tensor_path_2

**Category**: workflow  
**Description**: Workflow: test directed path 2 tensor path 2  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.directed_path_graph(2)
graph_2 = rustworkx.generators.directed_path_graph(2)
graph_product, node_map = rustworkx.digraph_tensor_product(graph_1, graph_2)
expected_node_map = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (1, 1): 3}
self.assertEqual(node_map, expected_node_map)
expected_edges = [(0, 3)]
self.assertEqual(graph_product.num_nodes(), 4)
self.assertEqual(graph_product.num_edges(), 1)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_tensor_product.py:26*

### test_directed_path_2_tensor_path_3

**Category**: workflow  
**Description**: Workflow: test directed path 2 tensor path 3  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.directed_path_graph(2)
graph_2 = rustworkx.generators.directed_path_graph(3)
graph_product, node_map = rustworkx.digraph_tensor_product(graph_1, graph_2)
expected_node_map = {(0, 1): 1, (1, 0): 3, (0, 0): 0, (1, 2): 5, (0, 2): 2, (1, 1): 4}
self.assertEqual(dict(node_map), expected_node_map)
expected_edges = [(0, 4), (1, 5)]
self.assertEqual(graph_product.num_nodes(), 6)
self.assertEqual(graph_product.num_edges(), 2)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_tensor_product.py:39*

### test_multi_graph_1

**Category**: workflow  
**Description**: Workflow: test multi graph 1  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.directed_path_graph(2)
graph_1.add_edge(0, 1, None)
graph_2 = rustworkx.generators.directed_path_graph(2)
graph_product, _ = rustworkx.digraph_tensor_product(graph_1, graph_2)
expected_edges = [(0, 3), (0, 3)]
self.assertEqual(graph_product.num_edges(), 2)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_tensor_product.py:72*

### test_multi_graph_2

**Category**: workflow  
**Description**: Workflow: test multi graph 2  
**Expected**: self.assertEqual(graph_product.edge_list(), expected_edges)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph_1 = rustworkx.generators.directed_path_graph(2)
graph_1.add_edge(0, 0, None)
graph_2 = rustworkx.generators.directed_path_graph(2)
graph_product, _ = rustworkx.digraph_tensor_product(graph_1, graph_2)
expected_edges = [(0, 3), (0, 1)]
self.assertEqual(graph_product.num_edges(), 2)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_tensor_product.py:82*

### test_all_shortest_paths_with_no_path

**Category**: workflow  
**Description**: Workflow: test all shortest paths with no path  
**Expected**: self.assertEqual(expected, paths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
paths = rustworkx.graph_all_shortest_paths(g, a, b, lambda x: float(x))
expected = []
self.assertEqual(expected, paths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_shortest_paths.py:55*

### test_all_shortest_paths_with_no_path

**Category**: workflow  
**Description**: Workflow: test all shortest paths with no path  
**Expected**: self.assertEqual(expected, paths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
paths = rustworkx.graph_all_shortest_paths(g, a, b, lambda x: float(x))
expected = []
self.assertEqual(expected, paths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_shortest_paths.py:55*

### test_graph_bfs_tree_edges_restricted

**Category**: workflow  
**Description**: Workflow: test graph bfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

class TreeEdgesRecorderRestricted(rustworkx.visit.BFSVisitor):
    prohibited = [(0, 2), (1, 2)]

    def __init__(self):
        self.edges = []

    def tree_edge(self, edge):
        edge = (edge[0], edge[1])
        if edge in self.prohibited:
            raise rustworkx.visit.PruneSearch
        self.edges.append(edge)
vis = TreeEdgesRecorderRestricted()
rustworkx.graph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_search.py:58*

### test_graph_bfs_goal_search_with_stop_search_exception

**Category**: workflow  
**Description**: Workflow: test graph bfs goal search with stop search exception  
**Expected**: self.assertEqual(vis.reconstruct_path(), [0, 1, 3])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

class GoalSearch(rustworkx.visit.BFSVisitor):
    goal = 3

    def __init__(self):
        self.parents = {}

    def tree_edge(self, edge):
        u, v, _ = edge
        self.parents[v] = u
        if v == self.goal:
            raise rustworkx.visit.StopSearch

    def reconstruct_path(self):
        v = self.goal
        path = [v]
        while v in self.parents:
            v = self.parents[v]
            path.append(v)
        path.reverse()
        return path
vis = GoalSearch()
rustworkx.graph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.reconstruct_path(), [0, 1, 3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_search.py:75*

### test_graph_bfs_tree_edges_restricted

**Category**: workflow  
**Description**: Workflow: test graph bfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
class TreeEdgesRecorderRestricted(rustworkx.visit.BFSVisitor):
    prohibited = [(0, 2), (1, 2)]

    def __init__(self):
        self.edges = []

    def tree_edge(self, edge):
        edge = (edge[0], edge[1])
        if edge in self.prohibited:
            raise rustworkx.visit.PruneSearch
        self.edges.append(edge)
vis = TreeEdgesRecorderRestricted()
rustworkx.graph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_search.py:58*

### test_graph_bfs_goal_search_with_stop_search_exception

**Category**: workflow  
**Description**: Workflow: test graph bfs goal search with stop search exception  
**Expected**: self.assertEqual(vis.reconstruct_path(), [0, 1, 3])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
class GoalSearch(rustworkx.visit.BFSVisitor):
    goal = 3

    def __init__(self):
        self.parents = {}

    def tree_edge(self, edge):
        u, v, _ = edge
        self.parents[v] = u
        if v == self.goal:
            raise rustworkx.visit.StopSearch

    def reconstruct_path(self):
        v = self.goal
        path = [v]
        while v in self.parents:
            v = self.parents[v]
            path.append(v)
        path.reverse()
        return path
vis = GoalSearch()
rustworkx.graph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.reconstruct_path(), [0, 1, 3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_search.py:75*

### test_subgraph_with_nodemap

**Category**: workflow  
**Description**: Workflow: test subgraph with nodemap  
**Expected**: self.assertEqual(dict(node_map), {0: 0, 1: 2, 2: 4})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
graph.add_nodes_from(list(range(6)))
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (1, 4), (2, 5)])
subgraph, node_map = graph.subgraph_with_nodemap([1, 2, 4])
self.assertEqual(set(subgraph.node_indices()), {0, 1, 2})
edge_list = list(subgraph.edge_list())
self.assertEqual(len(edge_list), 2)
self.assertIn((0, 1), edge_list)
self.assertIn((0, 2), edge_list)
node_map_dict = dict(node_map)
self.assertEqual(len(node_map_dict), 3)
self.assertEqual(set(node_map_dict.values()), {1, 2, 4})
graph2 = rustworkx.PyGraph()
graph2.add_nodes_from(['a', 'b', 'c', 'd', 'e'])
graph2.add_edges_from([(0, 1, 1), (2, 3, 2)])
subgraph, node_map = graph2.subgraph_with_nodemap([0, 2, 4])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(['a', 'c', 'e'], subgraph.nodes())
self.assertEqual(dict(node_map), {0: 0, 1: 2, 2: 4})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph.py:152*

### test_subgraph_with_nodemap_edge_cases

**Category**: workflow  
**Description**: Workflow: test subgraph with nodemap edge cases  
**Expected**: self.assertEqual(dict(node_map), {0: 0, 1: 1, 2: 2})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
graph.add_nodes_from(['a', 'b', 'c'])
graph.add_edges_from([(0, 1, 1), (1, 2, 2)])
subgraph, node_map = graph.subgraph_with_nodemap([])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
self.assertEqual(dict(node_map), {})
subgraph, node_map = graph.subgraph_with_nodemap([42, 100])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
self.assertEqual(dict(node_map), {})
subgraph, node_map = graph.subgraph_with_nodemap([1])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(['b'], subgraph.nodes())
self.assertEqual(dict(node_map), {0: 1})
subgraph, node_map = graph.subgraph_with_nodemap([0, 1, 2])
self.assertEqual([(0, 1, 1), (1, 2, 2)], subgraph.weighted_edge_list())
self.assertEqual(['a', 'b', 'c'], subgraph.nodes())
self.assertEqual(dict(node_map), {0: 0, 1: 1, 2: 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph.py:183*

### test_subgraph_with_nodemap

**Category**: workflow  
**Description**: Workflow: test subgraph with nodemap  
**Expected**: self.assertEqual(dict(node_map), {0: 0, 1: 2, 2: 4})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
graph.add_nodes_from(list(range(6)))
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (1, 4), (2, 5)])
subgraph, node_map = graph.subgraph_with_nodemap([1, 2, 4])
self.assertEqual(set(subgraph.node_indices()), {0, 1, 2})
edge_list = list(subgraph.edge_list())
self.assertEqual(len(edge_list), 2)
self.assertIn((0, 1), edge_list)
self.assertIn((0, 2), edge_list)
node_map_dict = dict(node_map)
self.assertEqual(len(node_map_dict), 3)
self.assertEqual(set(node_map_dict.values()), {1, 2, 4})
graph2 = rustworkx.PyGraph()
graph2.add_nodes_from(['a', 'b', 'c', 'd', 'e'])
graph2.add_edges_from([(0, 1, 1), (2, 3, 2)])
subgraph, node_map = graph2.subgraph_with_nodemap([0, 2, 4])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(['a', 'c', 'e'], subgraph.nodes())
self.assertEqual(dict(node_map), {0: 0, 1: 2, 2: 4})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph.py:152*

### test_subgraph_with_nodemap_edge_cases

**Category**: workflow  
**Description**: Workflow: test subgraph with nodemap edge cases  
**Expected**: self.assertEqual(dict(node_map), {0: 0, 1: 1, 2: 2})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyGraph()
graph.add_nodes_from(['a', 'b', 'c'])
graph.add_edges_from([(0, 1, 1), (1, 2, 2)])
subgraph, node_map = graph.subgraph_with_nodemap([])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
self.assertEqual(dict(node_map), {})
subgraph, node_map = graph.subgraph_with_nodemap([42, 100])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
self.assertEqual(dict(node_map), {})
subgraph, node_map = graph.subgraph_with_nodemap([1])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(['b'], subgraph.nodes())
self.assertEqual(dict(node_map), {0: 1})
subgraph, node_map = graph.subgraph_with_nodemap([0, 1, 2])
self.assertEqual([(0, 1, 1), (1, 2, 2)], subgraph.weighted_edge_list())
self.assertEqual(['a', 'b', 'c'], subgraph.nodes())
self.assertEqual(dict(node_map), {0: 0, 1: 1, 2: 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph.py:183*

### test_node_frequency

**Category**: workflow  
**Description**: Workflow: test node frequency  
**Expected**: self.assertAlmostEqual(counts[6] / (path_length + 1), 1 / 14, delta=tol)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rx.PyGraph()
graph.add_nodes_from(range(7))
graph.add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (4, 5), (2, 4), (2, 5), (5, 6)])
path_length = 5000
path = rx.generate_random_path(graph, 0, path_length, 5)
counts = collections.Counter(path)
tol = 0.01
self.assertAlmostEqual(counts[0] / (path_length + 1), 1 / 14, delta=tol)
self.assertAlmostEqual(counts[1] / (path_length + 1), 2 / 14, delta=tol)
self.assertAlmostEqual(counts[2] / (path_length + 1), 4 / 14, delta=tol)
self.assertAlmostEqual(counts[3] / (path_length + 1), 1 / 14, delta=tol)
self.assertAlmostEqual(counts[4] / (path_length + 1), 2 / 14, delta=tol)
self.assertAlmostEqual(counts[5] / (path_length + 1), 3 / 14, delta=tol)
self.assertAlmostEqual(counts[6] / (path_length + 1), 1 / 14, delta=tol)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_random_walk.py:31*

### test_node_frequency

**Category**: workflow  
**Description**: Workflow: test node frequency  
**Expected**: self.assertAlmostEqual(counts[6] / (path_length + 1), 1 / 14, delta=tol)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rx.PyGraph()
graph.add_nodes_from(range(7))
graph.add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (4, 5), (2, 4), (2, 5), (5, 6)])
path_length = 5000
path = rx.generate_random_path(graph, 0, path_length, 5)
counts = collections.Counter(path)
tol = 0.01
self.assertAlmostEqual(counts[0] / (path_length + 1), 1 / 14, delta=tol)
self.assertAlmostEqual(counts[1] / (path_length + 1), 2 / 14, delta=tol)
self.assertAlmostEqual(counts[2] / (path_length + 1), 4 / 14, delta=tol)
self.assertAlmostEqual(counts[3] / (path_length + 1), 1 / 14, delta=tol)
self.assertAlmostEqual(counts[4] / (path_length + 1), 2 / 14, delta=tol)
self.assertAlmostEqual(counts[5] / (path_length + 1), 3 / 14, delta=tol)
self.assertAlmostEqual(counts[6] / (path_length + 1), 1 / 14, delta=tol)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_random_walk.py:31*

### test_k_shortest_path_with_no_path

**Category**: workflow  
**Description**: Workflow: test k shortest path with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
path_lengths = rustworkx.graph_k_shortest_path_lengths(g, start=a, k=1, edge_cost=float, goal=b)
expected = {}
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_k_shortest_path.py:67*

### test_k_shortest_path_with_no_path

**Category**: workflow  
**Description**: Workflow: test k shortest path with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
path_lengths = rustworkx.graph_k_shortest_path_lengths(g, start=a, k=1, edge_cost=float, goal=b)
expected = {}
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_k_shortest_path.py:67*

### test_get_edge_data

**Category**: workflow  
**Description**: Workflow: test get edge data  
**Expected**: self.assertEqual('Edgy', res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'Edgy')
res = dag.get_edge_data(node_a, node_b)
self.assertEqual('Edgy', res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edges.py:19*

### test_get_all_edge_data

**Category**: workflow  
**Description**: Workflow: test get all edge data  
**Expected**: self.assertIn('Edgy', res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'Edgy')
dag.add_edge(node_a, node_b, 'b')
res = dag.get_all_edge_data(node_a, node_b)
self.assertIn('b', res)
self.assertIn('Edgy', res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edges.py:26*

### test_update_edge_parallel_edges

**Category**: workflow  
**Description**: Workflow: test update edge parallel edges  
**Expected**: self.assertEqual([(0, 1, 'not edgy'), (0, 1, 'Edgy')], list(graph.weighted_edge_list()))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'not edgy')
edge_index = graph.add_edge(node_a, node_b, 'not edgy')
graph.update_edge_by_index(edge_index, 'Edgy')
self.assertEqual([(0, 1, 'not edgy'), (0, 1, 'Edgy')], list(graph.weighted_edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edges.py:81*

### test_remove_edges_from

**Category**: workflow  
**Description**: Workflow: test remove edges from  
**Expected**: self.assertEqual([], graph.edges())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
graph.add_edge(node_a, node_b, 'edgy')
graph.add_edge(node_a, node_c, 'super_edgy')
graph.remove_edges_from([(node_a, node_b), (node_a, node_c)])
self.assertEqual([], graph.edges())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edges.py:157*

### test_remove_edges_from_gen

**Category**: workflow  
**Description**: Workflow: test remove edges from gen  
**Expected**: self.assertEqual([], graph.edges())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
graph.add_edge(node_a, node_b, 'edgy')
graph.add_edge(node_a, node_c, 'super_edgy')
graph.remove_edges_from(((node_a, n) for n in (node_b, node_c)))
self.assertEqual([], graph.edges())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edges.py:167*

### test_remove_edges_from_invalid

**Category**: workflow  
**Description**: Workflow: test remove edges from invalid  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
graph = rustworkx.PyDiGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
graph.add_edge(node_a, node_b, 'edgy')
graph.add_edge(node_a, node_c, 'super_edgy')
with self.assertRaises(rustworkx.NoEdgeBetweenNodes):
    graph.remove_edges_from([(node_b, node_c), (node_a, node_c)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edges.py:177*

### test_add_cycle

**Category**: workflow  
**Description**: Workflow: test add cycle  
**Expected**: self.assertRaises(rustworkx.DAGWouldCycle, dag.add_edge, node_b, node_a, {})  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
dag.check_cycle = True
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {})
self.assertRaises(rustworkx.DAGWouldCycle, dag.add_edge, node_b, node_a, {})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edges.py:200*

### test_add_edge_with_cycle_check_enabled

**Category**: workflow  
**Description**: Workflow: test add edge with cycle check enabled  
**Expected**: self.assertTrue(dag.has_edge(node_c, node_b))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG(True)
node_a = dag.add_node('a')
node_c = dag.add_node('c')
node_b = dag.add_child(node_a, 'b', {})
dag.add_edge(node_c, node_b, {})
self.assertTrue(dag.has_edge(node_c, node_b))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edges.py:207*

### test_enable_cycle_checking_after_edge

**Category**: workflow  
**Description**: Workflow: test enable cycle checking after edge  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {})
dag.add_edge(node_b, node_a, {})
with self.assertRaises(rustworkx.DAGHasCycle):
    dag.check_cycle = True
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edges.py:215*

### test_find_predecessor_node_by_edge

**Category**: workflow  
**Description**: Workflow: test find predecessor node by edge  
**Expected**: self.assertEqual('a', res)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'a to b')
node_c = dag.add_child(node_b, 'c', 'b to c')
dag.add_child(node_c, 'd', 'c to d')

def compare_edges(edge):
    return 'a to b' == edge
res = dag.find_predecessor_node_by_edge(node_b, compare_edges)
self.assertEqual('a', res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edges.py:254*

### test_dijkstra_has_path

**Category**: workflow  
**Description**: Workflow: test dijkstra has path  
**Expected**: self.assertTrue(rustworkx.graph_has_path(g, a, c))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
c = g.add_node('C')
edge_list = [(a, b, 7), (c, b, 9), (c, b, 10)]
g.add_edges_from(edge_list)
self.assertTrue(rustworkx.graph_has_path(g, a, c))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra.py:53*

### test_dijkstra_length_with_no_path

**Category**: workflow  
**Description**: Workflow: test dijkstra length with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
path_lengths = rustworkx.graph_dijkstra_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
expected = {}
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra.py:73*

### test_dijkstra_with_no_path

**Category**: workflow  
**Description**: Workflow: test dijkstra with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

g = rustworkx.PyGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.graph_dijkstra_shortest_path_lengths(g, a, lambda x: float(x))
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra.py:94*

### test_dijkstra_path_with_no_path

**Category**: workflow  
**Description**: Workflow: test dijkstra path with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

g = rustworkx.PyGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.graph_dijkstra_shortest_paths(g, a, weight_fn=lambda x: float(x))
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra.py:102*

### test_dijkstra_with_disconnected_nodes

**Category**: workflow  
**Description**: Workflow: test dijkstra with disconnected nodes  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
g.add_edge(a, b, 1.2)
g.add_node('C')
d = g.add_node('D')
g.add_edge(b, d, 2.4)
path = rustworkx.graph_dijkstra_shortest_path_lengths(g, a, lambda x: round(x, 1))
expected = {1: 1.2, 3: 3.5999999999999996}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra.py:110*

### test_dijkstra_has_path

**Category**: workflow  
**Description**: Workflow: test dijkstra has path  
**Expected**: self.assertTrue(rustworkx.graph_has_path(g, a, c))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
c = g.add_node('C')
edge_list = [(a, b, 7), (c, b, 9), (c, b, 10)]
g.add_edges_from(edge_list)
self.assertTrue(rustworkx.graph_has_path(g, a, c))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra.py:53*

### test_dijkstra_length_with_no_path

**Category**: workflow  
**Description**: Workflow: test dijkstra length with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
path_lengths = rustworkx.graph_dijkstra_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
expected = {}
self.assertEqual(expected, path_lengths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra.py:73*

### test_dijkstra_with_no_path

**Category**: workflow  
**Description**: Workflow: test dijkstra with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.graph_dijkstra_shortest_path_lengths(g, a, lambda x: float(x))
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra.py:94*

### test_dijkstra_path_with_no_path

**Category**: workflow  
**Description**: Workflow: test dijkstra path with no path  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.graph_dijkstra_shortest_paths(g, a, weight_fn=lambda x: float(x))
expected = {}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra.py:102*

### test_dijkstra_with_disconnected_nodes

**Category**: workflow  
**Description**: Workflow: test dijkstra with disconnected nodes  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
g.add_edge(a, b, 1.2)
g.add_node('C')
d = g.add_node('D')
g.add_edge(b, d, 2.4)
path = rustworkx.graph_dijkstra_shortest_path_lengths(g, a, lambda x: round(x, 1))
expected = {1: 1.2, 3: 3.5999999999999996}
self.assertEqual(expected, path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra.py:110*

### test_deepcopy_with_holes_returns_graph

**Category**: method_call  
**Description**: test deepcopy with holes returns graph  
**Expected**: self.assertEqual([node_a, node_c], dag_b.node_indexes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(dag_b, rustworkx.PyGraph)
self.assertEqual([node_a, node_c], dag_b.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_deepcopy.py:39*

### test_deepcopy_with_holes_returns_graph

**Category**: method_call  
**Description**: test deepcopy with holes returns graph  
**Expected**: self.assertEqual([node_a, node_c], dag_b.node_indexes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(dag_b, rustworkx.PyGraph)
self.assertEqual([node_a, node_c], dag_b.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_deepcopy.py:39*

### test_normalized

**Category**: method_call  
**Description**: test normalized  
**Expected**: self.assertEqual({0: 1, 1: 1}, a)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual({0: 1, 1: 1}, h)
self.assertEqual({0: 1, 1: 1}, a)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_hits.py:132*

### test_normalized

**Category**: method_call  
**Description**: test normalized  
**Expected**: self.assertEqual({0: 1, 1: 1}, a)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual({0: 1, 1: 1}, h)
self.assertEqual({0: 1, 1: 1}, a)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_hits.py:132*

### test_petersen_graph_count

**Category**: method_call  
**Description**: test petersen graph count  
**Expected**: self.assertEqual(len(graph.edges()), 3 * n)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 2 * n)
self.assertEqual(len(graph.edges()), 3 * n)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_petersen.py:23*

### test_petersen_graph_count

**Category**: method_call  
**Description**: test petersen graph count  
**Expected**: self.assertEqual(len(graph.edges()), 3 * n)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 2 * n)
self.assertEqual(len(graph.edges()), 3 * n)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_petersen.py:23*

### test_digraph_dfs_tree_edges

**Category**: method_call  
**Description**: test digraph dfs tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (2, 1)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.digraph_dfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (2, 1)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_search.py:43*

### test_digraph_dfs_tree_edges_no_starting_point

**Category**: method_call  
**Description**: test digraph dfs tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (2, 1), (4, 7)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.digraph_dfs_search(self.graph, None, vis)
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (2, 1), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_search.py:55*

### test_digraph_dfs_tree_edges_restricted

**Category**: method_call  
**Description**: test digraph dfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (2, 1), (1, 3)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.digraph_dfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (2, 1), (1, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_search.py:72*

### test_digraph_dfs_tree_edges

**Category**: method_call  
**Description**: test digraph dfs tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (2, 1)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
rustworkx.digraph_dfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (2, 1)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_search.py:43*

### test_digraph_dfs_tree_edges_no_starting_point

**Category**: method_call  
**Description**: test digraph dfs tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (2, 1), (4, 7)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
rustworkx.digraph_dfs_search(self.graph, None, vis)
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (2, 1), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_search.py:55*

### test_digraph_dfs_tree_edges_restricted

**Category**: method_call  
**Description**: test digraph dfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (2, 1), (1, 3)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
rustworkx.digraph_dfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (2, 1), (1, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_search.py:72*

### test_node_labels_drawn

**Category**: method_call  
**Description**: test node labels drawn  
**Expected**: self.assertIn('y', texts)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
plt.close('all')
self.fig, self.ax = plt.subplots()

self.assertIn('x', texts)
self.assertIn('y', texts)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_mpl.py:244*

### test_edge_count

**Category**: method_call  
**Description**: test edge count  
**Expected**: self.assertGreater(len(self.ax.collections) + len(self.ax.patches), 1)  
**Confidence**: 0.85  
**Tags**: mock, unittest  

```python
# Setup
plt.close('all')
self.fig, self.ax = plt.subplots()

mpl_draw(graph, ax=self.ax)
self.assertGreater(len(self.ax.collections) + len(self.ax.patches), 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_mpl.py:260*

### test_directed_graph_produces_arrows

**Category**: method_call  
**Description**: test directed graph produces arrows  
**Expected**: self.assertGreater(len(self.ax.patches), 0)  
**Confidence**: 0.85  
**Tags**: mock, unittest  

```python
# Setup
plt.close('all')
self.fig, self.ax = plt.subplots()

mpl_draw(graph, ax=self.ax)
self.assertGreater(len(self.ax.patches), 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_mpl.py:268*

### test_node_labels_drawn

**Category**: method_call  
**Description**: test node labels drawn  
**Expected**: self.assertIn('y', texts)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('x', texts)
self.assertIn('y', texts)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_mpl.py:244*

### test_null_graph

**Category**: method_call  
**Description**: test null graph  
**Expected**: self.assertEqual(rustworkx.bridges(graph), set())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 2), (0, 3), (1, 4), (4, 9), (5, 7), (0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 8), (5, 6), (6, 7), (8, 9)])
self.barbell_graph = rustworkx.PyGraph()
self.barbell_graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])

self.assertEqual(rustworkx.articulation_points(graph), set())
self.assertEqual(rustworkx.bridges(graph), set())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_biconnected.py:62*

### test_null_graph

**Category**: method_call  
**Description**: test null graph  
**Expected**: self.assertEqual(rustworkx.biconnected_components(graph), {})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 2), (0, 3), (1, 4), (4, 9), (5, 7), (0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 8), (5, 6), (6, 7), (8, 9)])
self.barbell_graph = rustworkx.PyGraph()
self.barbell_graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])

self.assertEqual(rustworkx.bridges(graph), set())
self.assertEqual(rustworkx.biconnected_components(graph), {})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_biconnected.py:63*

### test_trivial_graph

**Category**: method_call  
**Description**: test trivial graph  
**Expected**: self.assertEqual(rustworkx.articulation_points(graph), set())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 2), (0, 3), (1, 4), (4, 9), (5, 7), (0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 8), (5, 6), (6, 7), (8, 9)])
self.barbell_graph = rustworkx.PyGraph()
self.barbell_graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])

graph.add_edge(a, b, None)
self.assertEqual(rustworkx.articulation_points(graph), set())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_biconnected.py:70*

### test_trivial_graph

**Category**: method_call  
**Description**: test trivial graph  
**Expected**: self.assertEqual(rustworkx.bridges(graph), {(0, 1)})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 2), (0, 3), (1, 4), (4, 9), (5, 7), (0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 8), (5, 6), (6, 7), (8, 9)])
self.barbell_graph = rustworkx.PyGraph()
self.barbell_graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])

self.assertEqual(rustworkx.articulation_points(graph), set())
self.assertEqual(rustworkx.bridges(graph), {(0, 1)})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_biconnected.py:71*

### test_another_trivial_graph

**Category**: method_call  
**Description**: test another trivial graph  
**Expected**: self.assertEqual(rustworkx.articulation_points(graph), {1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 2), (0, 3), (1, 4), (4, 9), (5, 7), (0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 8), (5, 6), (6, 7), (8, 9)])
self.barbell_graph = rustworkx.PyGraph()
self.barbell_graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])

graph.add_edge(b, c, None)
self.assertEqual(rustworkx.articulation_points(graph), {1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_biconnected.py:80*

### test_another_trivial_graph

**Category**: method_call  
**Description**: test another trivial graph  
**Expected**: self.assertEqual(sorted_edges(rustworkx.bridges(graph)), {(0, 1), (1, 2)})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 2), (0, 3), (1, 4), (4, 9), (5, 7), (0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 8), (5, 6), (6, 7), (8, 9)])
self.barbell_graph = rustworkx.PyGraph()
self.barbell_graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])

self.assertEqual(rustworkx.articulation_points(graph), {1})
self.assertEqual(sorted_edges(rustworkx.bridges(graph)), {(0, 1), (1, 2)})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_biconnected.py:81*

### test_graph

**Category**: method_call  
**Description**: test graph  
**Expected**: self.assertEqual(rustworkx.articulation_points(self.graph), {4, 5})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 2), (0, 3), (1, 4), (4, 9), (5, 7), (0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 8), (5, 6), (6, 7), (8, 9)])
self.barbell_graph = rustworkx.PyGraph()
self.barbell_graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])

self.assertEqual(rustworkx.biconnected_components(self.graph), components)
self.assertEqual(rustworkx.articulation_points(self.graph), {4, 5})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_biconnected.py:101*

### test_graph

**Category**: method_call  
**Description**: test graph  
**Expected**: self.assertEqual(sorted_edges(rustworkx.bridges(self.graph)), {(4, 5)})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 2), (0, 3), (1, 4), (4, 9), (5, 7), (0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 8), (5, 6), (6, 7), (8, 9)])
self.barbell_graph = rustworkx.PyGraph()
self.barbell_graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])

self.assertEqual(rustworkx.articulation_points(self.graph), {4, 5})
self.assertEqual(sorted_edges(rustworkx.bridges(self.graph)), {(4, 5)})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_biconnected.py:102*

### test_simple_example_graph

**Category**: method_call  
**Description**: test simple example graph  
**Expected**: self.assertTrue(graph.has_edge(0, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.node_indexes(), [0, 1, 2])
self.assertTrue(graph.has_edge(0, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edgelist.py:37*

### test_simple_example_graph

**Category**: method_call  
**Description**: test simple example graph  
**Expected**: self.assertTrue(graph.has_edge(1, 2))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.has_edge(0, 1))
self.assertTrue(graph.has_edge(1, 2))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edgelist.py:38*

### test_simple_example_graph

**Category**: method_call  
**Description**: test simple example graph  
**Expected**: self.assertTrue(graph.has_edge(1, 0))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.has_edge(1, 2))
self.assertTrue(graph.has_edge(1, 0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edgelist.py:39*

### test_simple_example_graph

**Category**: method_call  
**Description**: test simple example graph  
**Expected**: self.assertTrue(graph.has_edge(2, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.has_edge(1, 0))
self.assertTrue(graph.has_edge(2, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edgelist.py:40*

### test_simple_example_graph

**Category**: method_call  
**Description**: test simple example graph  
**Expected**: self.assertFalse(graph.has_edge(0, 2))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.has_edge(2, 1))
self.assertFalse(graph.has_edge(0, 2))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edgelist.py:41*

### test_blank_line_graph

**Category**: method_call  
**Description**: test blank line graph  
**Expected**: self.assertTrue(graph.has_edge(0, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.node_indexes(), [0, 1, 2])
self.assertTrue(graph.has_edge(0, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edgelist.py:51*

### test_blank_line_graph

**Category**: method_call  
**Description**: test blank line graph  
**Expected**: self.assertTrue(graph.has_edge(1, 2))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.has_edge(0, 1))
self.assertTrue(graph.has_edge(1, 2))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edgelist.py:52*

### test_blank_line_graph

**Category**: method_call  
**Description**: test blank line graph  
**Expected**: self.assertTrue(graph.has_edge(1, 0))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.has_edge(1, 2))
self.assertTrue(graph.has_edge(1, 0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_edgelist.py:53*

### test_all_simple_path_no_path

**Category**: method_call  
**Description**: test all simple path no path  
**Expected**: self.assertEqual([], rustworkx.graph_all_simple_paths(dag, 0, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 5), (5, 2), (5, 3)]

dag.add_node(1)
self.assertEqual([], rustworkx.graph_all_simple_paths(dag, 0, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_simple_paths.py:219*

### test_digraph_graph_all_simple_paths

**Category**: method_call  
**Description**: test digraph graph all simple paths  
**Expected**: self.assertRaises(TypeError, rustworkx.graph_all_simple_paths, (dag, 0, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 5), (5, 2), (5, 3)]

dag.add_node(1)
self.assertRaises(TypeError, rustworkx.graph_all_simple_paths, (dag, 0, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_simple_paths.py:232*

### test_all_simple_path_no_path

**Category**: method_call  
**Description**: test all simple path no path  
**Expected**: self.assertEqual({0: {}, 1: {}}, rustworkx.all_pairs_all_simple_paths(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.cycle_graph(4)

graph.add_node(1)
self.assertEqual({0: {}, 1: {}}, rustworkx.all_pairs_all_simple_paths(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_simple_paths.py:344*

### test_all_simple_path_no_path

**Category**: method_call  
**Description**: test all simple path no path  
**Expected**: self.assertEqual([0], rustworkx.longest_simple_path(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.cycle_graph(4)

graph.add_node(1)
self.assertEqual([0], rustworkx.longest_simple_path(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_simple_paths.py:373*

### test_all_simple_path_no_path

**Category**: method_call  
**Description**: test all simple path no path  
**Expected**: self.assertEqual([], rustworkx.graph_all_simple_paths(dag, 0, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
dag.add_node(1)
self.assertEqual([], rustworkx.graph_all_simple_paths(dag, 0, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_simple_paths.py:219*

### test_digraph_graph_all_simple_paths

**Category**: method_call  
**Description**: test digraph graph all simple paths  
**Expected**: self.assertRaises(TypeError, rustworkx.graph_all_simple_paths, (dag, 0, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
dag.add_node(1)
self.assertRaises(TypeError, rustworkx.graph_all_simple_paths, (dag, 0, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_simple_paths.py:232*

### test_all_simple_path_no_path

**Category**: method_call  
**Description**: test all simple path no path  
**Expected**: self.assertEqual({0: {}, 1: {}}, rustworkx.all_pairs_all_simple_paths(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_node(1)
self.assertEqual({0: {}, 1: {}}, rustworkx.all_pairs_all_simple_paths(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_simple_paths.py:344*

### test_all_simple_path_no_path

**Category**: method_call  
**Description**: test all simple path no path  
**Expected**: self.assertEqual([0], rustworkx.longest_simple_path(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_node(1)
self.assertEqual([0], rustworkx.longest_simple_path(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_simple_paths.py:373*

### test_single_self_edge

**Category**: method_call  
**Description**: test single self edge  
**Expected**: self.assertEqual(rustworkx.max_weight_matching(graph), set())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.extend_from_weighted_edge_list([(0, 0, 100)])
self.assertEqual(rustworkx.max_weight_matching(graph), set())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_max_weight_matching.py:99*

### test_single_self_edge

**Category**: method_call  
**Description**: test single self edge  
**Expected**: self.assertEqual(rustworkx.max_weight_matching(graph), set())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.extend_from_weighted_edge_list([(0, 0, 100)])
self.assertEqual(rustworkx.max_weight_matching(graph), set())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_max_weight_matching.py:99*

### test_two_colors_with_isolates

**Category**: method_call  
**Description**: test two colors with isolates  
**Expected**: self.assertEqual(rustworkx.two_color(graph), {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1, 7: 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertEqual(rustworkx.two_color(graph), {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1, 7: 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bipartite.py:33*

### test_is_bipartite_with_isolates

**Category**: method_call  
**Description**: test is bipartite with isolates  
**Expected**: self.assertTrue(rustworkx.is_bipartite(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertTrue(rustworkx.is_bipartite(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bipartite.py:40*

### test_two_colors_not_bipartite_with_isolates

**Category**: method_call  
**Description**: test two colors not bipartite with isolates  
**Expected**: self.assertIsNone(rustworkx.two_color(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertIsNone(rustworkx.two_color(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bipartite.py:45*

### test_not_bipartite_with_isolates

**Category**: method_call  
**Description**: test not bipartite with isolates  
**Expected**: self.assertFalse(rustworkx.is_bipartite(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertFalse(rustworkx.is_bipartite(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bipartite.py:50*

### test_two_colors_with_isolates

**Category**: method_call  
**Description**: test two colors with isolates  
**Expected**: self.assertEqual(rustworkx.two_color(graph), {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1, 7: 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertEqual(rustworkx.two_color(graph), {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1, 7: 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bipartite.py:33*

### test_is_bipartite_with_isolates

**Category**: method_call  
**Description**: test is bipartite with isolates  
**Expected**: self.assertTrue(rustworkx.is_bipartite(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertTrue(rustworkx.is_bipartite(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bipartite.py:40*

### test_two_colors_not_bipartite_with_isolates

**Category**: method_call  
**Description**: test two colors not bipartite with isolates  
**Expected**: self.assertIsNone(rustworkx.two_color(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertIsNone(rustworkx.two_color(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bipartite.py:45*

### test_not_bipartite_with_isolates

**Category**: method_call  
**Description**: test not bipartite with isolates  
**Expected**: self.assertFalse(rustworkx.is_bipartite(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertFalse(rustworkx.is_bipartite(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bipartite.py:50*

### test_random_layout_no_seed

**Category**: method_call  
**Description**: test random layout no seed  
**Expected**: self.assertEqual(len(res), 10)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(10)

self.assertIsInstance(res, rustworkx.Pos2DMapping)
self.assertEqual(len(res), 10)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_layout.py:71*

### test_random_layout_no_seed

**Category**: method_call  
**Description**: test random layout no seed  
**Expected**: self.assertEqual(len(res[0]), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(10)

self.assertEqual(len(res), 10)
self.assertEqual(len(res[0]), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_layout.py:72*

### test_random_layout_no_seed

**Category**: method_call  
**Description**: test random layout no seed  
**Expected**: self.assertIsInstance(res[0][0], float)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(10)

self.assertEqual(len(res[0]), 2)
self.assertIsInstance(res[0][0], float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_layout.py:73*

### test_random_layout_no_seed

**Category**: method_call  
**Description**: test random layout no seed  
**Expected**: self.assertEqual(len(res), 10)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(res, rustworkx.Pos2DMapping)
self.assertEqual(len(res), 10)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_layout.py:71*

### test_random_layout_no_seed

**Category**: method_call  
**Description**: test random layout no seed  
**Expected**: self.assertEqual(len(res[0]), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(res), 10)
self.assertEqual(len(res[0]), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_layout.py:72*

### test_random_layout_no_seed

**Category**: method_call  
**Description**: test random layout no seed  
**Expected**: self.assertIsInstance(res[0][0], float)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(res[0]), 2)
self.assertIsInstance(res[0][0], float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_layout.py:73*

### test_noweight_graph

**Category**: method_call  
**Description**: test noweight graph  
**Expected**: self.assertEqual([None, None, None], gprime.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([1, 2, 3], gprime.node_indices())
self.assertEqual([None, None, None], gprime.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pickle.py:28*

### test_noweight_graph

**Category**: method_call  
**Description**: test noweight graph  
**Expected**: self.assertEqual({1: (1, 2, None), 3: (3, 1, None)}, dict(gprime.edge_index_map()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([None, None, None], gprime.nodes())
self.assertEqual({1: (1, 2, None), 3: (3, 1, None)}, dict(gprime.edge_index_map()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pickle.py:29*

### test_weight_graph

**Category**: method_call  
**Description**: test weight graph  
**Expected**: self.assertEqual(['B', 'C', 'D'], gprime.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([1, 2, 3], gprime.node_indices())
self.assertEqual(['B', 'C', 'D'], gprime.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pickle.py:39*

### test_weight_graph

**Category**: method_call  
**Description**: test weight graph  
**Expected**: self.assertEqual({1: (1, 2, 'B -> C'), 3: (3, 1, 'D -> B')}, dict(gprime.edge_index_map()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(['B', 'C', 'D'], gprime.nodes())
self.assertEqual({1: (1, 2, 'B -> C'), 3: (3, 1, 'D -> B')}, dict(gprime.edge_index_map()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pickle.py:40*

### test_contracted_nodes_pickle

**Category**: method_call  
**Description**: Test pickle/unpickle of directed graphs with contracted nodes (issue #1503)  
**Expected**: self.assertEqual([2, contracted_idx], g.node_indices())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
g.add_edge(2, contracted_idx, 'C -> AB')
self.assertEqual([2, contracted_idx], g.node_indices())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pickle.py:52*

### test_contracted_nodes_pickle

**Category**: method_call  
**Description**: Test pickle/unpickle of directed graphs with contracted nodes (issue #1503)  
**Expected**: self.assertEqual([(2, contracted_idx)], g.edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([2, contracted_idx], g.node_indices())
self.assertEqual([(2, contracted_idx)], g.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pickle.py:55*

### test_contracted_nodes_pickle

**Category**: method_call  
**Description**: Test pickle/unpickle of directed graphs with contracted nodes (issue #1503)  
**Expected**: self.assertEqual(g.edge_list(), gprime.edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(g.node_indices(), gprime.node_indices())
self.assertEqual(g.edge_list(), gprime.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pickle.py:62*

### test_contracted_nodes_pickle

**Category**: method_call  
**Description**: Test pickle/unpickle of directed graphs with contracted nodes (issue #1503)  
**Expected**: self.assertEqual(g.nodes(), gprime.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(g.edge_list(), gprime.edge_list())
self.assertEqual(g.nodes(), gprime.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pickle.py:63*

### test_noweight_graph

**Category**: method_call  
**Description**: test noweight graph  
**Expected**: self.assertEqual([None, None, None], gprime.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([1, 2, 3], gprime.node_indices())
self.assertEqual([None, None, None], gprime.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pickle.py:28*

### test_noweight_graph

**Category**: method_call  
**Description**: test noweight graph  
**Expected**: self.assertEqual({1: (1, 2, None), 3: (3, 1, None)}, dict(gprime.edge_index_map()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([None, None, None], gprime.nodes())
self.assertEqual({1: (1, 2, None), 3: (3, 1, None)}, dict(gprime.edge_index_map()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_pickle.py:29*

### test_simple_graph

**Category**: method_call  
**Description**: test simple graph  
**Expected**: self.assertEqual(len(res[0]), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res), 3)
self.assertEqual(len(res[0]), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_spring_layout.py:34*

### test_simple_graph

**Category**: method_call  
**Description**: test simple graph  
**Expected**: self.assertIsInstance(res[0][0], float)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res[0]), 2)
self.assertIsInstance(res[0][0], float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_spring_layout.py:35*

### test_simple_graph_with_edge_weights

**Category**: method_call  
**Description**: test simple graph with edge weights  
**Expected**: self.assertEqual(len(res[0]), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res), 3)
self.assertEqual(len(res[0]), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_spring_layout.py:40*

### test_simple_graph_with_edge_weights

**Category**: method_call  
**Description**: test simple graph with edge weights  
**Expected**: self.assertIsInstance(res[0][0], float)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res[0]), 2)
self.assertIsInstance(res[0][0], float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_spring_layout.py:41*

### test_simple_graph_center

**Category**: method_call  
**Description**: test simple graph center  
**Expected**: self.assertEqual(len(res[0]), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res), 3)
self.assertEqual(len(res[0]), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_spring_layout.py:46*

### test_simple_graph_center

**Category**: method_call  
**Description**: test simple graph center  
**Expected**: self.assertIsInstance(res[0][0], float)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res[0]), 2)
self.assertIsInstance(res[0][0], float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_spring_layout.py:47*

### test_simple_graph_linear_cooling

**Category**: method_call  
**Description**: test simple graph linear cooling  
**Expected**: self.assertEqual(len(res[0]), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res), 3)
self.assertEqual(len(res[0]), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_spring_layout.py:61*

### test_simple_graph_linear_cooling

**Category**: method_call  
**Description**: test simple graph linear cooling  
**Expected**: self.assertIsInstance(res[0][0], float)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res[0]), 2)
self.assertIsInstance(res[0][0], float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_spring_layout.py:62*

### test_graph_with_removed_nodes

**Category**: method_call  
**Description**: test graph with removed nodes  
**Expected**: self.assertTrue(nodes[0] in res)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res), 2)
self.assertTrue(nodes[0] in res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_spring_layout.py:70*

### test_graph_with_removed_nodes

**Category**: method_call  
**Description**: test graph with removed nodes  
**Expected**: self.assertTrue(nodes[2] in res)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertTrue(nodes[0] in res)
self.assertTrue(nodes[2] in res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_spring_layout.py:71*

### test_clique

**Category**: method_call  
**Description**: test clique  
**Expected**: self.assertEqual(0, len(complement_graph.edges()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.nodes(), complement_graph.nodes())
self.assertEqual(0, len(complement_graph.edges()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_complement.py:25*

### test_null_graph

**Category**: method_call  
**Description**: test null graph  
**Expected**: self.assertEqual(0, len(complement_graph.edges()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(0, len(complement_graph.nodes()))
self.assertEqual(0, len(complement_graph.edges()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_complement.py:47*

### test_clique

**Category**: method_call  
**Description**: test clique  
**Expected**: self.assertEqual(0, len(complement_graph.edges()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.nodes(), complement_graph.nodes())
self.assertEqual(0, len(complement_graph.edges()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_complement.py:25*

### test_null_graph

**Category**: method_call  
**Description**: test null graph  
**Expected**: self.assertEqual(0, len(complement_graph.edges()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(0, len(complement_graph.nodes()))
self.assertEqual(0, len(complement_graph.edges()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_complement.py:47*

### test_empty_replacement

**Category**: method_call  
**Description**: test empty replacement  
**Expected**: self.assertEqual([(0, 1), (3, 4)], self.graph.edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.directed_path_graph(5)

self.assertEqual(res, {})
self.assertEqual([(0, 1), (3, 4)], self.graph.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_substitute_node_with_subgraph.py:25*

### test_single_node

**Category**: method_call  
**Description**: test single node  
**Expected**: self.assertEqual('edge', self.graph.get_edge_data(5, 6))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.directed_path_graph(5)

self.assertEqual([(0, 1), (3, 4), (5, 6), (1, 5), (5, 3)], self.graph.edge_list())
self.assertEqual('edge', self.graph.get_edge_data(5, 6))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_substitute_node_with_subgraph.py:33*

### test_single_node

**Category**: method_call  
**Description**: test single node  
**Expected**: self.assertEqual(res, {0: 5, 1: 6})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.directed_path_graph(5)

self.assertEqual('edge', self.graph.get_edge_data(5, 6))
self.assertEqual(res, {0: 5, 1: 6})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_substitute_node_with_subgraph.py:34*

### test_node_filter

**Category**: method_call  
**Description**: test node filter  
**Expected**: self.assertEqual(res, {0: 5})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.directed_path_graph(5)

self.assertEqual([(0, 1), (3, 4), (1, 5), (5, 3)], self.graph.edge_list())
self.assertEqual(res, {0: 5})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_substitute_node_with_subgraph.py:47*

### test_write_to_string

**Category**: method_call  
**Description**: Write a PyDiGraph to a Matrix Market string.  
**Expected**: self.assertIn('matrix', mm_str)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(mm_str, str)
self.assertIn('matrix', mm_str)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_matrix_market.py:17*

### test_write_to_string

**Category**: method_call  
**Description**: Write a PyDiGraph to a Matrix Market string.  
**Expected**: self.assertIn('3 3 2', mm_str)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('matrix', mm_str)
self.assertIn('3 3 2', mm_str)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_matrix_market.py:18*

### test_write_to_file

**Category**: method_call  
**Description**: Write PyDiGraph data to a Matrix Market file.  
**Expected**: self.assertIn('3 3 2', content)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('matrix', content)
self.assertIn('3 3 2', content)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_matrix_market.py:34*

### test_read_from_file

**Category**: method_call  
**Description**: Read a Matrix Market file into a PyDiGraph.  
**Expected**: self.assertEqual(len(g.nodes()), 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(g, rustworkx.PyDiGraph)
self.assertEqual(len(g.nodes()), 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_matrix_market.py:50*

### test_read_from_file

**Category**: method_call  
**Description**: Read a Matrix Market file into a PyDiGraph.  
**Expected**: self.assertEqual(len(g.edges()), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(g.nodes()), 3)
self.assertEqual(len(g.edges()), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_matrix_market.py:51*

### test_read_from_string

**Category**: method_call  
**Description**: Read Matrix Market data directly from a string.  
**Expected**: self.assertEqual(len(g.nodes()), 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(g, rustworkx.PyDiGraph)
self.assertEqual(len(g.nodes()), 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_matrix_market.py:63*

### test_read_from_string

**Category**: method_call  
**Description**: Read Matrix Market data directly from a string.  
**Expected**: self.assertEqual(len(g.edges()), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(g.nodes()), 3)
self.assertEqual(len(g.edges()), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_matrix_market.py:64*

### test_roundtrip_in_memory

**Category**: method_call  
**Description**: Roundtrip: write → read should reconstruct same directed graph.  
**Expected**: self.assertEqual(len(g2.edges()), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(g2.nodes()), len(g.nodes()))
self.assertEqual(len(g2.edges()), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_matrix_market.py:77*

### test_roundtrip_via_file

**Category**: method_call  
**Description**: Roundtrip through file should preserve directed structure.  
**Expected**: self.assertEqual(len(g2.edges()), 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(g2.nodes()), 2)
self.assertEqual(len(g2.edges()), 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_matrix_market.py:91*

### test_write_to_string

**Category**: method_call  
**Description**: Write a PyDiGraph to a Matrix Market string.  
**Expected**: self.assertIn('matrix', mm_str)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(mm_str, str)
self.assertIn('matrix', mm_str)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_matrix_market.py:17*

### test_floyd_warshall_numpy_digraph_three_edges

**Category**: method_call  
**Description**: test floyd warshall numpy digraph three edges  
**Expected**: self.assertEqual(dist[3, 0], 16)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dist[0, 3], 15)
self.assertEqual(dist[3, 0], 16)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_floyd_warshall.py:203*

### test_weighted_numpy_digraph_two_edges

**Category**: method_call  
**Description**: test weighted numpy digraph two edges  
**Expected**: self.assertEqual(dist[2, 0], 6)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dist[0, 2], 4)
self.assertEqual(dist[2, 0], 6)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_floyd_warshall.py:224*

### test_floyd_warshall_numpy_digraph_cycle

**Category**: method_call  
**Description**: test floyd warshall numpy digraph cycle  
**Expected**: self.assertEqual(dist[0, 4], 4)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dist[0, 3], 3)
self.assertEqual(dist[0, 4], 4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_floyd_warshall.py:234*

### test_numpy_directed_no_edges

**Category**: method_call  
**Description**: test numpy directed no edges  
**Expected**: self.assertTrue(numpy.array_equal(dist, expected))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
numpy.fill_diagonal(expected, 0)
self.assertTrue(numpy.array_equal(dist, expected))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_floyd_warshall.py:258*

### test_floyd_warshall_numpy_digraph_cycle_with_removals

**Category**: method_call  
**Description**: test floyd warshall numpy digraph cycle with removals  
**Expected**: self.assertEqual(dist[0, 4], 4)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dist[0, 3], 3)
self.assertEqual(dist[0, 4], 4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_floyd_warshall.py:269*

### test_floyd_warshall_numpy_digraph_cycle_no_weight_fn

**Category**: method_call  
**Description**: test floyd warshall numpy digraph cycle no weight fn  
**Expected**: self.assertEqual(dist[0, 4], 4)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dist[0, 3], 3)
self.assertEqual(dist[0, 4], 4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_floyd_warshall.py:278*

### test_full_rary_tree_graph_weights

**Category**: method_call  
**Description**: test full rary tree graph weights  
**Expected**: self.assertEqual([x for x in range(4)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 4)
self.assertEqual([x for x in range(4)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_full_rary_tree.py:70*

### test_full_rary_tree_graph_weights

**Category**: method_call  
**Description**: test full rary tree graph weights  
**Expected**: self.assertEqual(len(graph.edges()), 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([x for x in range(4)], graph.nodes())
self.assertEqual(len(graph.edges()), 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_full_rary_tree.py:71*

### test_full_rary_tree_graph_weights

**Category**: method_call  
**Description**: test full rary tree graph weights  
**Expected**: self.assertEqual(list(graph.edge_list()), expected_edges)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph.edges()), 3)
self.assertEqual(list(graph.edge_list()), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_full_rary_tree.py:72*

### test_full_rary_tree_graph_weight_less_nodes

**Category**: method_call  
**Description**: test full rary tree graph weight less nodes  
**Expected**: self.assertEqual(expected_weights, graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
expected_weights.extend([None, None])
self.assertEqual(expected_weights, graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_full_rary_tree.py:79*

### test_directed_path_graph

**Category**: method_call  
**Description**: test directed path graph  
**Expected**: self.assertEqual(len(graph.edges()), 19)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 19)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_path.py:21*

### test_directed_path_graph_weights

**Category**: method_call  
**Description**: test directed path graph weights  
**Expected**: self.assertEqual([x for x in range(20)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual([x for x in range(20)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_path.py:29*

### test_directed_path_graph_weights

**Category**: method_call  
**Description**: test directed path graph weights  
**Expected**: self.assertEqual(len(graph.edges()), 19)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([x for x in range(20)], graph.nodes())
self.assertEqual(len(graph.edges()), 19)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_path.py:30*

### test_directed_path_graph_bidirectional

**Category**: method_call  
**Description**: test directed path graph bidirectional  
**Expected**: self.assertEqual(graph.in_edges(0), [(1, 0, None)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.out_edges(0), [(0, 1, None)])
self.assertEqual(graph.in_edges(0), [(1, 0, None)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_path.py:38*

### test_directed_path_graph_bidirectional

**Category**: method_call  
**Description**: test directed path graph bidirectional  
**Expected**: self.assertEqual(graph.in_edges(19), [(18, 19, None)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.out_edges(19), [(19, 18, None)])
self.assertEqual(graph.in_edges(19), [(18, 19, None)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_path.py:43*

### test_path_graph

**Category**: method_call  
**Description**: test path graph  
**Expected**: self.assertEqual(len(graph.edges()), 19)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 19)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_path.py:52*

### test_path_graph_weights

**Category**: method_call  
**Description**: test path graph weights  
**Expected**: self.assertEqual([x for x in range(20)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual([x for x in range(20)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_path.py:57*

### test_path_graph_weights

**Category**: method_call  
**Description**: test path graph weights  
**Expected**: self.assertEqual(len(graph.edges()), 19)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([x for x in range(20)], graph.nodes())
self.assertEqual(len(graph.edges()), 19)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_path.py:58*

### test_directed_path_graph

**Category**: method_call  
**Description**: test directed path graph  
**Expected**: self.assertEqual(len(graph.edges()), 19)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 19)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_path.py:21*

### test_directed_path_graph_weights

**Category**: method_call  
**Description**: test directed path graph weights  
**Expected**: self.assertEqual([x for x in range(20)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual([x for x in range(20)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_path.py:29*

### test_graph

**Category**: method_call  
**Description**: test graph  
**Expected**: self.assertEqual(out_graph.edge_list(), expected_edges)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(out_graph.node_indices(), expected_nodes)
self.assertEqual(out_graph.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_line_graph.py:34*

### test_graph

**Category**: method_call  
**Description**: test graph  
**Expected**: self.assertEqual(out_edge_map, expected_edge_map)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(out_graph.edge_list(), expected_edges)
self.assertEqual(out_edge_map, expected_edge_map)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_line_graph.py:35*

### test_graph_with_holes

**Category**: method_call  
**Description**: Graph with missing node and edge indices.  
**Expected**: self.assertEqual(out_graph.edge_list(), expected_edges)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(out_graph.node_indices(), expected_nodes)
self.assertEqual(out_graph.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_line_graph.py:56*

### test_graph_with_holes

**Category**: method_call  
**Description**: Graph with missing node and edge indices.  
**Expected**: self.assertEqual(out_edge_map, expected_edge_map)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(out_graph.edge_list(), expected_edges)
self.assertEqual(out_edge_map, expected_edge_map)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_line_graph.py:57*

### test_graph

**Category**: method_call  
**Description**: test graph  
**Expected**: self.assertEqual(out_graph.edge_list(), expected_edges)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(out_graph.node_indices(), expected_nodes)
self.assertEqual(out_graph.edge_list(), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_line_graph.py:34*

### test_graph

**Category**: method_call  
**Description**: test graph  
**Expected**: self.assertEqual(out_edge_map, expected_edge_map)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(out_graph.edge_list(), expected_edges)
self.assertEqual(out_edge_map, expected_edge_map)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_line_graph.py:35*

### test_directed_cycle_graph

**Category**: method_call  
**Description**: test directed cycle graph  
**Expected**: self.assertEqual(len(graph.edges()), 20)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 20)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_cycle.py:21*

### test_directed_cycle_graph_weights

**Category**: method_call  
**Description**: test directed cycle graph weights  
**Expected**: self.assertEqual([x for x in range(20)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual([x for x in range(20)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_cycle.py:29*

### test_directed_cycle_graph_weights

**Category**: method_call  
**Description**: test directed cycle graph weights  
**Expected**: self.assertEqual(len(graph.edges()), 20)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([x for x in range(20)], graph.nodes())
self.assertEqual(len(graph.edges()), 20)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_cycle.py:30*

### test_directed_cycle_graph_bidirectional

**Category**: method_call  
**Description**: test directed cycle graph bidirectional  
**Expected**: self.assertEqual(graph.in_edges(0), [(19, 0, None), (1, 0, None)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.out_edges(0), [(0, 19, None), (0, 1, None)])
self.assertEqual(graph.in_edges(0), [(19, 0, None), (1, 0, None)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_cycle.py:38*

### test_directed_cycle_graph_bidirectional

**Category**: method_call  
**Description**: test directed cycle graph bidirectional  
**Expected**: self.assertEqual(graph.in_edges(19), [(0, 19, None), (18, 19, None)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.out_edges(19), [(19, 0, None), (19, 18, None)])
self.assertEqual(graph.in_edges(19), [(0, 19, None), (18, 19, None)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_cycle.py:43*

### test_cycle_graph

**Category**: method_call  
**Description**: test cycle graph  
**Expected**: self.assertEqual(len(graph.edges()), 20)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 20)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_cycle.py:52*

### test_cycle_graph_weights

**Category**: method_call  
**Description**: test cycle graph weights  
**Expected**: self.assertEqual([x for x in range(20)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual([x for x in range(20)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_cycle.py:57*

### test_cycle_graph_weights

**Category**: method_call  
**Description**: test cycle graph weights  
**Expected**: self.assertEqual(len(graph.edges()), 20)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([x for x in range(20)], graph.nodes())
self.assertEqual(len(graph.edges()), 20)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_cycle.py:58*

### test_directed_cycle_graph

**Category**: method_call  
**Description**: test directed cycle graph  
**Expected**: self.assertEqual(len(graph.edges()), 20)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 20)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_cycle.py:21*

### test_directed_cycle_graph_weights

**Category**: method_call  
**Description**: test directed cycle graph weights  
**Expected**: self.assertEqual([x for x in range(20)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual([x for x in range(20)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_cycle.py:29*

### test_single_neighbor

**Category**: method_call  
**Description**: test single neighbor  
**Expected**: self.assertFalse(digraph.is_symmetric())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
digraph.add_child(node_a, 'c', {'a': 2})
self.assertFalse(digraph.is_symmetric())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_symmetric.py:27*

### test_bidirectional_ring

**Category**: method_call  
**Description**: test bidirectional ring  
**Expected**: self.assertTrue(digraph.is_symmetric())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
digraph.extend_from_edge_list(edge_list)
self.assertTrue(digraph.is_symmetric())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_symmetric.py:42*

### test_empty_graph_make_symmetric

**Category**: method_call  
**Description**: test empty graph make symmetric  
**Expected**: self.assertEqual(0, digraph.num_edges())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
digraph.make_symmetric()
self.assertEqual(0, digraph.num_edges())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_symmetric.py:47*

### test_empty_graph_make_symmetric

**Category**: method_call  
**Description**: test empty graph make symmetric  
**Expected**: self.assertEqual(0, digraph.num_nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(0, digraph.num_edges())
self.assertEqual(0, digraph.num_nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_symmetric.py:48*

### test_empty_graph_make_symmetric_with_function_arg

**Category**: method_call  
**Description**: test empty graph make symmetric with function arg  
**Expected**: self.assertEqual(0, digraph.num_edges())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
digraph.make_symmetric(default_weight_function)
self.assertEqual(0, digraph.num_edges())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_symmetric.py:81*

### test_empty_graph_make_symmetric_with_function_arg

**Category**: method_call  
**Description**: test empty graph make symmetric with function arg  
**Expected**: self.assertEqual(0, digraph.num_nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(0, digraph.num_edges())
self.assertEqual(0, digraph.num_nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_symmetric.py:82*

### test_single_neighbor

**Category**: method_call  
**Description**: test single neighbor  
**Expected**: self.assertFalse(digraph.is_symmetric())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
digraph.add_child(node_a, 'c', {'a': 2})
self.assertFalse(digraph.is_symmetric())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_symmetric.py:27*

### test_bidirectional_ring

**Category**: method_call  
**Description**: test bidirectional ring  
**Expected**: self.assertTrue(digraph.is_symmetric())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
digraph.extend_from_edge_list(edge_list)
self.assertTrue(digraph.is_symmetric())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_symmetric.py:42*

### test_empty_graph_make_symmetric

**Category**: method_call  
**Description**: test empty graph make symmetric  
**Expected**: self.assertEqual(0, digraph.num_edges())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
digraph.make_symmetric()
self.assertEqual(0, digraph.num_edges())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_symmetric.py:47*

### test_empty_graph_make_symmetric

**Category**: method_call  
**Description**: test empty graph make symmetric  
**Expected**: self.assertEqual(0, digraph.num_nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(0, digraph.num_edges())
self.assertEqual(0, digraph.num_nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_symmetric.py:48*

### test_directed_empty

**Category**: method_call  
**Description**: test directed empty  
**Expected**: self.assertEqual(res, {})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.example_edges = [(0, 2), (0, 3), (0, 5), (1, 4), (1, 6), (1, 7), (2, 3), (3, 5), (2, 5), (5, 6), (4, 6), (4, 7), (6, 7), (5, 8), (6, 8), (6, 9), (8, 9), (0, 10), (1, 10), (1, 11), (10, 11), (12, 13), (13, 15), (14, 15), (12, 14), (8, 19), (11, 16), (11, 17), (12, 18)]
example_core = {}
for i in range(8):
    example_core[i] = 3
for i in range(8, 16):
    example_core[i] = 2
for i in range(16, 20):
    example_core[i] = 1
example_core[20] = 0
self.example_core = example_core

self.assertIsInstance(res, dict)
self.assertEqual(res, {})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_core_number.py:72*

### test_directed_all_0

**Category**: method_call  
**Description**: test directed all 0  
**Expected**: self.assertEqual(res, {0: 0, 1: 0, 2: 0, 3: 0})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.example_edges = [(0, 2), (0, 3), (0, 5), (1, 4), (1, 6), (1, 7), (2, 3), (3, 5), (2, 5), (5, 6), (4, 6), (4, 7), (6, 7), (5, 8), (6, 8), (6, 9), (8, 9), (0, 10), (1, 10), (1, 11), (10, 11), (12, 13), (13, 15), (14, 15), (12, 14), (8, 19), (11, 16), (11, 17), (12, 18)]
example_core = {}
for i in range(8):
    example_core[i] = 3
for i in range(8, 16):
    example_core[i] = 2
for i in range(16, 20):
    example_core[i] = 1
example_core[20] = 0
self.example_core = example_core

self.assertIsInstance(res, dict)
self.assertEqual(res, {0: 0, 1: 0, 2: 0, 3: 0})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_core_number.py:79*

### test_directed_all_3

**Category**: method_call  
**Description**: test directed all 3  
**Expected**: self.assertEqual(res, {0: 3, 1: 3, 2: 3, 3: 3})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.example_edges = [(0, 2), (0, 3), (0, 5), (1, 4), (1, 6), (1, 7), (2, 3), (3, 5), (2, 5), (5, 6), (4, 6), (4, 7), (6, 7), (5, 8), (6, 8), (6, 9), (8, 9), (0, 10), (1, 10), (1, 11), (10, 11), (12, 13), (13, 15), (14, 15), (12, 14), (8, 19), (11, 16), (11, 17), (12, 18)]
example_core = {}
for i in range(8):
    example_core[i] = 3
for i in range(8, 16):
    example_core[i] = 2
for i in range(16, 20):
    example_core[i] = 1
example_core[20] = 0
self.example_core = example_core

self.assertIsInstance(res, dict)
self.assertEqual(res, {0: 3, 1: 3, 2: 3, 3: 3})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_core_number.py:87*

### test_directed_paper_example

**Category**: method_call  
**Description**: test directed paper example  
**Expected**: self.assertEqual(res, self.example_core)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.example_edges = [(0, 2), (0, 3), (0, 5), (1, 4), (1, 6), (1, 7), (2, 3), (3, 5), (2, 5), (5, 6), (4, 6), (4, 7), (6, 7), (5, 8), (6, 8), (6, 9), (8, 9), (0, 10), (1, 10), (1, 11), (10, 11), (12, 13), (13, 15), (14, 15), (12, 14), (8, 19), (11, 16), (11, 17), (12, 18)]
example_core = {}
for i in range(8):
    example_core[i] = 3
for i in range(8, 16):
    example_core[i] = 2
for i in range(16, 20):
    example_core[i] = 1
example_core[20] = 0
self.example_core = example_core

self.assertIsInstance(res, dict)
self.assertEqual(res, self.example_core)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_core_number.py:95*

### test_directed_empty

**Category**: method_call  
**Description**: test directed empty  
**Expected**: self.assertEqual(res, {})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(res, dict)
self.assertEqual(res, {})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_core_number.py:72*

### test_directed_all_0

**Category**: method_call  
**Description**: test directed all 0  
**Expected**: self.assertEqual(res, {0: 0, 1: 0, 2: 0, 3: 0})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(res, dict)
self.assertEqual(res, {0: 0, 1: 0, 2: 0, 3: 0})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_core_number.py:79*

### test_directed_all_3

**Category**: method_call  
**Description**: test directed all 3  
**Expected**: self.assertEqual(res, {0: 3, 1: 3, 2: 3, 3: 3})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(res, dict)
self.assertEqual(res, {0: 3, 1: 3, 2: 3, 3: 3})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_core_number.py:87*

### test_directed_paper_example

**Category**: method_call  
**Description**: test directed paper example  
**Expected**: self.assertEqual(res, self.example_core)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(res, dict)
self.assertEqual(res, self.example_core)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_core_number.py:95*

### test_lollipop_graph_count

**Category**: method_call  
**Description**: test lollipop graph count  
**Expected**: self.assertEqual(len(graph.edges()), 139)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 139)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_lollipop.py:21*

### test_lollipop_graph_weights_count

**Category**: method_call  
**Description**: test lollipop graph weights count  
**Expected**: self.assertEqual(list(range(20)), graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(list(range(20)), graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_lollipop.py:28*

### test_lollipop_graph_weights_count

**Category**: method_call  
**Description**: test lollipop graph weights count  
**Expected**: self.assertEqual(len(graph.edges()), 139)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(range(20)), graph.nodes())
self.assertEqual(len(graph.edges()), 139)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_lollipop.py:29*

### test_lollipop_graph_weights_edge

**Category**: method_call  
**Description**: test lollipop graph weights edge  
**Expected**: self.assertEqual(graph.nodes(), [0, 1, 2, 3, 0, 1, 2])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(weighted_edge_list, expected_weighted_edge_list)
self.assertEqual(graph.nodes(), [0, 1, 2, 3, 0, 1, 2])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_lollipop.py:64*

### test_lollipop_graph_no_path_weights_or_num

**Category**: method_call  
**Description**: test lollipop graph no path weights or num  
**Expected**: self.assertEqual(graph.weighted_edge_list(), mesh.weighted_edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.nodes(), mesh.nodes())
self.assertEqual(graph.weighted_edge_list(), mesh.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_lollipop.py:70*

### test_lollipop_graph_no_path_weights_or_num

**Category**: method_call  
**Description**: test lollipop graph no path weights or num  
**Expected**: self.assertEqual(rustworkx.generators.lollipop_graph(4).edge_list(), rustworkx.generators.mesh_graph(4).edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.weighted_edge_list(), mesh.weighted_edge_list())
self.assertEqual(rustworkx.generators.lollipop_graph(4).edge_list(), rustworkx.generators.mesh_graph(4).edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_lollipop.py:71*

### test_lollipop_graph_count

**Category**: method_call  
**Description**: test lollipop graph count  
**Expected**: self.assertEqual(len(graph.edges()), 139)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 139)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_lollipop.py:21*

### test_lollipop_graph_weights_count

**Category**: method_call  
**Description**: test lollipop graph weights count  
**Expected**: self.assertEqual(list(range(20)), graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(list(range(20)), graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_lollipop.py:28*

### test_lollipop_graph_weights_count

**Category**: method_call  
**Description**: test lollipop graph weights count  
**Expected**: self.assertEqual(len(graph.edges()), 139)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(range(20)), graph.nodes())
self.assertEqual(len(graph.edges()), 139)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_lollipop.py:29*

### test_lollipop_graph_weights_edge

**Category**: method_call  
**Description**: test lollipop graph weights edge  
**Expected**: self.assertEqual(graph.nodes(), [0, 1, 2, 3, 0, 1, 2])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(weighted_edge_list, expected_weighted_edge_list)
self.assertEqual(graph.nodes(), [0, 1, 2, 3, 0, 1, 2])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_lollipop.py:64*

### test_graph_dfs_tree_edges

**Category**: method_call  
**Description**: test graph dfs tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (3, 1)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.graph_dfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (3, 1)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_search.py:43*

### test_graph_dfs_tree_edges_no_starting_point

**Category**: method_call  
**Description**: test graph dfs tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (3, 1), (4, 7)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.graph_dfs_search(self.graph, None, vis)
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (3, 1), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_search.py:55*

### test_graph_dfs_tree_edges_restricted

**Category**: method_call  
**Description**: test graph dfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.graph_dfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_search.py:72*

### test_graph_dfs_tree_edges

**Category**: method_call  
**Description**: test graph dfs tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (3, 1)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
rustworkx.graph_dfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (3, 1)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_search.py:43*

### test_graph_dfs_tree_edges_no_starting_point

**Category**: method_call  
**Description**: test graph dfs tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (3, 1), (4, 7)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
rustworkx.graph_dfs_search(self.graph, None, vis)
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (5, 3), (3, 1), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_search.py:55*

### test_graph_dfs_tree_edges_restricted

**Category**: method_call  
**Description**: test graph dfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
rustworkx.graph_dfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_search.py:72*

### test_graph_to_dot_to_file

**Category**: method_call  
**Description**: test graph to dot to file  
**Expected**: self.assertIsNone(res)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

self.addCleanup(os.remove, self.path)
self.assertIsNone(res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dot.py:105*

### test_from_dot_graph

**Category**: method_call  
**Description**: test from dot graph  
**Expected**: self.assertEqual(len(g.edges()), 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

self.assertEqual(len(g.nodes()), 2)
self.assertEqual(len(g.edges()), 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dot.py:139*

### test_from_dot_digraph

**Category**: method_call  
**Description**: test from dot digraph  
**Expected**: self.assertEqual(len(g.edges()), 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

self.assertEqual(len(g.nodes()), 2)
self.assertEqual(len(g.edges()), 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dot.py:149*

### test_graph_roundtrip_with_attrs

**Category**: method_call  
**Description**: test graph roundtrip with attrs  
**Expected**: self.assertEqual(len(g2.edges()), 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

self.assertEqual(len(g2.nodes()), 2)
self.assertEqual(len(g2.edges()), 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dot.py:176*

### test_digraph_roundtrip_with_attrs

**Category**: method_call  
**Description**: test digraph roundtrip with attrs  
**Expected**: self.assertEqual(len(g2.edges()), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

self.assertEqual(len(g2.nodes()), 2)
self.assertEqual(len(g2.edges()), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dot.py:204*

### test_graph_to_dot_to_file

**Category**: method_call  
**Description**: test graph to dot to file  
**Expected**: self.assertIsNone(res)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.addCleanup(os.remove, self.path)
self.assertIsNone(res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dot.py:105*

### test_from_dot_graph

**Category**: method_call  
**Description**: test from dot graph  
**Expected**: self.assertEqual(len(g.edges()), 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(g.nodes()), 2)
self.assertEqual(len(g.edges()), 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dot.py:139*

### test_from_dot_digraph

**Category**: method_call  
**Description**: test from dot digraph  
**Expected**: self.assertEqual(len(g.edges()), 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(g.nodes()), 2)
self.assertEqual(len(g.edges()), 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dot.py:149*

### test_clear

**Category**: method_call  
**Description**: test clear  
**Expected**: self.assertEqual(dag.num_nodes(), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
dag.clear()
self.assertEqual(dag.num_nodes(), 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_clear.py:24*

### test_clear

**Category**: method_call  
**Description**: test clear  
**Expected**: self.assertEqual(dag.num_edges(), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dag.num_nodes(), 0)
self.assertEqual(dag.num_edges(), 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_clear.py:25*

### test_clear

**Category**: method_call  
**Description**: test clear  
**Expected**: self.assertEqual(dag.nodes(), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dag.num_edges(), 0)
self.assertEqual(dag.nodes(), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_clear.py:26*

### test_clear

**Category**: method_call  
**Description**: test clear  
**Expected**: self.assertEqual(dag.edges(), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dag.nodes(), [])
self.assertEqual(dag.edges(), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_clear.py:27*

### test_clear_reuse

**Category**: method_call  
**Description**: test clear reuse  
**Expected**: self.assertEqual(dag.num_nodes(), 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
dag.add_child(node_a, 'c', {'a': 2})
self.assertEqual(dag.num_nodes(), 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_clear.py:38*

### test_clear_reuse

**Category**: method_call  
**Description**: test clear reuse  
**Expected**: self.assertEqual(dag.num_edges(), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dag.num_nodes(), 3)
self.assertEqual(dag.num_edges(), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_clear.py:39*

### test_clear_reuse

**Category**: method_call  
**Description**: test clear reuse  
**Expected**: self.assertEqual(dag.nodes(), ['a', 'b', 'c'])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dag.num_edges(), 2)
self.assertEqual(dag.nodes(), ['a', 'b', 'c'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_clear.py:40*

### test_clear_reuse

**Category**: method_call  
**Description**: test clear reuse  
**Expected**: self.assertEqual(dag.edges(), [{'a': 1}, {'a': 2}])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dag.nodes(), ['a', 'b', 'c'])
self.assertEqual(dag.edges(), [{'a': 1}, {'a': 2}])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_clear.py:41*

### test_cycle_no_source

**Category**: method_call  
**Description**: test cycle no source  
**Expected**: self.assertTrue(res[0] == res[1][::-1])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.add_nodes_from(list(range(10)))
self.graph.add_edges_from_no_data([(0, 1), (3, 0), (0, 5), (8, 0), (1, 2), (1, 6), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9)])

self.assertEqual(len(res), 2)
self.assertTrue(res[0] == res[1][::-1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_find_cycle.py:95*

### test_cycle_no_source

**Category**: method_call  
**Description**: test cycle no source  
**Expected**: self.assertTrue(res[0] == res[1][::-1])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(res), 2)
self.assertTrue(res[0] == res[1][::-1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_find_cycle.py:95*

### test_graph_dijkstra_tree_edges

**Category**: method_call  
**Description**: test graph dijkstra tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

rustworkx.graph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra_search.py:50*

### test_graph_dijkstra_tree_edges_no_starting_point

**Category**: method_call  
**Description**: test graph dijkstra tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3), (4, 7)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

rustworkx.graph_dijkstra_search(self.graph, None, float, vis)
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra_search.py:69*

### test_graph_dijkstra_goal_search_with_stop_search_exception

**Category**: method_call  
**Description**: test graph dijkstra goal search with stop search exception  
**Expected**: self.assertEqual(vis.reconstruct_path(), [0, 2, 5, 3])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

rustworkx.graph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.reconstruct_path(), [0, 2, 5, 3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra_search.py:100*

### test_graph_dijkstra_goal_search_with_stop_search_exception

**Category**: method_call  
**Description**: test graph dijkstra goal search with stop search exception  
**Expected**: self.assertEqual(vis.opt_goal_cost, 4.0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

self.assertEqual(vis.reconstruct_path(), [0, 2, 5, 3])
self.assertEqual(vis.opt_goal_cost, 4.0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dijkstra_search.py:101*

### test_directed_hexagonal_graph_2_2

**Category**: method_call  
**Description**: test directed hexagonal graph 2 2  
**Expected**: self.assertEqual(len(graph.edges()), len(expected_edges))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 16)
self.assertEqual(len(graph.edges()), len(expected_edges))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_hexagonal.py:45*

### test_directed_hexagonal_graph_2_2

**Category**: method_call  
**Description**: test directed hexagonal graph 2 2  
**Expected**: self.assertEqual(list(graph.edge_list()), expected_edges)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph.edges()), len(expected_edges))
self.assertEqual(list(graph.edge_list()), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_hexagonal.py:46*

### test_directed_hexagonal_graph_3_2

**Category**: method_call  
**Description**: test directed hexagonal graph 3 2  
**Expected**: self.assertEqual(len(graph.edges()), len(expected_edges))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 22)
self.assertEqual(len(graph.edges()), len(expected_edges))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_hexagonal.py:80*

### test_directed_hexagonal_graph_3_2

**Category**: method_call  
**Description**: test directed hexagonal graph 3 2  
**Expected**: self.assertEqual(list(graph.edge_list()), expected_edges)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph.edges()), len(expected_edges))
self.assertEqual(list(graph.edge_list()), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_hexagonal.py:81*

### test_simple_graph_composition

**Category**: method_call  
**Description**: test simple graph composition  
**Expected**: self.assertEqual([0, 1, 2, 3, 4], graph.node_indexes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual({0: 3, 1: 4}, res)
self.assertEqual([0, 1, 2, 3, 4], graph.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_compose.py:31*

### test_edge_map_and_node_map_funcs_graph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs graph compose  
**Expected**: self.assertEqual(graph[res[other_output_nodes[0]]], 'qr[0]')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual({2: 4, 3: 3, 4: 5}, res)
self.assertEqual(graph[res[other_output_nodes[0]]], 'qr[0]')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_compose.py:74*

### test_edge_map_and_node_map_funcs_graph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs graph compose  
**Expected**: self.assertEqual(graph[res[other_output_nodes[1]]], 'qr[1]')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph[res[other_output_nodes[0]]], 'qr[0]')
self.assertEqual(graph[res[other_output_nodes[1]]], 'qr[1]')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_compose.py:75*

### test_edge_map_and_node_map_funcs_graph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs graph compose  
**Expected**: self.assertTrue(graph.has_edge(0, 2))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph[res[other_output_nodes[1]]], 'qr[1]')
self.assertTrue(graph.has_edge(0, 2))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_compose.py:76*

### test_edge_map_and_node_map_funcs_graph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs graph compose  
**Expected**: self.assertTrue(graph.get_all_edge_data(0, 2), ['qr[0]'])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.has_edge(0, 2))
self.assertTrue(graph.get_all_edge_data(0, 2), ['qr[0]'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_compose.py:78*

### test_edge_map_and_node_map_funcs_graph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs graph compose  
**Expected**: self.assertTrue(graph.has_edge(1, 4))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.get_all_edge_data(0, 2), ['qr[0]'])
self.assertTrue(graph.has_edge(1, 4))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_compose.py:79*

### test_edge_map_and_node_map_funcs_graph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs graph compose  
**Expected**: self.assertTrue(graph.get_all_edge_data(0, 2), ['qr[1]'])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.has_edge(1, 4))
self.assertTrue(graph.get_all_edge_data(0, 2), ['qr[1]'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_compose.py:81*

### test_edge_map_and_node_map_funcs_graph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs graph compose  
**Expected**: self.assertTrue(graph.has_edge(2, 4))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.get_all_edge_data(0, 2), ['qr[1]'])
self.assertTrue(graph.has_edge(2, 4))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_compose.py:82*

### test_two_colors_with_isolates

**Category**: method_call  
**Description**: test two colors with isolates  
**Expected**: self.assertEqual(rustworkx.two_color(graph), {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1, 7: 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertEqual(rustworkx.two_color(graph), {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1, 7: 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bipartite.py:29*

### test_is_bipartite_with_isolates

**Category**: method_call  
**Description**: test is bipartite with isolates  
**Expected**: self.assertTrue(rustworkx.is_bipartite(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertTrue(rustworkx.is_bipartite(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bipartite.py:36*

### test_two_colors_not_bipartite_with_isolates

**Category**: method_call  
**Description**: test two colors not bipartite with isolates  
**Expected**: self.assertIsNone(rustworkx.two_color(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertIsNone(rustworkx.two_color(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bipartite.py:41*

### test_not_bipartite_with_isolates

**Category**: method_call  
**Description**: test not bipartite with isolates  
**Expected**: self.assertFalse(rustworkx.is_bipartite(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertFalse(rustworkx.is_bipartite(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bipartite.py:46*

### test_two_colors_with_isolates

**Category**: method_call  
**Description**: test two colors with isolates  
**Expected**: self.assertEqual(rustworkx.two_color(graph), {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1, 7: 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertEqual(rustworkx.two_color(graph), {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1, 7: 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bipartite.py:29*

### test_is_bipartite_with_isolates

**Category**: method_call  
**Description**: test is bipartite with isolates  
**Expected**: self.assertTrue(rustworkx.is_bipartite(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertTrue(rustworkx.is_bipartite(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bipartite.py:36*

### test_two_colors_not_bipartite_with_isolates

**Category**: method_call  
**Description**: test two colors not bipartite with isolates  
**Expected**: self.assertIsNone(rustworkx.two_color(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertIsNone(rustworkx.two_color(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bipartite.py:41*

### test_not_bipartite_with_isolates

**Category**: method_call  
**Description**: test not bipartite with isolates  
**Expected**: self.assertFalse(rustworkx.is_bipartite(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_nodes_from(range(3))
self.assertFalse(rustworkx.is_bipartite(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bipartite.py:46*

### test_simple_graph

**Category**: method_call  
**Description**: test simple graph  
**Expected**: self.assertEqual(len(res[0]), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res), 3)
self.assertEqual(len(res[0]), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_spring_layout.py:34*

### test_simple_graph

**Category**: method_call  
**Description**: test simple graph  
**Expected**: self.assertIsInstance(res[0][0], float)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res[0]), 2)
self.assertIsInstance(res[0][0], float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_spring_layout.py:35*

### test_simple_graph_with_edge_weights

**Category**: method_call  
**Description**: test simple graph with edge weights  
**Expected**: self.assertEqual(len(res[0]), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res), 3)
self.assertEqual(len(res[0]), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_spring_layout.py:40*

### test_simple_graph_with_edge_weights

**Category**: method_call  
**Description**: test simple graph with edge weights  
**Expected**: self.assertIsInstance(res[0][0], float)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res[0]), 2)
self.assertIsInstance(res[0][0], float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_spring_layout.py:41*

### test_simple_graph_center

**Category**: method_call  
**Description**: test simple graph center  
**Expected**: self.assertEqual(len(res[0]), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res), 3)
self.assertEqual(len(res[0]), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_spring_layout.py:46*

### test_simple_graph_center

**Category**: method_call  
**Description**: test simple graph center  
**Expected**: self.assertIsInstance(res[0][0], float)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res[0]), 2)
self.assertIsInstance(res[0][0], float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_spring_layout.py:47*

### test_simple_graph_linear_cooling

**Category**: method_call  
**Description**: test simple graph linear cooling  
**Expected**: self.assertEqual(len(res[0]), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res), 3)
self.assertEqual(len(res[0]), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_spring_layout.py:61*

### test_simple_graph_linear_cooling

**Category**: method_call  
**Description**: test simple graph linear cooling  
**Expected**: self.assertIsInstance(res[0][0], float)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res[0]), 2)
self.assertIsInstance(res[0][0], float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_spring_layout.py:62*

### test_graph_with_removed_nodes

**Category**: method_call  
**Description**: test graph with removed nodes  
**Expected**: self.assertTrue(nodes[0] in res)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertEqual(len(res), 2)
self.assertTrue(nodes[0] in res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_spring_layout.py:70*

### test_graph_with_removed_nodes

**Category**: method_call  
**Description**: test graph with removed nodes  
**Expected**: self.assertTrue(nodes[2] in res)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
node_a = self.graph.add_node(1)
node_b = self.graph.add_node(2)
self.graph.add_edge(node_a, node_b, 1)
node_c = self.graph.add_node(3)
self.graph.add_edge(node_a, node_c, 2)

self.assertTrue(nodes[0] in res)
self.assertTrue(nodes[2] in res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_spring_layout.py:71*

### test_digraph_bfs_tree_edges

**Category**: method_call  
**Description**: test digraph bfs tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.digraph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_search.py:43*

### test_digraph_bfs_tree_edges_no_starting_point

**Category**: method_call  
**Description**: test digraph bfs tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3), (4, 7)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.digraph_bfs_search(self.graph, None, vis)
self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_search.py:55*

### test_digraph_bfs_tree_edges_restricted

**Category**: method_call  
**Description**: test digraph bfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (1, 3)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.digraph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 1), (1, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_search.py:72*

### test_digraph_bfs_goal_search_with_stop_search_exception

**Category**: method_call  
**Description**: test digraph bfs goal search with stop search exception  
**Expected**: self.assertEqual(vis.reconstruct_path(), [0, 1, 3])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.digraph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.reconstruct_path(), [0, 1, 3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_search.py:100*

### test_digraph_bfs_tree_edges

**Category**: method_call  
**Description**: test digraph bfs tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
rustworkx.digraph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_search.py:43*

### test_digraph_bfs_tree_edges_no_starting_point

**Category**: method_call  
**Description**: test digraph bfs tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3), (4, 7)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
rustworkx.digraph_bfs_search(self.graph, None, vis)
self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_search.py:55*

### test_subgraph

**Category**: method_call  
**Description**: test subgraph  
**Expected**: self.assertEqual(['b', 'd'], subgraph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([(0, 1, 4)], subgraph.weighted_edge_list())
self.assertEqual(['b', 'd'], subgraph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph.py:27*

### test_subgraph_empty_list

**Category**: method_call  
**Description**: test subgraph empty list  
**Expected**: self.assertEqual(0, len(subgraph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph.py:38*

### test_subgraph_invalid_entry

**Category**: method_call  
**Description**: test subgraph invalid entry  
**Expected**: self.assertEqual(0, len(subgraph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph.py:49*

### test_subgraph_pass_by_reference

**Category**: method_call  
**Description**: test subgraph pass by reference  
**Expected**: self.assertEqual([{'a': 0}, 'b', 'd'], subgraph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([(0, 1, 1), (0, 2, 3), (1, 2, 4)], subgraph.weighted_edge_list())
self.assertEqual([{'a': 0}, 'b', 'd'], subgraph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph.py:60*

### test_subgraph_replace_weight_no_reference

**Category**: method_call  
**Description**: test subgraph replace weight no reference  
**Expected**: self.assertEqual([{'a': 0}, 'b', 'd'], subgraph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([(0, 1, 1), (0, 2, 3), (1, 2, 4)], subgraph.weighted_edge_list())
self.assertEqual([{'a': 0}, 'b', 'd'], subgraph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph.py:73*

### test_edge_subgraph

**Category**: method_call  
**Description**: test edge subgraph  
**Expected**: self.assertEqual([(0, 1, 1), (1, 3, 4)], subgraph.weighted_edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(['a', 'b', 'd'], subgraph.nodes())
self.assertEqual([(0, 1, 1), (1, 3, 4)], subgraph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph.py:86*

### test_edge_subgraph_parallel_edge

**Category**: method_call  
**Description**: test edge subgraph parallel edge  
**Expected**: self.assertEqual([(0, 1, 2), (0, 1, 3), (1, 2, 4)], subgraph.weighted_edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([0, 1, 2], subgraph.nodes())
self.assertEqual([(0, 1, 2), (0, 1, 3), (1, 2, 4)], subgraph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph.py:103*

### test_edge_subgraph_non_edge

**Category**: method_call  
**Description**: test edge subgraph non edge  
**Expected**: self.assertEqual([(0, 1, 2), (0, 1, 3), (1, 2, 4)], subgraph.weighted_edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([0, 1, 2], subgraph.nodes())
self.assertEqual([(0, 1, 2), (0, 1, 3), (1, 2, 4)], subgraph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_subgraph.py:137*

### test_alternating_path

**Category**: method_call  
**Description**: test alternating path  
**Expected**: self.assertEqual(rx.generate_random_path(graph, 0, 3, None), [0, 1, 0, 1])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_edge(1, 0, None)
self.assertEqual(rx.generate_random_path(graph, 0, 3, None), [0, 1, 0, 1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_random_walk.py:37*

### test_alternating_path

**Category**: method_call  
**Description**: test alternating path  
**Expected**: self.assertEqual(rx.generate_random_path(graph, 0, 3, None), [0, 1, 0, 1])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_edge(1, 0, None)
self.assertEqual(rx.generate_random_path(graph, 0, 3, None), [0, 1, 0, 1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_random_walk.py:37*

### test_empty_replacement

**Category**: method_call  
**Description**: test empty replacement  
**Expected**: self.assertEqual([(0, 1), (1, 2)], self.graph.edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.path_graph(5)

self.assertEqual(res, {})
self.assertEqual([(0, 1), (1, 2)], self.graph.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_substitute_node_with_subgraph.py:25*

### test_single_node

**Category**: method_call  
**Description**: test single node  
**Expected**: self.assertEqual([(0, 1), (1, 5), (3, 4), (5, 3)], sorted(self.graph.edge_list()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.path_graph(5)

self.assertEqual(res, {0: 5})
self.assertEqual([(0, 1), (1, 5), (3, 4), (5, 3)], sorted(self.graph.edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_substitute_node_with_subgraph.py:31*

### test_node_filter

**Category**: method_call  
**Description**: test node filter  
**Expected**: self.assertEqual([(1, 2), (2, 3), (3, 4), (5, 6), (5, 7), (5, 8), (5, 9), (6, 7), (6, 8), (6, 9), (7, 1), (7, 8), (7, 9), (8, 9)], sorted(self.graph.edge_list()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.path_graph(5)

self.assertEqual(res, {i: i + 5 for i in range(5)})
self.assertEqual([(1, 2), (2, 3), (3, 4), (5, 6), (5, 7), (5, 8), (5, 9), (6, 7), (6, 8), (6, 9), (7, 1), (7, 8), (7, 9), (8, 9)], sorted(self.graph.edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_substitute_node_with_subgraph.py:39*

### test_edge_weight_modifier

**Category**: method_call  
**Description**: test edge weight modifier  
**Expected**: self.assertEqual('edge-migrated', self.graph.get_edge_data(5, 6))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.path_graph(5)

self.assertEqual([(0, 1), (3, 4), (5, 6), (1, 5), (5, 3)], self.graph.edge_list())
self.assertEqual('edge-migrated', self.graph.get_edge_data(5, 6))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_substitute_node_with_subgraph.py:79*

### test_edge_weight_modifier

**Category**: method_call  
**Description**: test edge weight modifier  
**Expected**: self.assertEqual(res, {0: 5, 1: 6})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.path_graph(5)

self.assertEqual('edge-migrated', self.graph.get_edge_data(5, 6))
self.assertEqual(res, {0: 5, 1: 6})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_substitute_node_with_subgraph.py:80*

### test_none_mapping

**Category**: method_call  
**Description**: test none mapping  
**Expected**: self.assertEqual(res, {0: 5, 1: 6})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.graph = rustworkx.generators.path_graph(5)

self.assertEqual([(0, 1), (3, 4), (5, 6)], self.graph.edge_list())
self.assertEqual(res, {0: 5, 1: 6})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_substitute_node_with_subgraph.py:89*

### test_binomial_tree_graph_weights

**Category**: method_call  
**Description**: test binomial tree graph weights  
**Expected**: self.assertEqual([x for x in range(4)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 4)
self.assertEqual([x for x in range(4)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_binomial_tree.py:53*

### test_binomial_tree_graph_weights

**Category**: method_call  
**Description**: test binomial tree graph weights  
**Expected**: self.assertEqual(len(graph.edges()), 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([x for x in range(4)], graph.nodes())
self.assertEqual(len(graph.edges()), 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_binomial_tree.py:54*

### test_binomial_tree_graph_weights

**Category**: method_call  
**Description**: test binomial tree graph weights  
**Expected**: self.assertEqual(list(graph.edge_list()), expected_edges)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph.edges()), 3)
self.assertEqual(list(graph.edge_list()), expected_edges)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_binomial_tree.py:55*

### test_binomial_tree_graph_weight_less_nodes

**Category**: method_call  
**Description**: test binomial tree graph weight less nodes  
**Expected**: self.assertEqual(expected_weights, graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
expected_weights.extend([None, None])
self.assertEqual(expected_weights, graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_binomial_tree.py:62*

### test_binomial_tree_graph_weight_less_nodes

**Category**: method_call  
**Description**: test binomial tree graph weight less nodes  
**Expected**: self.assertEqual(len(graph.edges()), 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(expected_weights, graph.nodes())
self.assertEqual(len(graph.edges()), 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_binomial_tree.py:63*

### test_directed_binomial_tree_graph_weights

**Category**: method_call  
**Description**: test directed binomial tree graph weights  
**Expected**: self.assertEqual([x for x in range(4)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 4)
self.assertEqual([x for x in range(4)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_binomial_tree.py:108*

### test_directed_binomial_tree_graph_weights

**Category**: method_call  
**Description**: test directed binomial tree graph weights  
**Expected**: self.assertEqual(len(graph.edges()), 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([x for x in range(4)], graph.nodes())
self.assertEqual(len(graph.edges()), 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_binomial_tree.py:109*

### test_directed_binomial_tree_graph_weight_less_nodes

**Category**: method_call  
**Description**: test directed binomial tree graph weight less nodes  
**Expected**: self.assertEqual(expected_weights, graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
expected_weights.extend([None, None])
self.assertEqual(expected_weights, graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_binomial_tree.py:116*

### test_directed_binomial_tree_graph_weight_less_nodes

**Category**: method_call  
**Description**: test directed binomial tree graph weight less nodes  
**Expected**: self.assertEqual(len(graph.edges()), 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(expected_weights, graph.nodes())
self.assertEqual(len(graph.edges()), 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_binomial_tree.py:117*

### test_binomial_tree_graph_weights

**Category**: method_call  
**Description**: test binomial tree graph weights  
**Expected**: self.assertEqual([x for x in range(4)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 4)
self.assertEqual([x for x in range(4)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_binomial_tree.py:53*

### test_filter_nodes

**Category**: method_call  
**Description**: test filter nodes  
**Expected**: self.assertEqual(list(lizard_indices), [3])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(cat_indices), [0, 1, 4])
self.assertEqual(list(lizard_indices), [3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_filter.py:38*

### test_filter_nodes

**Category**: method_call  
**Description**: test filter nodes  
**Expected**: self.assertEqual(list(human_indices), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(lizard_indices), [3])
self.assertEqual(list(human_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_filter.py:39*

### test_filter_edges

**Category**: method_call  
**Description**: test filter edges  
**Expected**: self.assertEqual(list(enemies_indices), [2])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(friends_indices), [0, 1])
self.assertEqual(list(enemies_indices), [2])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_filter.py:64*

### test_filter_edges

**Category**: method_call  
**Description**: test filter edges  
**Expected**: self.assertEqual(list(frenemies_indices), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(enemies_indices), [2])
self.assertEqual(list(frenemies_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_filter.py:65*

### test_filter_nodes

**Category**: method_call  
**Description**: test filter nodes  
**Expected**: self.assertEqual(list(lizard_indices), [3])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(cat_indices), [0, 1, 4])
self.assertEqual(list(lizard_indices), [3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_filter.py:38*

### test_filter_nodes

**Category**: method_call  
**Description**: test filter nodes  
**Expected**: self.assertEqual(list(human_indices), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(lizard_indices), [3])
self.assertEqual(list(human_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_filter.py:39*

### test_simple

**Category**: method_call  
**Description**: Test a simple permutation on a path graph of size 4.  
**Expected**: self.assertEqual(3, len(swaps))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test cases.'
super().setUp()
random.seed(0)

swap_permutation(permutation, swaps)
self.assertEqual(3, len(swaps))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_token_swapper.py:47*

### test_simple

**Category**: method_call  
**Description**: Test a simple permutation on a path graph of size 4.  
**Expected**: self.assertEqual({i: i for i in range(4)}, permutation)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test cases.'
super().setUp()
random.seed(0)

self.assertEqual(3, len(swaps))
self.assertEqual({i: i for i in range(4)}, permutation)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_token_swapper.py:48*

### test_small

**Category**: method_call  
**Description**: Test an inverting permutation on a small path graph of size 8  
**Expected**: self.assertEqual({i: i for i in range(8)}, permutation)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test cases.'
super().setUp()
random.seed(0)

swap_permutation(permutation, swaps)
self.assertEqual({i: i for i in range(8)}, permutation)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_token_swapper.py:56*

### test_bug1

**Category**: method_call  
**Description**: Tests for a bug that occurred in happy swap chains of length >2.  
**Expected**: self.assertEqual({i: i for i in permutation}, permutation)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test cases.'
super().setUp()
random.seed(0)

swap_permutation(permutation, swaps)
self.assertEqual({i: i for i in permutation}, permutation)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_token_swapper.py:67*

### test_partial_simple

**Category**: method_call  
**Description**: Test a partial mapping on a small graph.  
**Expected**: self.assertEqual(3, len(swaps))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test cases.'
super().setUp()
random.seed(0)

swap_permutation(mapping, swaps)
self.assertEqual(3, len(swaps))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_token_swapper.py:75*

### test_partial_simple

**Category**: method_call  
**Description**: Test a partial mapping on a small graph.  
**Expected**: self.assertEqual({3: 3}, mapping)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test cases.'
super().setUp()
random.seed(0)

self.assertEqual(3, len(swaps))
self.assertEqual({3: 3}, mapping)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_token_swapper.py:76*

### test_partial_simple_remove_node

**Category**: method_call  
**Description**: Test a partial mapping on a small graph with a node removed.  
**Expected**: self.assertEqual(2, len(swaps))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test cases.'
super().setUp()
random.seed(0)

swap_permutation(mapping, swaps)
self.assertEqual(2, len(swaps))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_token_swapper.py:86*

### test_partial_simple_remove_node

**Category**: method_call  
**Description**: Test a partial mapping on a small graph with a node removed.  
**Expected**: self.assertEqual({3: 3}, mapping)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test cases.'
super().setUp()
random.seed(0)

self.assertEqual(2, len(swaps))
self.assertEqual({3: 3}, mapping)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_token_swapper.py:87*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(graph[node_a], {'a': 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph[node_a], {'a': 1})
self.assertEqual(graph[node_a], {'a': 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_to_directed.py:70*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(graph[node_a], {'a': 1, 'b': 2})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph[node_a], {'a': 1, 'b': 2})
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_to_directed.py:73*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_to_directed.py:74*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(graph.get_edge_data(0, 1), {'a': 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_to_directed.py:75*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1, 'b': 2})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_to_directed.py:78*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(graph[node_a], {'a': 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph[node_a], {'a': 1})
self.assertEqual(graph[node_a], {'a': 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_to_directed.py:70*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(graph[node_a], {'a': 1, 'b': 2})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph[node_a], {'a': 1, 'b': 2})
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_to_directed.py:73*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_to_directed.py:74*

### test_min_cut_graph_single_edge

**Category**: method_call  
**Description**: test min cut graph single edge  
**Expected**: self.assertEqual(partition, [1])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(value, 10.0)
self.assertEqual(partition, [1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_min_cut.py:35*

### test_min_cut_graph_parallel_edge

**Category**: method_call  
**Description**: test min cut graph parallel edge  
**Expected**: self.assertEqual(partition, [1])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(value, 10.0)
self.assertEqual(partition, [1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_min_cut.py:42*

### test_min_cut_graph_nan_edge_weight

**Category**: method_call  
**Description**: test min cut graph nan edge weight  
**Expected**: self.assertEqual(partition, [1])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(value, 4.0)
self.assertEqual(partition, [1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_min_cut.py:108*

### test_min_cut_graph_single_edge

**Category**: method_call  
**Description**: test min cut graph single edge  
**Expected**: self.assertEqual(partition, [1])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(value, 10.0)
self.assertEqual(partition, [1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_min_cut.py:35*

### test_min_cut_graph_parallel_edge

**Category**: method_call  
**Description**: test min cut graph parallel edge  
**Expected**: self.assertEqual(partition, [1])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(value, 10.0)
self.assertEqual(partition, [1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_min_cut.py:42*

### test_min_cut_graph_nan_edge_weight

**Category**: method_call  
**Description**: test min cut graph nan edge weight  
**Expected**: self.assertEqual(partition, [1])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(value, 4.0)
self.assertEqual(partition, [1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_min_cut.py:108*

### test_filename

**Category**: method_call  
**Description**: test filename  
**Expected**: self.assertTrue(os.path.isfile('test_graphviz_filename.svg'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graphviz_draw(graph, filename='test_graphviz_filename.svg', image_type='svg', method='neato')
self.assertTrue(os.path.isfile('test_graphviz_filename.svg'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_graphviz.py:143*

### test_qiskit_style_visualization

**Category**: method_call  
**Description**: This test is to test visualizations like qiskit performs which regressed in 0.15.0.  
**Expected**: self.assertTrue(os.path.isfile('test_qiskit_style_visualization.png'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graphviz_draw(graph, node_attr_fn=color_node, edge_attr_fn=color_edge, filename='test_qiskit_style_visualization.png', image_type='png', method='neato')
self.assertTrue(os.path.isfile('test_qiskit_style_visualization.png'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_graphviz.py:190*

### test_filename

**Category**: method_call  
**Description**: test filename  
**Expected**: self.assertTrue(os.path.isfile('test_graphviz_filename.svg'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graphviz_draw(graph, filename='test_graphviz_filename.svg', image_type='svg', method='neato')
self.assertTrue(os.path.isfile('test_graphviz_filename.svg'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_graphviz.py:143*

### test_qiskit_style_visualization

**Category**: method_call  
**Description**: This test is to test visualizations like qiskit performs which regressed in 0.15.0.  
**Expected**: self.assertTrue(os.path.isfile('test_qiskit_style_visualization.png'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graphviz_draw(graph, node_attr_fn=color_node, edge_attr_fn=color_edge, filename='test_qiskit_style_visualization.png', image_type='png', method='neato')
self.assertTrue(os.path.isfile('test_qiskit_style_visualization.png'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_graphviz.py:190*

### test_random_layout_no_seed

**Category**: method_call  
**Description**: test random layout no seed  
**Expected**: self.assertEqual(len(res), 10)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.directed_path_graph(10)

self.assertIsInstance(res, rustworkx.Pos2DMapping)
self.assertEqual(len(res), 10)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layout.py:71*

### test_random_layout_no_seed

**Category**: method_call  
**Description**: test random layout no seed  
**Expected**: self.assertEqual(len(res[0]), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.directed_path_graph(10)

self.assertEqual(len(res), 10)
self.assertEqual(len(res[0]), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layout.py:72*

### test_random_layout_no_seed

**Category**: method_call  
**Description**: test random layout no seed  
**Expected**: self.assertIsInstance(res[0][0], float)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.directed_path_graph(10)

self.assertEqual(len(res[0]), 2)
self.assertIsInstance(res[0][0], float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layout.py:73*

### test_random_layout_no_seed

**Category**: method_call  
**Description**: test random layout no seed  
**Expected**: self.assertEqual(len(res), 10)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(res, rustworkx.Pos2DMapping)
self.assertEqual(len(res), 10)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layout.py:71*

### test_random_layout_no_seed

**Category**: method_call  
**Description**: test random layout no seed  
**Expected**: self.assertEqual(len(res[0]), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(res), 10)
self.assertEqual(len(res[0]), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layout.py:72*

### test_random_layout_no_seed

**Category**: method_call  
**Description**: test random layout no seed  
**Expected**: self.assertIsInstance(res[0][0], float)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(res[0]), 2)
self.assertIsInstance(res[0][0], float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layout.py:73*

### test_tr_with_deletion

**Category**: method_call  
**Description**: test tr with deletion  
**Expected**: self.assertEqual(index_map[4], 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertCountEqual(list(tr.edge_list()), [(0, 1), (0, 2), (2, 3)])
self.assertEqual(index_map[4], 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitive_reduction.py:70*

### test_tr_with_deletion

**Category**: method_call  
**Description**: test tr with deletion  
**Expected**: self.assertEqual(index_map[4], 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertCountEqual(list(tr.edge_list()), [(0, 1), (0, 2), (2, 3)])
self.assertEqual(index_map[4], 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitive_reduction.py:70*

### test_number_weakly_connected_all_strong

**Category**: method_call  
**Description**: test number weakly connected all strong  
**Expected**: self.assertEqual(rustworkx.number_weakly_connected_components(G), 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
G.add_child(node_b, 3, {})
self.assertEqual(rustworkx.number_weakly_connected_components(G), 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_weakly_connected.py:23*

### test_number_weakly_connected

**Category**: method_call  
**Description**: test number weakly connected  
**Expected**: self.assertEqual(rustworkx.number_weakly_connected_components(G), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
G.add_node(3)
self.assertEqual(rustworkx.number_weakly_connected_components(G), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_weakly_connected.py:30*

### test_number_weakly_connected_node_holes

**Category**: method_call  
**Description**: test number weakly connected node holes  
**Expected**: self.assertEqual(rustworkx.number_weakly_connected_components(graph), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.remove_node(1)
self.assertEqual(rustworkx.number_weakly_connected_components(graph), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_weakly_connected.py:43*

### test_is_weakly_connected_false

**Category**: method_call  
**Description**: test is weakly connected false  
**Expected**: self.assertFalse(rustworkx.is_weakly_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4)])
self.assertFalse(rustworkx.is_weakly_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_weakly_connected.py:56*

### test_is_weakly_connected_true

**Category**: method_call  
**Description**: test is weakly connected true  
**Expected**: self.assertTrue(rustworkx.is_weakly_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 0), (2, 4), (4, 5), (5, 6), (6, 7), (7, 4)])
self.assertTrue(rustworkx.is_weakly_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_weakly_connected.py:63*

### test_number_weakly_connected_all_strong

**Category**: method_call  
**Description**: test number weakly connected all strong  
**Expected**: self.assertEqual(rustworkx.number_weakly_connected_components(G), 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
G.add_child(node_b, 3, {})
self.assertEqual(rustworkx.number_weakly_connected_components(G), 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_weakly_connected.py:23*

### test_number_weakly_connected

**Category**: method_call  
**Description**: test number weakly connected  
**Expected**: self.assertEqual(rustworkx.number_weakly_connected_components(G), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
G.add_node(3)
self.assertEqual(rustworkx.number_weakly_connected_components(G), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_weakly_connected.py:30*

### test_number_weakly_connected_node_holes

**Category**: method_call  
**Description**: test number weakly connected node holes  
**Expected**: self.assertEqual(rustworkx.number_weakly_connected_components(graph), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.remove_node(1)
self.assertEqual(rustworkx.number_weakly_connected_components(graph), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_weakly_connected.py:43*

### test_is_weakly_connected_false

**Category**: method_call  
**Description**: test is weakly connected false  
**Expected**: self.assertFalse(rustworkx.is_weakly_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4)])
self.assertFalse(rustworkx.is_weakly_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_weakly_connected.py:56*

### test_is_weakly_connected_true

**Category**: method_call  
**Description**: test is weakly connected true  
**Expected**: self.assertTrue(rustworkx.is_weakly_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 0), (2, 4), (4, 5), (5, 6), (6, 7), (7, 4)])
self.assertTrue(rustworkx.is_weakly_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_weakly_connected.py:63*

### test_hash

**Category**: method_call  
**Description**: test hash  
**Expected**: self.assertEqual(hash_res, hash(res))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.dag = rustworkx.PyDAG()
self.node_a = self.dag.add_node('a')
self.node_b = self.dag.add_child(self.node_a, 'b', 'Edgy')

self.assertIsInstance(hash_res, int)
self.assertEqual(hash_res, hash(res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_custom_return_types.py:81*

### test_hash

**Category**: method_call  
**Description**: test hash  
**Expected**: self.assertEqual(hash_res, hash(res))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.dag = rustworkx.PyDAG()
node_a = self.dag.add_node('a')
self.dag.add_child(node_a, 'b', 'Edgy')

self.assertIsInstance(hash_res, int)
self.assertEqual(hash_res, hash(res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_custom_return_types.py:163*

### test_slices

**Category**: method_call  
**Description**: test slices  
**Expected**: self.assertEqual(nodes[0:-1], [0, 1, 2])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.dag = rustworkx.PyDAG()
node_a = self.dag.add_node('a')
self.dag.add_child(node_a, 'b', 'Edgy')

self.assertEqual([0, 2], slice_return)
self.assertEqual(nodes[0:-1], [0, 1, 2])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_custom_return_types.py:172*

### test_slices_negatives

**Category**: method_call  
**Description**: test slices negatives  
**Expected**: self.assertEqual([], indices[-1:-2])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.dag = rustworkx.PyDAG()
node_a = self.dag.add_node('a')
self.dag.add_child(node_a, 'b', 'Edgy')

self.assertEqual([2, 3], slice_return)
self.assertEqual([], indices[-1:-2])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_custom_return_types.py:184*

### test_hash

**Category**: method_call  
**Description**: test hash  
**Expected**: self.assertEqual(hash_res, hash(res))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.dag = rustworkx.PyDAG()
node_a = self.dag.add_node('a')
self.dag.add_child(node_a, 'b', 'Edgy')

self.assertIsInstance(hash_res, int)
self.assertEqual(hash_res, hash(res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_custom_return_types.py:279*

### test_hash

**Category**: method_call  
**Description**: test hash  
**Expected**: self.assertEqual(hash_res, hash(res))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.dag = rustworkx.PyDiGraph()
node_a = self.dag.add_node('a')
node_b = self.dag.add_child(node_a, 'b', 'Edgy')
self.dag.add_child(node_b, 'c', 'Super Edgy')

self.assertIsInstance(hash_res, int)
self.assertEqual(hash_res, hash(res))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_custom_return_types.py:369*

### test_null_graph

**Category**: method_call  
**Description**: test null graph  
**Expected**: self.assertEqual(0, len(complement_graph.edges()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(0, len(complement_graph.nodes()))
self.assertEqual(0, len(complement_graph.edges()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_complement.py:22*

### test_clique_directed

**Category**: method_call  
**Description**: test clique directed  
**Expected**: self.assertEqual(0, len(complement_graph.edges()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.nodes(), complement_graph.nodes())
self.assertEqual(0, len(complement_graph.edges()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_complement.py:31*

### test_null_graph

**Category**: method_call  
**Description**: test null graph  
**Expected**: self.assertEqual(0, len(complement_graph.edges()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(0, len(complement_graph.nodes()))
self.assertEqual(0, len(complement_graph.edges()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_complement.py:22*

### test_clique_directed

**Category**: method_call  
**Description**: test clique directed  
**Expected**: self.assertEqual(0, len(complement_graph.edges()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.nodes(), complement_graph.nodes())
self.assertEqual(0, len(complement_graph.edges()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_complement.py:31*

### test_undirected_empty

**Category**: method_call  
**Description**: test undirected empty  
**Expected**: self.assertEqual(res, {})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.example_edges = [(0, 2), (0, 3), (0, 5), (1, 4), (1, 6), (1, 7), (2, 3), (3, 5), (2, 5), (5, 6), (4, 6), (4, 7), (6, 7), (5, 8), (6, 8), (6, 9), (8, 9), (0, 10), (1, 10), (1, 11), (10, 11), (12, 13), (13, 15), (14, 15), (12, 14), (8, 19), (11, 16), (11, 17), (12, 18)]
example_core = {}
for i in range(8):
    example_core[i] = 3
for i in range(8, 16):
    example_core[i] = 2
for i in range(16, 20):
    example_core[i] = 1
example_core[20] = 0
self.example_core = example_core

self.assertIsInstance(res, dict)
self.assertEqual(res, {})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_core_number.py:72*

### test_undirected_all_0

**Category**: method_call  
**Description**: test undirected all 0  
**Expected**: self.assertEqual(res, {0: 0, 1: 0, 2: 0, 3: 0})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.example_edges = [(0, 2), (0, 3), (0, 5), (1, 4), (1, 6), (1, 7), (2, 3), (3, 5), (2, 5), (5, 6), (4, 6), (4, 7), (6, 7), (5, 8), (6, 8), (6, 9), (8, 9), (0, 10), (1, 10), (1, 11), (10, 11), (12, 13), (13, 15), (14, 15), (12, 14), (8, 19), (11, 16), (11, 17), (12, 18)]
example_core = {}
for i in range(8):
    example_core[i] = 3
for i in range(8, 16):
    example_core[i] = 2
for i in range(16, 20):
    example_core[i] = 1
example_core[20] = 0
self.example_core = example_core

self.assertIsInstance(res, dict)
self.assertEqual(res, {0: 0, 1: 0, 2: 0, 3: 0})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_core_number.py:79*

### test_undirected_all_3

**Category**: method_call  
**Description**: test undirected all 3  
**Expected**: self.assertEqual(res, {0: 3, 1: 3, 2: 3, 3: 3})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.example_edges = [(0, 2), (0, 3), (0, 5), (1, 4), (1, 6), (1, 7), (2, 3), (3, 5), (2, 5), (5, 6), (4, 6), (4, 7), (6, 7), (5, 8), (6, 8), (6, 9), (8, 9), (0, 10), (1, 10), (1, 11), (10, 11), (12, 13), (13, 15), (14, 15), (12, 14), (8, 19), (11, 16), (11, 17), (12, 18)]
example_core = {}
for i in range(8):
    example_core[i] = 3
for i in range(8, 16):
    example_core[i] = 2
for i in range(16, 20):
    example_core[i] = 1
example_core[20] = 0
self.example_core = example_core

self.assertIsInstance(res, dict)
self.assertEqual(res, {0: 3, 1: 3, 2: 3, 3: 3})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_core_number.py:87*

### test_undirected_paper_example

**Category**: method_call  
**Description**: test undirected paper example  
**Expected**: self.assertEqual(res, self.example_core)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.example_edges = [(0, 2), (0, 3), (0, 5), (1, 4), (1, 6), (1, 7), (2, 3), (3, 5), (2, 5), (5, 6), (4, 6), (4, 7), (6, 7), (5, 8), (6, 8), (6, 9), (8, 9), (0, 10), (1, 10), (1, 11), (10, 11), (12, 13), (13, 15), (14, 15), (12, 14), (8, 19), (11, 16), (11, 17), (12, 18)]
example_core = {}
for i in range(8):
    example_core[i] = 3
for i in range(8, 16):
    example_core[i] = 2
for i in range(16, 20):
    example_core[i] = 1
example_core[20] = 0
self.example_core = example_core

self.assertIsInstance(res, dict)
self.assertEqual(res, self.example_core)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_core_number.py:95*

### test_undirected_empty

**Category**: method_call  
**Description**: test undirected empty  
**Expected**: self.assertEqual(res, {})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(res, dict)
self.assertEqual(res, {})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_core_number.py:72*

### test_undirected_all_0

**Category**: method_call  
**Description**: test undirected all 0  
**Expected**: self.assertEqual(res, {0: 0, 1: 0, 2: 0, 3: 0})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(res, dict)
self.assertEqual(res, {0: 0, 1: 0, 2: 0, 3: 0})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_core_number.py:79*

### test_undirected_all_3

**Category**: method_call  
**Description**: test undirected all 3  
**Expected**: self.assertEqual(res, {0: 3, 1: 3, 2: 3, 3: 3})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(res, dict)
self.assertEqual(res, {0: 3, 1: 3, 2: 3, 3: 3})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_core_number.py:87*

### test_undirected_paper_example

**Category**: method_call  
**Description**: test undirected paper example  
**Expected**: self.assertEqual(res, self.example_core)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(res, dict)
self.assertEqual(res, self.example_core)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_core_number.py:95*

### test_number_connected

**Category**: method_call  
**Description**: test number connected  
**Expected**: self.assertEqual(rustworkx.number_connected_components(graph), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_edge(0, 1, None)
self.assertEqual(rustworkx.number_connected_components(graph), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_connected_components.py:22*

### test_number_connected_direct

**Category**: method_call  
**Description**: test number connected direct  
**Expected**: self.assertEqual(len(rustworkx.weakly_connected_components(graph)), 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_edges_from_no_data([(3, 2), (2, 1), (1, 0)])
self.assertEqual(len(rustworkx.weakly_connected_components(graph)), 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_connected_components.py:28*

### test_number_connected_node_holes

**Category**: method_call  
**Description**: test number connected node holes  
**Expected**: self.assertEqual(rustworkx.number_connected_components(graph), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.remove_node(1)
self.assertEqual(rustworkx.number_connected_components(graph), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_connected_components.py:34*

### test_is_connected_false

**Category**: method_call  
**Description**: test is connected false  
**Expected**: self.assertFalse(rustworkx.is_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4)])
self.assertFalse(rustworkx.is_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_connected_components.py:63*

### test_is_connected_true

**Category**: method_call  
**Description**: test is connected true  
**Expected**: self.assertTrue(rustworkx.is_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 0), (2, 4), (4, 5), (5, 6), (6, 7), (7, 4)])
self.assertTrue(rustworkx.is_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_connected_components.py:70*

### test_number_connected

**Category**: method_call  
**Description**: test number connected  
**Expected**: self.assertEqual(rustworkx.number_connected_components(graph), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_edge(0, 1, None)
self.assertEqual(rustworkx.number_connected_components(graph), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_connected_components.py:22*

### test_number_connected_direct

**Category**: method_call  
**Description**: test number connected direct  
**Expected**: self.assertEqual(len(rustworkx.weakly_connected_components(graph)), 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_edges_from_no_data([(3, 2), (2, 1), (1, 0)])
self.assertEqual(len(rustworkx.weakly_connected_components(graph)), 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_connected_components.py:28*

### test_number_connected_node_holes

**Category**: method_call  
**Description**: test number connected node holes  
**Expected**: self.assertEqual(rustworkx.number_connected_components(graph), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.remove_node(1)
self.assertEqual(rustworkx.number_connected_components(graph), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_connected_components.py:34*

### test_is_connected_false

**Category**: method_call  
**Description**: test is connected false  
**Expected**: self.assertFalse(rustworkx.is_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4)])
self.assertFalse(rustworkx.is_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_connected_components.py:63*

### test_is_connected_true

**Category**: method_call  
**Description**: test is connected true  
**Expected**: self.assertTrue(rustworkx.is_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 0), (2, 4), (4, 5), (5, 6), (6, 7), (7, 4)])
self.assertTrue(rustworkx.is_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_connected_components.py:70*

### test_null_cartesian_null

**Category**: method_call  
**Description**: test null cartesian null  
**Expected**: self.assertEqual(len(graph_product.edge_list()), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph_product.nodes()), 0)
self.assertEqual(len(graph_product.edge_list()), 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_cartesian_product.py:23*

### test_directed_path_2_cartesian_path_2

**Category**: method_call  
**Description**: test directed path 2 cartesian path 2  
**Expected**: self.assertEqual(len(graph_product.edge_list()), 4)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph_product.nodes()), 4)
self.assertEqual(len(graph_product.edge_list()), 4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_cartesian_product.py:31*

### test_directed_path_2_cartesian_path_3

**Category**: method_call  
**Description**: test directed path 2 cartesian path 3  
**Expected**: self.assertEqual(len(graph_product.edge_list()), 7)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph_product.nodes()), 6)
self.assertEqual(len(graph_product.edge_list()), 7)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_cartesian_product.py:39*

### test_null_cartesian_null

**Category**: method_call  
**Description**: test null cartesian null  
**Expected**: self.assertEqual(len(graph_product.edge_list()), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph_product.nodes()), 0)
self.assertEqual(len(graph_product.edge_list()), 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_cartesian_product.py:23*

### test_directed_path_2_cartesian_path_2

**Category**: method_call  
**Description**: test directed path 2 cartesian path 2  
**Expected**: self.assertEqual(len(graph_product.edge_list()), 4)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph_product.nodes()), 4)
self.assertEqual(len(graph_product.edge_list()), 4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_cartesian_product.py:31*

### test_directed_path_2_cartesian_path_3

**Category**: method_call  
**Description**: test directed path 2 cartesian path 3  
**Expected**: self.assertEqual(len(graph_product.edge_list()), 7)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph_product.nodes()), 6)
self.assertEqual(len(graph_product.edge_list()), 7)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_cartesian_product.py:39*

### test_directed_star_graph

**Category**: method_call  
**Description**: test directed star graph  
**Expected**: self.assertEqual(len(graph.edges()), 19)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 19)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_star.py:21*

### test_star_directed_graph_inward

**Category**: method_call  
**Description**: test star directed graph inward  
**Expected**: self.assertEqual(len(graph.edges()), 19)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 19)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_star.py:28*

### test_directed_star_graph_weights

**Category**: method_call  
**Description**: test directed star graph weights  
**Expected**: self.assertEqual([x for x in range(20)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual([x for x in range(20)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_star.py:35*

### test_directed_star_graph_weights

**Category**: method_call  
**Description**: test directed star graph weights  
**Expected**: self.assertEqual(len(graph.edges()), 19)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([x for x in range(20)], graph.nodes())
self.assertEqual(len(graph.edges()), 19)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_star.py:36*

### test_directed_star_graph_bidirectional

**Category**: method_call  
**Description**: test directed star graph bidirectional  
**Expected**: self.assertEqual(graph.in_edges(0), inw[::-1])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.out_edges(0), outw[::-1])
self.assertEqual(graph.in_edges(0), inw[::-1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_star.py:50*

### test_directed_star_graph_bidirectional_inward

**Category**: method_call  
**Description**: test directed star graph bidirectional inward  
**Expected**: self.assertEqual(graph.in_edges(0), inw[::-1])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.out_edges(0), outw[::-1])
self.assertEqual(graph.in_edges(0), inw[::-1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_star.py:62*

### test_directed_star_graph_bidirectional_inward

**Category**: method_call  
**Description**: test directed star graph bidirectional inward  
**Expected**: self.assertEqual(graph.in_edges(0), inw[::-1])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.out_edges(0), outw[::-1])
self.assertEqual(graph.in_edges(0), inw[::-1])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_star.py:72*

### test_star_directed_graph_weights_inward

**Category**: method_call  
**Description**: test star directed graph weights inward  
**Expected**: self.assertEqual([x for x in range(20)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual([x for x in range(20)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_star.py:77*

### test_directed_heavy_hex_graph_1

**Category**: method_call  
**Description**: test directed heavy hex graph 1  
**Expected**: self.assertEqual(graph.edge_list(), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(1, len(graph))
self.assertEqual(graph.edge_list(), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_square.py:22*

### test_heavy_hex_graph_1

**Category**: method_call  
**Description**: test heavy hex graph 1  
**Expected**: self.assertEqual(graph.edge_list(), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(1, len(graph))
self.assertEqual(graph.edge_list(), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_square.py:28*

### test_directed_heavy_square_graph_5

**Category**: method_call  
**Description**: test directed heavy square graph 5  
**Expected**: self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + 2 * d * (d - 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 3 * d * d - 2 * d)
self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + 2 * d * (d - 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_square.py:34*

### test_directed_heavy_square_graph_5_bidirectional

**Category**: method_call  
**Description**: test directed heavy square graph 5 bidirectional  
**Expected**: self.assertEqual(len(graph.edges()), 2 * (2 * d * (d - 1) + 2 * d * (d - 1)))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 3 * d * d - 2 * d)
self.assertEqual(len(graph.edges()), 2 * (2 * d * (d - 1) + 2 * d * (d - 1)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_square.py:123*

### test_heavy_square_graph_5

**Category**: method_call  
**Description**: test heavy square graph 5  
**Expected**: self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + 2 * d * (d - 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 3 * d * d - 2 * d)
self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + 2 * d * (d - 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_square.py:292*

### test_directed_heavy_square_graph_3

**Category**: method_call  
**Description**: test directed heavy square graph 3  
**Expected**: self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + 2 * d * (d - 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 3 * d * d - 2 * d)
self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + 2 * d * (d - 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_square.py:381*

### test_directed_heavy_square_graph_3_bidirectional

**Category**: method_call  
**Description**: test directed heavy square graph 3 bidirectional  
**Expected**: self.assertEqual(len(graph.edges()), 2 * (2 * d * (d - 1) + 2 * d * (d - 1)))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 3 * d * d - 2 * d)
self.assertEqual(len(graph.edges()), 2 * (2 * d * (d - 1) + 2 * d * (d - 1)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_square.py:414*

### test_heavy_square_graph_3

**Category**: method_call  
**Description**: test heavy square graph 3  
**Expected**: self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + 2 * d * (d - 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 3 * d * d - 2 * d)
self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + 2 * d * (d - 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_square.py:471*

### test_directed_heavy_hex_graph_1

**Category**: method_call  
**Description**: test directed heavy hex graph 1  
**Expected**: self.assertEqual(graph.edge_list(), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(1, len(graph))
self.assertEqual(graph.edge_list(), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_square.py:22*

### test_heavy_hex_graph_1

**Category**: method_call  
**Description**: test heavy hex graph 1  
**Expected**: self.assertEqual(graph.edge_list(), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(1, len(graph))
self.assertEqual(graph.edge_list(), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_square.py:28*

### test_noweight_graph

**Category**: method_call  
**Description**: test noweight graph  
**Expected**: self.assertEqual([None, None, None], gprime.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([1, 2, 3], gprime.node_indices())
self.assertEqual([None, None, None], gprime.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_pickle.py:28*

### test_noweight_graph

**Category**: method_call  
**Description**: test noweight graph  
**Expected**: self.assertEqual({1: (1, 2, None), 3: (3, 1, None)}, dict(gprime.edge_index_map()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([None, None, None], gprime.nodes())
self.assertEqual({1: (1, 2, None), 3: (3, 1, None)}, dict(gprime.edge_index_map()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_pickle.py:29*

### test_weight_graph

**Category**: method_call  
**Description**: test weight graph  
**Expected**: self.assertEqual(['B', 'C', 'D'], gprime.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([1, 2, 3], gprime.node_indices())
self.assertEqual(['B', 'C', 'D'], gprime.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_pickle.py:39*

### test_weight_graph

**Category**: method_call  
**Description**: test weight graph  
**Expected**: self.assertEqual({1: (1, 2, 'B -> C'), 3: (3, 1, 'D -> B')}, dict(gprime.edge_index_map()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(['B', 'C', 'D'], gprime.nodes())
self.assertEqual({1: (1, 2, 'B -> C'), 3: (3, 1, 'D -> B')}, dict(gprime.edge_index_map()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_pickle.py:40*

### test_contracted_nodes_pickle

**Category**: method_call  
**Description**: Test pickle/unpickle of graphs with contracted nodes (issue #1503)  
**Expected**: self.assertEqual([2, contracted_idx], g.node_indices())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
g.add_edge(2, contracted_idx, 'C -> AB')
self.assertEqual([2, contracted_idx], g.node_indices())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_pickle.py:52*

### test_contracted_nodes_pickle

**Category**: method_call  
**Description**: Test pickle/unpickle of graphs with contracted nodes (issue #1503)  
**Expected**: self.assertEqual([(2, contracted_idx)], g.edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([2, contracted_idx], g.node_indices())
self.assertEqual([(2, contracted_idx)], g.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_pickle.py:55*

### test_contracted_nodes_pickle

**Category**: method_call  
**Description**: Test pickle/unpickle of graphs with contracted nodes (issue #1503)  
**Expected**: self.assertEqual(g.edge_list(), gprime.edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(g.node_indices(), gprime.node_indices())
self.assertEqual(g.edge_list(), gprime.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_pickle.py:62*

### test_contracted_nodes_pickle

**Category**: method_call  
**Description**: Test pickle/unpickle of graphs with contracted nodes (issue #1503)  
**Expected**: self.assertEqual(g.nodes(), gprime.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(g.edge_list(), gprime.edge_list())
self.assertEqual(g.nodes(), gprime.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_pickle.py:63*

### test_contracted_nodes_with_weights_pickle

**Category**: method_call  
**Description**: Test pickle/unpickle of graphs with contracted nodes and edge weights  
**Expected**: self.assertEqual(g.edge_list(), gprime.edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(g.node_indices(), gprime.node_indices())
self.assertEqual(g.edge_list(), gprime.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_pickle.py:81*

### test_contracted_nodes_with_weights_pickle

**Category**: method_call  
**Description**: Test pickle/unpickle of graphs with contracted nodes and edge weights  
**Expected**: self.assertEqual(g.nodes(), gprime.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(g.edge_list(), gprime.edge_list())
self.assertEqual(g.nodes(), gprime.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_pickle.py:82*

### test_directed_grid_graph_dimensions

**Category**: method_call  
**Description**: test directed grid graph dimensions  
**Expected**: self.assertEqual(len(graph.edges()), 31)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 31)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_grid.py:21*

### test_directed_grid_graph_dimensions

**Category**: method_call  
**Description**: test directed grid graph dimensions  
**Expected**: self.assertEqual(graph.out_edges(0), [(0, 1, None), (0, 5, None)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph.edges()), 31)
self.assertEqual(graph.out_edges(0), [(0, 1, None), (0, 5, None)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_grid.py:22*

### test_directed_grid_graph_dimensions

**Category**: method_call  
**Description**: test directed grid graph dimensions  
**Expected**: self.assertEqual(graph.out_edges(7), [(7, 8, None), (7, 12, None)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.out_edges(0), [(0, 1, None), (0, 5, None)])
self.assertEqual(graph.out_edges(7), [(7, 8, None), (7, 12, None)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_grid.py:23*

### test_directed_grid_graph_dimensions

**Category**: method_call  
**Description**: test directed grid graph dimensions  
**Expected**: self.assertEqual(graph.out_edges(9), [(9, 14, None)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.out_edges(7), [(7, 8, None), (7, 12, None)])
self.assertEqual(graph.out_edges(9), [(9, 14, None)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_grid.py:24*

### test_directed_grid_graph_dimensions

**Category**: method_call  
**Description**: test directed grid graph dimensions  
**Expected**: self.assertEqual(graph.out_edges(17), [(17, 18, None)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.out_edges(9), [(9, 14, None)])
self.assertEqual(graph.out_edges(17), [(17, 18, None)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_grid.py:25*

### test_directed_grid_graph_dimensions

**Category**: method_call  
**Description**: test directed grid graph dimensions  
**Expected**: self.assertEqual(graph.out_edges(19), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.out_edges(17), [(17, 18, None)])
self.assertEqual(graph.out_edges(19), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_grid.py:26*

### test_directed_grid_graph_dimensions

**Category**: method_call  
**Description**: test directed grid graph dimensions  
**Expected**: self.assertEqual(graph.in_edges(0), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.out_edges(19), [])
self.assertEqual(graph.in_edges(0), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_grid.py:27*

### test_directed_grid_graph_dimensions

**Category**: method_call  
**Description**: test directed grid graph dimensions  
**Expected**: self.assertEqual(graph.in_edges(2), [(1, 2, None)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.in_edges(0), [])
self.assertEqual(graph.in_edges(2), [(1, 2, None)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_grid.py:28*

### test_directed_grid_graph_dimensions

**Category**: method_call  
**Description**: test directed grid graph dimensions  
**Expected**: self.assertEqual(graph.in_edges(5), [(0, 5, None)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.in_edges(2), [(1, 2, None)])
self.assertEqual(graph.in_edges(5), [(0, 5, None)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_grid.py:29*

### test_directed_grid_graph_dimensions

**Category**: method_call  
**Description**: test directed grid graph dimensions  
**Expected**: self.assertEqual(graph.in_edges(7), [(6, 7, None), (2, 7, None)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.in_edges(5), [(0, 5, None)])
self.assertEqual(graph.in_edges(7), [(6, 7, None), (2, 7, None)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_grid.py:30*

### test_empty_graph

**Category**: method_call  
**Description**: test empty graph  
**Expected**: self.assertEqual(len(graph.edges()), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_empty.py:21*

### test_empty_directed_graph

**Category**: method_call  
**Description**: test empty directed graph  
**Expected**: self.assertEqual(len(graph.edges()), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_empty.py:26*

### test_empty_directed_graph

**Category**: method_call  
**Description**: test empty directed graph  
**Expected**: self.assertIsInstance(graph, rustworkx.PyDiGraph)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph.edges()), 0)
self.assertIsInstance(graph, rustworkx.PyDiGraph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_empty.py:27*

### test_empty_graph

**Category**: method_call  
**Description**: test empty graph  
**Expected**: self.assertEqual(len(graph.edges()), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_empty.py:21*

### test_empty_directed_graph

**Category**: method_call  
**Description**: test empty directed graph  
**Expected**: self.assertEqual(len(graph.edges()), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_empty.py:26*

### test_empty_directed_graph

**Category**: method_call  
**Description**: test empty directed graph  
**Expected**: self.assertIsInstance(graph, rustworkx.PyDiGraph)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph.edges()), 0)
self.assertIsInstance(graph, rustworkx.PyDiGraph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_empty.py:27*

### test_union_basic_merge_none

**Category**: method_call  
**Description**: test union basic merge none  
**Expected**: self.assertTrue(len(final.edge_list()) == 4)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.add_nodes_from(['a_1', 'a_2', 'a_3'])
self.graph.extend_from_weighted_edge_list([(0, 1, 'e_1'), (1, 2, 'e_2')])

self.assertTrue(len(final.nodes()) == 6)
self.assertTrue(len(final.edge_list()) == 4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_union.py:25*

### test_union_basic_merge_nodes_only

**Category**: method_call  
**Description**: test union basic merge nodes only  
**Expected**: self.assertTrue(len(final.get_all_edge_data(0, 1)) == 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.add_nodes_from(['a_1', 'a_2', 'a_3'])
self.graph.extend_from_weighted_edge_list([(0, 1, 'e_1'), (1, 2, 'e_2')])

self.assertTrue(len(final.edge_list()) == 4)
self.assertTrue(len(final.get_all_edge_data(0, 1)) == 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_union.py:34*

### test_union_basic_merge_nodes_only

**Category**: method_call  
**Description**: test union basic merge nodes only  
**Expected**: self.assertTrue(len(final.nodes()) == 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.add_nodes_from(['a_1', 'a_2', 'a_3'])
self.graph.extend_from_weighted_edge_list([(0, 1, 'e_1'), (1, 2, 'e_2')])

self.assertTrue(len(final.get_all_edge_data(0, 1)) == 2)
self.assertTrue(len(final.nodes()) == 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_union.py:35*

### test_union_basic_merge_none

**Category**: method_call  
**Description**: test union basic merge none  
**Expected**: self.assertTrue(len(final.edge_list()) == 4)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(len(final.nodes()) == 6)
self.assertTrue(len(final.edge_list()) == 4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_union.py:25*

### test_tree

**Category**: method_call  
**Description**: test tree  
**Expected**: self.assertEqual(len(self.graph.nodes()) - 1, len(mst_graph.edge_list()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 3), (self.a, self.d, 2), (self.b, self.c, 4), (self.c, self.d, 1), (self.a, self.f, 1), (self.b, self.f, 6), (self.d, self.e, 5), (self.c, self.e, 7)]
self.graph.add_edges_from(edge_list)
self.expected_edges = [(self.a, self.b, 3), (self.a, self.d, 2), (self.c, self.d, 1), (self.a, self.f, 1), (self.d, self.e, 5)]

self.assertEqual(self.graph.nodes(), mst_graph.nodes())
self.assertEqual(len(self.graph.nodes()) - 1, len(mst_graph.edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_mst.py:61*

### test_tree

**Category**: method_call  
**Description**: test tree  
**Expected**: self.assertEqualEdgeList(self.expected_edges, mst_graph.weighted_edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 3), (self.a, self.d, 2), (self.b, self.c, 4), (self.c, self.d, 1), (self.a, self.f, 1), (self.b, self.f, 6), (self.d, self.e, 5), (self.c, self.e, 7)]
self.graph.add_edges_from(edge_list)
self.expected_edges = [(self.a, self.b, 3), (self.a, self.d, 2), (self.c, self.d, 1), (self.a, self.f, 1), (self.d, self.e, 5)]

self.assertEqual(len(self.graph.nodes()) - 1, len(mst_graph.edge_list()))
self.assertEqualEdgeList(self.expected_edges, mst_graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_mst.py:62*

### test_forest

**Category**: method_call  
**Description**: test forest  
**Expected**: self.assertEqual(len(self.graph.nodes()) - 2, len(msf_graph.edge_list()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 3), (self.a, self.d, 2), (self.b, self.c, 4), (self.c, self.d, 1), (self.a, self.f, 1), (self.b, self.f, 6), (self.d, self.e, 5), (self.c, self.e, 7)]
self.graph.add_edges_from(edge_list)
self.expected_edges = [(self.a, self.b, 3), (self.a, self.d, 2), (self.c, self.d, 1), (self.a, self.f, 1), (self.d, self.e, 5)]

self.assertEqual(self.graph.nodes(), msf_graph.nodes())
self.assertEqual(len(self.graph.nodes()) - 2, len(msf_graph.edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_mst.py:73*

### test_forest

**Category**: method_call  
**Description**: test forest  
**Expected**: self.assertEqualEdgeList(forest_expected_edges, msf_graph.weighted_edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 3), (self.a, self.d, 2), (self.b, self.c, 4), (self.c, self.d, 1), (self.a, self.f, 1), (self.b, self.f, 6), (self.d, self.e, 5), (self.c, self.e, 7)]
self.graph.add_edges_from(edge_list)
self.expected_edges = [(self.a, self.b, 3), (self.a, self.d, 2), (self.c, self.d, 1), (self.a, self.f, 1), (self.d, self.e, 5)]

self.assertEqual(len(self.graph.nodes()) - 2, len(msf_graph.edge_list()))
self.assertEqualEdgeList(forest_expected_edges, msf_graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_mst.py:74*

### test_isolated

**Category**: method_call  
**Description**: test isolated  
**Expected**: self.assertEqual(self.graph.nodes(), msf_graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 3), (self.a, self.d, 2), (self.b, self.c, 4), (self.c, self.d, 1), (self.a, self.f, 1), (self.b, self.f, 6), (self.d, self.e, 5), (self.c, self.e, 7)]
self.graph.add_edges_from(edge_list)
self.expected_edges = [(self.a, self.b, 3), (self.a, self.d, 2), (self.c, self.d, 1), (self.a, self.f, 1), (self.d, self.e, 5)]

self.assertEqual('S', msf_graph.nodes()[s])
self.assertEqual(self.graph.nodes(), msf_graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_mst.py:81*

### test_isolated

**Category**: method_call  
**Description**: test isolated  
**Expected**: self.assertEqual(len(self.graph.nodes()) - 2, len(msf_graph.edge_list()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 3), (self.a, self.d, 2), (self.b, self.c, 4), (self.c, self.d, 1), (self.a, self.f, 1), (self.b, self.f, 6), (self.d, self.e, 5), (self.c, self.e, 7)]
self.graph.add_edges_from(edge_list)
self.expected_edges = [(self.a, self.b, 3), (self.a, self.d, 2), (self.c, self.d, 1), (self.a, self.f, 1), (self.d, self.e, 5)]

self.assertEqual(self.graph.nodes(), msf_graph.nodes())
self.assertEqual(len(self.graph.nodes()) - 2, len(msf_graph.edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_mst.py:82*

### test_isolated

**Category**: method_call  
**Description**: test isolated  
**Expected**: self.assertEqualEdgeList(self.expected_edges, msf_graph.weighted_edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 3), (self.a, self.d, 2), (self.b, self.c, 4), (self.c, self.d, 1), (self.a, self.f, 1), (self.b, self.f, 6), (self.d, self.e, 5), (self.c, self.e, 7)]
self.graph.add_edges_from(edge_list)
self.expected_edges = [(self.a, self.b, 3), (self.a, self.d, 2), (self.c, self.d, 1), (self.a, self.f, 1), (self.d, self.e, 5)]

self.assertEqual(len(self.graph.nodes()) - 2, len(msf_graph.edge_list()))
self.assertEqualEdgeList(self.expected_edges, msf_graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_mst.py:83*

### test_default_weight

**Category**: method_call  
**Description**: test default weight  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(weightless_graph, mst_graph_weight_2))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 3), (self.a, self.d, 2), (self.b, self.c, 4), (self.c, self.d, 1), (self.a, self.f, 1), (self.b, self.f, 6), (self.d, self.e, 5), (self.c, self.e, 7)]
self.graph.add_edges_from(edge_list)
self.expected_edges = [(self.a, self.b, 3), (self.a, self.d, 2), (self.c, self.d, 1), (self.a, self.f, 1), (self.d, self.e, 5)]

self.assertTrue(rustworkx.is_isomorphic(weightless_graph, mst_graph_default_weight))
self.assertTrue(rustworkx.is_isomorphic(weightless_graph, mst_graph_weight_2))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_mst.py:104*

### test_deepcopy_with_holes

**Category**: method_call  
**Description**: test deepcopy with holes  
**Expected**: self.assertEqual([node_a, node_c], dag_b.node_indexes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(dag_b, rustworkx.PyDAG)
self.assertEqual([node_a, node_c], dag_b.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_deepcopy.py:37*

### test_deepcopy_check_cycle

**Category**: method_call  
**Description**: test deepcopy check cycle  
**Expected**: self.assertFalse(graph_d.check_cycle)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph_b.check_cycle)
self.assertFalse(graph_d.check_cycle)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_deepcopy.py:55*

### test_deepcopy_different_objects

**Category**: method_call  
**Description**: test deepcopy different objects  
**Expected**: self.assertIsNot(graph_a.attrs, graph_b.attrs)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph_a.attrs, graph_b.attrs)
self.assertIsNot(graph_a.attrs, graph_b.attrs)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_deepcopy.py:63*

### test_deepcopy_different_objects

**Category**: method_call  
**Description**: test deepcopy different objects  
**Expected**: self.assertEqual(graph_a[node_a], graph_b[node_a])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsNot(graph_a.attrs, graph_b.attrs)
self.assertEqual(graph_a[node_a], graph_b[node_a])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_deepcopy.py:64*

### test_number_strongly_connected_all_strong

**Category**: method_call  
**Description**: test number strongly connected all strong  
**Expected**: self.assertEqual(rustworkx.number_strongly_connected_components(G), 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
G.add_child(node_b, 3, {})
self.assertEqual(rustworkx.number_strongly_connected_components(G), 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_strongly_connected.py:23*

### test_number_strongly_connected

**Category**: method_call  
**Description**: test number strongly connected  
**Expected**: self.assertEqual(rustworkx.number_strongly_connected_components(G), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
G.add_node(3)
self.assertEqual(rustworkx.number_strongly_connected_components(G), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_strongly_connected.py:31*

### test_is_strongly_connected_false

**Category**: method_call  
**Description**: test is strongly connected false  
**Expected**: self.assertFalse(rustworkx.is_strongly_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 0), (2, 4), (4, 5), (5, 6), (6, 7), (7, 4)])
self.assertFalse(rustworkx.is_strongly_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_strongly_connected.py:66*

### test_is_strongly_connected_true

**Category**: method_call  
**Description**: test is strongly connected true  
**Expected**: self.assertTrue(rustworkx.is_strongly_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 0), (2, 4), (4, 2), (4, 5), (5, 6), (6, 7), (7, 4)])
self.assertTrue(rustworkx.is_strongly_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_strongly_connected.py:83*

### test_condensation

**Category**: method_call  
**Description**: test condensation  
**Expected**: self.assertEqual(len(condensed_graph.edge_indices()), 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.node_a = self.graph.add_node('a')
self.node_b = self.graph.add_node('b')
self.node_c = self.graph.add_node('c')
self.node_d = self.graph.add_node('d')
self.node_e = self.graph.add_node('e')
self.node_f = self.graph.add_node('f')
self.node_g = self.graph.add_node('g')
self.node_h = self.graph.add_node('h')
self.graph.add_edge(self.node_a, self.node_b, 'a->b')
self.graph.add_edge(self.node_b, self.node_c, 'b->c')
self.graph.add_edge(self.node_c, self.node_d, 'c->d')
self.graph.add_edge(self.node_d, self.node_a, 'd->a')
self.graph.add_edge(self.node_b, self.node_e, 'b->e')
self.graph.add_edge(self.node_e, self.node_f, 'e->f')
self.graph.add_edge(self.node_f, self.node_g, 'f->g')
self.graph.add_edge(self.node_g, self.node_h, 'g->h')
self.graph.add_edge(self.node_h, self.node_e, 'h->e')

self.assertEqual(len(condensed_graph.node_indices()), 2)
self.assertEqual(len(condensed_graph.edge_indices()), 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_strongly_connected.py:136*

### test_condensation

**Category**: method_call  
**Description**: test condensation  
**Expected**: self.assertTrue(set(scc1) == {'e', 'f', 'g', 'h'} or set(scc2) == {'e', 'f', 'g', 'h'})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.node_a = self.graph.add_node('a')
self.node_b = self.graph.add_node('b')
self.node_c = self.graph.add_node('c')
self.node_d = self.graph.add_node('d')
self.node_e = self.graph.add_node('e')
self.node_f = self.graph.add_node('f')
self.node_g = self.graph.add_node('g')
self.node_h = self.graph.add_node('h')
self.graph.add_edge(self.node_a, self.node_b, 'a->b')
self.graph.add_edge(self.node_b, self.node_c, 'b->c')
self.graph.add_edge(self.node_c, self.node_d, 'c->d')
self.graph.add_edge(self.node_d, self.node_a, 'd->a')
self.graph.add_edge(self.node_b, self.node_e, 'b->e')
self.graph.add_edge(self.node_e, self.node_f, 'e->f')
self.graph.add_edge(self.node_f, self.node_g, 'f->g')
self.graph.add_edge(self.node_g, self.node_h, 'g->h')
self.graph.add_edge(self.node_h, self.node_e, 'h->e')

self.assertTrue(set(scc1) == {'a', 'b', 'c', 'd'} or set(scc2) == {'a', 'b', 'c', 'd'})
self.assertTrue(set(scc1) == {'e', 'f', 'g', 'h'} or set(scc2) == {'e', 'f', 'g', 'h'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_strongly_connected.py:149*

### test_digraph_to_dot_to_file

**Category**: method_call  
**Description**: test digraph to dot to file  
**Expected**: self.assertIsNone(res)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

self.addCleanup(os.remove, self.path)
self.assertIsNone(res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dot.py:51*

### test_digraph_to_dot_to_file

**Category**: method_call  
**Description**: test digraph to dot to file  
**Expected**: self.assertIsNone(res)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.addCleanup(os.remove, self.path)
self.assertIsNone(res)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dot.py:51*

### test_directed_heavy_hex_graph_1

**Category**: method_call  
**Description**: test directed heavy hex graph 1  
**Expected**: self.assertEqual(graph.edge_list(), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(1, len(graph))
self.assertEqual(graph.edge_list(), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_hex.py:22*

### test_heavy_hex_graph_1

**Category**: method_call  
**Description**: test heavy hex graph 1  
**Expected**: self.assertEqual(graph.edge_list(), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(1, len(graph))
self.assertEqual(graph.edge_list(), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_hex.py:28*

### test_directed_heavy_hex_graph_3

**Category**: method_call  
**Description**: test directed heavy hex graph 3  
**Expected**: self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + (d + 1) * (d - 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), (5 * d * d - 2 * d - 1) / 2)
self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + (d + 1) * (d - 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_hex.py:34*

### test_directed_heavy_hex_graph_3_bidirectional

**Category**: method_call  
**Description**: test directed heavy hex graph 3 bidirectional  
**Expected**: self.assertEqual(len(graph.edges()), 2 * (2 * d * (d - 1) + (d + 1) * (d - 1)))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), (5 * d * d - 2 * d - 1) / 2)
self.assertEqual(len(graph.edges()), 2 * (2 * d * (d - 1) + (d + 1) * (d - 1)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_hex.py:63*

### test_heavy_hex_graph_3

**Category**: method_call  
**Description**: test heavy hex graph 3  
**Expected**: self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + (d + 1) * (d - 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), (5 * d * d - 2 * d - 1) / 2)
self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + (d + 1) * (d - 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_hex.py:112*

### test_directed_heavy_hex_graph_5

**Category**: method_call  
**Description**: test directed heavy hex graph 5  
**Expected**: self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + (d + 1) * (d - 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), (5 * d * d - 2 * d - 1) / 2)
self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + (d + 1) * (d - 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_hex.py:141*

### test_directed_heavy_hex_graph_5_bidirectional

**Category**: method_call  
**Description**: test directed heavy hex graph 5 bidirectional  
**Expected**: self.assertEqual(len(graph.edges()), 2 * (2 * d * (d - 1) + (d + 1) * (d - 1)))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), (5 * d * d - 2 * d - 1) / 2)
self.assertEqual(len(graph.edges()), 2 * (2 * d * (d - 1) + (d + 1) * (d - 1)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_hex.py:214*

### test_heavy_hex_graph_5

**Category**: method_call  
**Description**: test heavy hex graph 5  
**Expected**: self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + (d + 1) * (d - 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), (5 * d * d - 2 * d - 1) / 2)
self.assertEqual(len(graph.edges()), 2 * d * (d - 1) + (d + 1) * (d - 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_hex.py:351*

### test_directed_heavy_hex_graph_1

**Category**: method_call  
**Description**: test directed heavy hex graph 1  
**Expected**: self.assertEqual(graph.edge_list(), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(1, len(graph))
self.assertEqual(graph.edge_list(), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_hex.py:22*

### test_heavy_hex_graph_1

**Category**: method_call  
**Description**: test heavy hex graph 1  
**Expected**: self.assertEqual(graph.edge_list(), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(1, len(graph))
self.assertEqual(graph.edge_list(), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_heavy_hex.py:28*

### test_write_to_string

**Category**: method_call  
**Description**: Write a PyGraph to a Matrix Market string.  
**Expected**: self.assertIn('matrix', mm_str)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(mm_str, str)
self.assertIn('matrix', mm_str)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matrix_market.py:17*

### test_write_to_string

**Category**: method_call  
**Description**: Write a PyGraph to a Matrix Market string.  
**Expected**: self.assertIn('3 3 4', mm_str)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('matrix', mm_str)
self.assertIn('3 3 4', mm_str)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matrix_market.py:18*

### test_write_to_file

**Category**: method_call  
**Description**: Write PyGraph data to a Matrix Market file.  
**Expected**: self.assertIn('3 3 4', content)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('matrix', content)
self.assertIn('3 3 4', content)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matrix_market.py:34*

### test_read_from_file

**Category**: method_call  
**Description**: Read a Matrix Market file into a PyGraph.  
**Expected**: self.assertEqual(len(g.nodes()), 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(g, rustworkx.PyGraph)
self.assertEqual(len(g.nodes()), 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matrix_market.py:53*

### test_read_from_file

**Category**: method_call  
**Description**: Read a Matrix Market file into a PyGraph.  
**Expected**: self.assertEqual(len(g.edges()), 5)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(g.nodes()), 3)
self.assertEqual(len(g.edges()), 5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matrix_market.py:54*

### test_read_from_string

**Category**: method_call  
**Description**: Read Matrix Market data directly from a string.  
**Expected**: self.assertEqual(len(g.nodes()), 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(g, rustworkx.PyGraph)
self.assertEqual(len(g.nodes()), 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matrix_market.py:67*

### test_read_from_string

**Category**: method_call  
**Description**: Read Matrix Market data directly from a string.  
**Expected**: self.assertEqual(len(g.edges()), 5)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(g.nodes()), 3)
self.assertEqual(len(g.edges()), 5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matrix_market.py:68*

### test_roundtrip_in_memory

**Category**: method_call  
**Description**: Roundtrip: write → read should reconstruct same graph.  
**Expected**: self.assertEqual(len(g2.edges()), 4)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(g2.nodes()), len(g.nodes()))
self.assertEqual(len(g2.edges()), 4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matrix_market.py:81*

### test_roundtrip_via_file

**Category**: method_call  
**Description**: Roundtrip through file should preserve structure.  
**Expected**: self.assertEqual(len(g2.edges()), 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(g2.nodes()), 2)
self.assertEqual(len(g2.edges()), 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matrix_market.py:95*

### test_write_to_string

**Category**: method_call  
**Description**: Write a PyGraph to a Matrix Market string.  
**Expected**: self.assertIn('matrix', mm_str)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(mm_str, str)
self.assertIn('matrix', mm_str)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matrix_market.py:17*

### test_floyd_warshall_numpy_three_edges

**Category**: method_call  
**Description**: test floyd warshall numpy three edges  
**Expected**: self.assertEqual(dist[3, 0], 15)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dist[0, 3], 15)
self.assertEqual(dist[3, 0], 15)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_floyd_warshall.py:108*

### test_weighted_numpy_two_edges

**Category**: method_call  
**Description**: test weighted numpy two edges  
**Expected**: self.assertEqual(dist[2, 0], 4)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dist[0, 2], 4)
self.assertEqual(dist[2, 0], 4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_floyd_warshall.py:129*

### test_floyd_warshall_numpy_cycle

**Category**: method_call  
**Description**: test floyd warshall numpy cycle  
**Expected**: self.assertEqual(dist[0, 4], 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dist[0, 3], 3)
self.assertEqual(dist[0, 4], 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_floyd_warshall.py:155*

### test_numpy_no_edges

**Category**: method_call  
**Description**: test numpy no edges  
**Expected**: self.assertTrue(numpy.array_equal(dist, expected))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
numpy.fill_diagonal(expected, 0)
self.assertTrue(numpy.array_equal(dist, expected))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_floyd_warshall.py:165*

### test_floyd_warshall_numpy_graph_cycle_with_removals

**Category**: method_call  
**Description**: test floyd warshall numpy graph cycle with removals  
**Expected**: self.assertEqual(dist[0, 4], 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dist[0, 3], 3)
self.assertEqual(dist[0, 4], 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_floyd_warshall.py:176*

### test_floyd_warshall_numpy_graph_cycle_no_weight_fn

**Category**: method_call  
**Description**: test floyd warshall numpy graph cycle no weight fn  
**Expected**: self.assertEqual(dist[0, 4], 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(dist[0, 3], 3)
self.assertEqual(dist[0, 4], 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_floyd_warshall.py:185*

### test_simple_example_digraph

**Category**: method_call  
**Description**: test simple example digraph  
**Expected**: self.assertTrue(graph.has_edge(0, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.node_indexes(), [0, 1, 2])
self.assertTrue(graph.has_edge(0, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edgelist.py:37*

### test_simple_example_digraph

**Category**: method_call  
**Description**: test simple example digraph  
**Expected**: self.assertTrue(graph.has_edge(1, 2))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.has_edge(0, 1))
self.assertTrue(graph.has_edge(1, 2))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edgelist.py:38*

### test_simple_example_digraph

**Category**: method_call  
**Description**: test simple example digraph  
**Expected**: self.assertFalse(graph.has_edge(1, 0))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.has_edge(1, 2))
self.assertFalse(graph.has_edge(1, 0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edgelist.py:39*

### test_simple_example_digraph

**Category**: method_call  
**Description**: test simple example digraph  
**Expected**: self.assertFalse(graph.has_edge(2, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertFalse(graph.has_edge(1, 0))
self.assertFalse(graph.has_edge(2, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edgelist.py:40*

### test_simple_example_digraph

**Category**: method_call  
**Description**: test simple example digraph  
**Expected**: self.assertFalse(graph.has_edge(0, 2))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertFalse(graph.has_edge(2, 1))
self.assertFalse(graph.has_edge(0, 2))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edgelist.py:41*

### test_blank_line_digraph

**Category**: method_call  
**Description**: test blank line digraph  
**Expected**: self.assertTrue(graph.has_edge(0, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.node_indexes(), [0, 1, 2])
self.assertTrue(graph.has_edge(0, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edgelist.py:51*

### test_blank_line_digraph

**Category**: method_call  
**Description**: test blank line digraph  
**Expected**: self.assertTrue(graph.has_edge(1, 2))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.has_edge(0, 1))
self.assertTrue(graph.has_edge(1, 2))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edgelist.py:52*

### test_blank_line_digraph

**Category**: method_call  
**Description**: test blank line digraph  
**Expected**: self.assertFalse(graph.has_edge(1, 0))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(graph.has_edge(1, 2))
self.assertFalse(graph.has_edge(1, 0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_edgelist.py:53*

### test_all_simple_path_no_path

**Category**: method_call  
**Description**: test all simple path no path  
**Expected**: self.assertEqual([], rustworkx.digraph_all_simple_paths(dag, 0, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 5), (5, 2), (5, 3)]

dag.add_node(1)
self.assertEqual([], rustworkx.digraph_all_simple_paths(dag, 0, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_all_simple_paths.py:118*

### test_graph_digraph_all_simple_paths

**Category**: method_call  
**Description**: test graph digraph all simple paths  
**Expected**: self.assertRaises(TypeError, rustworkx.digraph_all_simple_paths, (dag, 0, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 5), (5, 2), (5, 3)]

dag.add_node(1)
self.assertRaises(TypeError, rustworkx.digraph_all_simple_paths, (dag, 0, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_all_simple_paths.py:131*

### test_all_simple_path_no_path

**Category**: method_call  
**Description**: test all simple path no path  
**Expected**: self.assertEqual({0: {}, 1: {}}, rustworkx.all_pairs_all_simple_paths(dag))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 5), (5, 2), (5, 3)]

dag.add_node(1)
self.assertEqual({0: {}, 1: {}}, rustworkx.all_pairs_all_simple_paths(dag))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_all_simple_paths.py:361*

### test_all_simple_path_no_path

**Category**: method_call  
**Description**: test all simple path no path  
**Expected**: self.assertEqual([], rustworkx.digraph_all_simple_paths(dag, 0, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
dag.add_node(1)
self.assertEqual([], rustworkx.digraph_all_simple_paths(dag, 0, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_all_simple_paths.py:118*

### test_graph_digraph_all_simple_paths

**Category**: method_call  
**Description**: test graph digraph all simple paths  
**Expected**: self.assertRaises(TypeError, rustworkx.digraph_all_simple_paths, (dag, 0, 1))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
dag.add_node(1)
self.assertRaises(TypeError, rustworkx.digraph_all_simple_paths, (dag, 0, 1))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_all_simple_paths.py:131*

### test_all_simple_path_no_path

**Category**: method_call  
**Description**: test all simple path no path  
**Expected**: self.assertEqual({0: {}, 1: {}}, rustworkx.all_pairs_all_simple_paths(dag))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
dag.add_node(1)
self.assertEqual({0: {}, 1: {}}, rustworkx.all_pairs_all_simple_paths(dag))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_all_simple_paths.py:361*

### test_correct_successful_path

**Category**: method_call  
**Description**: test correct successful path  
**Expected**: self.assertAlmostEqual(dist, total_length(path))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(path, [0, 1, 2, 3])
self.assertAlmostEqual(dist, total_length(path))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_geometry.py:118*

### test_correct_successful_path

**Category**: method_call  
**Description**: test correct successful path  
**Expected**: self.assertAlmostEqual(dist, total_length(path))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(path, [0, 1, 2, 5, 6])
self.assertAlmostEqual(dist, total_length(path))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_geometry.py:122*

### test_correct_successful_path

**Category**: method_call  
**Description**: test correct successful path  
**Expected**: self.assertAlmostEqual(dist, total_length(path))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(path, [0, 1, 2, 3])
self.assertAlmostEqual(dist, total_length(path))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_geometry.py:118*

### test_correct_successful_path

**Category**: method_call  
**Description**: test correct successful path  
**Expected**: self.assertAlmostEqual(dist, total_length(path))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(path, [0, 1, 2, 5, 6])
self.assertAlmostEqual(dist, total_length(path))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_geometry.py:122*

### test_digraph_dijkstra_tree_edges

**Category**: method_call  
**Description**: test digraph dijkstra tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

rustworkx.digraph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra_search.py:50*

### test_digraph_dijkstra_tree_edges_no_starting_point

**Category**: method_call  
**Description**: test digraph dijkstra tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3), (4, 7)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

rustworkx.digraph_dijkstra_search(self.graph, None, float, vis)
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra_search.py:69*

### test_digraph_dijkstra_goal_search_with_stop_search_exception

**Category**: method_call  
**Description**: test digraph dijkstra goal search with stop search exception  
**Expected**: self.assertEqual(vis.reconstruct_path(), [0, 2, 5, 3])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

rustworkx.digraph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.reconstruct_path(), [0, 2, 5, 3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra_search.py:100*

### test_digraph_dijkstra_goal_search_with_stop_search_exception

**Category**: method_call  
**Description**: test digraph dijkstra goal search with stop search exception  
**Expected**: self.assertEqual(vis.opt_goal_cost, 4.0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.extend_from_weighted_edge_list([(0, 1, 1), (0, 2, 2), (1, 3, 10), (2, 1, 1), (2, 5, 1), (2, 6, 1), (5, 3, 1), (4, 7, 1)])

self.assertEqual(vis.reconstruct_path(), [0, 2, 5, 3])
self.assertEqual(vis.opt_goal_cost, 4.0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dijkstra_search.py:101*

### test_simple_dag_composition

**Category**: method_call  
**Description**: test simple dag composition  
**Expected**: self.assertEqual([0, 1, 2, 3, 4], rustworkx.topological_sort(dag))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual({0: 3, 1: 4}, res)
self.assertEqual([0, 1, 2, 3, 4], rustworkx.topological_sort(dag))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_compose.py:29*

### test_edge_map_and_node_map_funcs_digraph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs digraph compose  
**Expected**: self.assertEqual(digraph[res[other_output_nodes[0]]], 'qr[0]')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual({2: 4, 3: 3, 4: 5}, res)
self.assertEqual(digraph[res[other_output_nodes[0]]], 'qr[0]')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_compose.py:78*

### test_edge_map_and_node_map_funcs_digraph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs digraph compose  
**Expected**: self.assertEqual(digraph[res[other_output_nodes[1]]], 'qr[1]')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph[res[other_output_nodes[0]]], 'qr[0]')
self.assertEqual(digraph[res[other_output_nodes[1]]], 'qr[1]')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_compose.py:79*

### test_edge_map_and_node_map_funcs_digraph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs digraph compose  
**Expected**: self.assertTrue(digraph.has_edge(0, 2))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph[res[other_output_nodes[1]]], 'qr[1]')
self.assertTrue(digraph.has_edge(0, 2))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_compose.py:80*

### test_edge_map_and_node_map_funcs_digraph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs digraph compose  
**Expected**: self.assertTrue(digraph.get_all_edge_data(0, 2), ['qr[0]'])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(digraph.has_edge(0, 2))
self.assertTrue(digraph.get_all_edge_data(0, 2), ['qr[0]'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_compose.py:82*

### test_edge_map_and_node_map_funcs_digraph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs digraph compose  
**Expected**: self.assertTrue(digraph.has_edge(1, 4))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(digraph.get_all_edge_data(0, 2), ['qr[0]'])
self.assertTrue(digraph.has_edge(1, 4))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_compose.py:83*

### test_edge_map_and_node_map_funcs_digraph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs digraph compose  
**Expected**: self.assertTrue(digraph.get_all_edge_data(1, 4), ['qr[1]'])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(digraph.has_edge(1, 4))
self.assertTrue(digraph.get_all_edge_data(1, 4), ['qr[1]'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_compose.py:85*

### test_edge_map_and_node_map_funcs_digraph_compose

**Category**: method_call  
**Description**: test edge map and node map funcs digraph compose  
**Expected**: self.assertTrue(digraph.has_edge(2, 4))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(digraph.get_all_edge_data(1, 4), ['qr[1]'])
self.assertTrue(digraph.has_edge(2, 4))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_compose.py:86*

### test_directed_mesh_graph

**Category**: method_call  
**Description**: test directed mesh graph  
**Expected**: self.assertEqual(len(graph.edges()), 380)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 380)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_mesh.py:21*

### test_directed_mesh_graph_weights

**Category**: method_call  
**Description**: test directed mesh graph weights  
**Expected**: self.assertEqual([x for x in range(20)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual([x for x in range(20)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_mesh.py:32*

### test_directed_mesh_graph_weights

**Category**: method_call  
**Description**: test directed mesh graph weights  
**Expected**: self.assertEqual(len(graph.edges()), 380)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([x for x in range(20)], graph.nodes())
self.assertEqual(len(graph.edges()), 380)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_mesh.py:33*

### test_mesh_graph

**Category**: method_call  
**Description**: test mesh graph  
**Expected**: self.assertEqual(len(graph.edges()), 190)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 190)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_mesh.py:48*

### test_mesh_graph_weights

**Category**: method_call  
**Description**: test mesh graph weights  
**Expected**: self.assertEqual([x for x in range(20)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual([x for x in range(20)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_mesh.py:53*

### test_mesh_graph_weights

**Category**: method_call  
**Description**: test mesh graph weights  
**Expected**: self.assertEqual(len(graph.edges()), 190)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([x for x in range(20)], graph.nodes())
self.assertEqual(len(graph.edges()), 190)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_mesh.py:54*

### test_directed_mesh_graph

**Category**: method_call  
**Description**: test directed mesh graph  
**Expected**: self.assertEqual(len(graph.edges()), 380)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 380)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_mesh.py:21*

### test_directed_mesh_graph_weights

**Category**: method_call  
**Description**: test directed mesh graph weights  
**Expected**: self.assertEqual([x for x in range(20)], graph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual([x for x in range(20)], graph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_mesh.py:32*

### test_directed_mesh_graph_weights

**Category**: method_call  
**Description**: test directed mesh graph weights  
**Expected**: self.assertEqual(len(graph.edges()), 380)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([x for x in range(20)], graph.nodes())
self.assertEqual(len(graph.edges()), 380)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_mesh.py:33*

### test_mesh_graph

**Category**: method_call  
**Description**: test mesh graph  
**Expected**: self.assertEqual(len(graph.edges()), 190)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 20)
self.assertEqual(len(graph.edges()), 190)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_mesh.py:48*

### test_filter_nodes

**Category**: method_call  
**Description**: test filter nodes  
**Expected**: self.assertEqual(list(lizard_indices), [3])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(cat_indices), [0, 1, 4])
self.assertEqual(list(lizard_indices), [3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_filter.py:38*

### test_filter_nodes

**Category**: method_call  
**Description**: test filter nodes  
**Expected**: self.assertEqual(list(human_indices), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(lizard_indices), [3])
self.assertEqual(list(human_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_filter.py:39*

### test_filter_edges

**Category**: method_call  
**Description**: test filter edges  
**Expected**: self.assertEqual(list(enemies_indices), [2])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(friends_indices), [0, 1])
self.assertEqual(list(enemies_indices), [2])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_filter.py:64*

### test_filter_edges

**Category**: method_call  
**Description**: test filter edges  
**Expected**: self.assertEqual(list(frenemies_indices), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(enemies_indices), [2])
self.assertEqual(list(frenemies_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_filter.py:65*

### test_filter_nodes

**Category**: method_call  
**Description**: test filter nodes  
**Expected**: self.assertEqual(list(lizard_indices), [3])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(cat_indices), [0, 1, 4])
self.assertEqual(list(lizard_indices), [3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_filter.py:38*

### test_filter_nodes

**Category**: method_call  
**Description**: test filter nodes  
**Expected**: self.assertEqual(list(human_indices), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(list(lizard_indices), [3])
self.assertEqual(list(human_indices), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_filter.py:39*

### test_clear

**Category**: method_call  
**Description**: test clear  
**Expected**: self.assertEqual(graph.num_nodes(), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.clear()
self.assertEqual(graph.num_nodes(), 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_clear.py:26*

### test_clear

**Category**: method_call  
**Description**: test clear  
**Expected**: self.assertEqual(graph.num_edges(), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph.num_nodes(), 0)
self.assertEqual(graph.num_edges(), 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_clear.py:27*

### test_copy_with_holes_returns_graph

**Category**: method_call  
**Description**: test copy with holes returns graph  
**Expected**: self.assertEqual([node_a, node_c], graph_b.node_indexes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(graph_b, rustworkx.PyGraph)
self.assertEqual([node_a, node_c], graph_b.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_copy.py:38*

### test_copy_shared_ref

**Category**: method_call  
**Description**: test copy shared ref  
**Expected**: self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph_b[0]['a'], 42)
self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_copy.py:54*

### test_copy_with_holes_returns_graph

**Category**: method_call  
**Description**: test copy with holes returns graph  
**Expected**: self.assertEqual([node_a, node_c], graph_b.node_indexes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(graph_b, rustworkx.PyGraph)
self.assertEqual([node_a, node_c], graph_b.node_indexes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_copy.py:38*

### test_copy_shared_ref

**Category**: method_call  
**Description**: test copy shared ref  
**Expected**: self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph_b[0]['a'], 42)
self.assertEqual(graph_a.get_edge_data(0, 1), {'edge': 162})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_copy.py:54*

### test_empty_nodes

**Category**: method_call  
**Description**: Replacing empty nodes is functionally equivalent to add_node.  
**Expected**: self.assertEqual(set(dag.nodes()), {'m'})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
dag.contract_nodes([], 'm')
self.assertEqual(set(dag.nodes()), {'m'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_contract_nodes.py:43*

### test_unknown_nodes

**Category**: method_call  
**Description**: Replacing all unknown nodes is functionally equivalent to add_node,
since unknown nodes should be ignored.  
**Expected**: self.assertEqual(set(dag.nodes()), {'m'})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
dag.contract_nodes([0, 1, 2], 'm')
self.assertEqual(set(dag.nodes()), {'m'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_contract_nodes.py:53*

### test_cycle_path_len_gt_1

**Category**: method_call  
**Description**:     ┌─┐              ┌─┐
 ┌4─┤a├─1┐           │m├──1───┐
 │  └─┘  │           └┬┘      │
┌┴┐     ┌┴┐           │      ┌┴┐
│d│     │b│   ───►    │      │b│
└┬┘     └┬┘           │      └┬┘
 │  ┌─┐  2            │  ┌─┐  2
 └3─┤c├──┘            └3─┤c├──┘
    └─┘                  └─┘  
**Expected**: self.assertEqual({UndirectedEdge((node_b, node_c)), UndirectedEdge((node_c, node_m)), UndirectedEdge((node_b, node_m))}, set((UndirectedEdge(e) for e in dag.edge_list())))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([node_b, node_c, node_m], dag.node_indexes())
self.assertEqual({UndirectedEdge((node_b, node_c)), UndirectedEdge((node_c, node_m)), UndirectedEdge((node_b, node_m))}, set((UndirectedEdge(e) for e in dag.edge_list())))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_contract_nodes.py:82*

### test_multiple_paths_would_cycle

**Category**: method_call  
**Description**:     ┌─┐     ┌─┐                  ┌─┐     ┌─┐
 ┌3─┤c│     │e├─5┐            ┌──┤c│     │e├──┐
 │  └┬┘     └┬┘  │            │  └┬┘     └┬┘  │
┌┴┐  2  ┌─┐  4  ┌┴┐           │   2  ┌─┐  4   │
│d│  └──┤b├──┘  │f│   ───►    │   └──┤b├──┘   │
└─┘     └┬┘     └─┘           3      └┬┘      5
         1                    │       1       │
        ┌┴┐                   │      ┌┴┐      │
        │a│                   └──────┤m├──────┘
        └─┘                          └─┘  
**Expected**: self.assertEqual({UndirectedEdge((node_b, node_c)), UndirectedEdge((node_c, node_m)), UndirectedEdge((node_e, node_m)), UndirectedEdge((node_b, node_e)), UndirectedEdge((node_b, node_m))}, set((UndirectedEdge(e) for e in dag.edge_list())))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([node_b, node_c, node_e, node_m], list(dag.node_indexes()))
self.assertEqual({UndirectedEdge((node_b, node_c)), UndirectedEdge((node_c, node_m)), UndirectedEdge((node_e, node_m)), UndirectedEdge((node_b, node_e)), UndirectedEdge((node_b, node_m))}, set((UndirectedEdge(e) for e in dag.edge_list())))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_contract_nodes.py:121*

### test_barbell_graph_count

**Category**: method_call  
**Description**: test barbell graph count  
**Expected**: self.assertEqual(len(graph.edges()), 276)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 37)
self.assertEqual(len(graph.edges()), 276)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_barbell.py:21*

### test_barbell_graph_no_path_num

**Category**: method_call  
**Description**: test barbell graph no path num  
**Expected**: self.assertEqual(set(graph.edge_list()), set(mesh.edge_list()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
mesh.compose(mesh.copy(), {3: (0, None)})
self.assertEqual(set(graph.edge_list()), set(mesh.edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_barbell.py:52*

### test_barbell_graph_count

**Category**: method_call  
**Description**: test barbell graph count  
**Expected**: self.assertEqual(len(graph.edges()), 276)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(graph), 37)
self.assertEqual(len(graph.edges()), 276)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_barbell.py:21*

### test_barbell_graph_no_path_num

**Category**: method_call  
**Description**: test barbell graph no path num  
**Expected**: self.assertEqual(set(graph.edge_list()), set(mesh.edge_list()))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
mesh.compose(mesh.copy(), {3: (0, None)})
self.assertEqual(set(graph.edge_list()), set(mesh.edge_list()))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_barbell.py:52*

### test_is_semi_connected_simple

**Category**: method_call  
**Description**: test is semi connected simple  
**Expected**: self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_edge(1, 2, None)
self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_is_semi_connected.py:33*

### test_is_semi_connected_false

**Category**: method_call  
**Description**: test is semi connected false  
**Expected**: self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_edge(2, 1, None)
self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_is_semi_connected.py:41*

### test_is_semi_connected_single_node

**Category**: method_call  
**Description**: test is semi connected single node  
**Expected**: self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_node(0)
self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_is_semi_connected.py:47*

### test_is_semi_connected_disconnected_graph

**Category**: method_call  
**Description**: test is semi connected disconnected graph  
**Expected**: self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_node(1)
self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_is_semi_connected.py:58*

### test_is_semi_connected_with_node_gaps

**Category**: method_call  
**Description**: test is semi connected with node gaps  
**Expected**: self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_edge(3, 4, None)
self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_is_semi_connected.py:85*

### test_is_semi_connected_simple

**Category**: method_call  
**Description**: test is semi connected simple  
**Expected**: self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_edge(1, 2, None)
self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_is_semi_connected.py:33*

### test_is_semi_connected_false

**Category**: method_call  
**Description**: test is semi connected false  
**Expected**: self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_edge(2, 1, None)
self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_is_semi_connected.py:41*

### test_is_semi_connected_single_node

**Category**: method_call  
**Description**: test is semi connected single node  
**Expected**: self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_node(0)
self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_is_semi_connected.py:47*

### test_is_semi_connected_disconnected_graph

**Category**: method_call  
**Description**: test is semi connected disconnected graph  
**Expected**: self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_node(1)
self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_is_semi_connected.py:58*

### test_is_semi_connected_with_node_gaps

**Category**: method_call  
**Description**: test is semi connected with node gaps  
**Expected**: self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_edge(3, 4, None)
self.assertEqual(rustworkx.is_semi_connected(graph), naive_semi_connected(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_is_semi_connected.py:85*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(graph[node_a], {'a': 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph[node_a], {'a': 1})
self.assertEqual(graph[node_a], {'a': 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_to_undirected.py:57*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(graph[node_a], {'a': 1, 'b': 2})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph[node_a], {'a': 1, 'b': 2})
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_to_undirected.py:60*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_to_undirected.py:61*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(graph.get_edge_data(0, 1), {'a': 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_to_undirected.py:62*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1, 'b': 2})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_to_undirected.py:65*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(graph[node_a], {'a': 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph[node_a], {'a': 1})
self.assertEqual(graph[node_a], {'a': 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_to_undirected.py:57*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(graph[node_a], {'a': 1, 'b': 2})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(digraph[node_a], {'a': 1, 'b': 2})
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_to_undirected.py:60*

### test_shared_ref

**Category**: method_call  
**Description**: test shared ref  
**Expected**: self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_to_undirected.py:61*

### test_null_cartesian_null

**Category**: method_call  
**Description**: test null cartesian null  
**Expected**: self.assertEqual(graph_product.num_edges(), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph_product.num_nodes(), 0)
self.assertEqual(graph_product.num_edges(), 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cartesian_product.py:23*

### test_path_2_cartesian_path_2

**Category**: method_call  
**Description**: test path 2 cartesian path 2  
**Expected**: self.assertEqual(graph_product.num_edges(), 4)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph_product.num_nodes(), 4)
self.assertEqual(graph_product.num_edges(), 4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cartesian_product.py:31*

### test_path_2_cartesian_path_3

**Category**: method_call  
**Description**: test path 2 cartesian path 3  
**Expected**: self.assertEqual(graph_product.num_edges(), 7)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph_product.num_nodes(), 6)
self.assertEqual(graph_product.num_edges(), 7)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cartesian_product.py:39*

### test_null_cartesian_null

**Category**: method_call  
**Description**: test null cartesian null  
**Expected**: self.assertEqual(graph_product.num_edges(), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph_product.num_nodes(), 0)
self.assertEqual(graph_product.num_edges(), 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cartesian_product.py:23*

### test_path_2_cartesian_path_2

**Category**: method_call  
**Description**: test path 2 cartesian path 2  
**Expected**: self.assertEqual(graph_product.num_edges(), 4)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph_product.num_nodes(), 4)
self.assertEqual(graph_product.num_edges(), 4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cartesian_product.py:31*

### test_path_2_cartesian_path_3

**Category**: method_call  
**Description**: test path 2 cartesian path 3  
**Expected**: self.assertEqual(graph_product.num_edges(), 7)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(graph_product.num_nodes(), 6)
self.assertEqual(graph_product.num_edges(), 7)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cartesian_product.py:39*

### test_all_shortest_paths

**Category**: method_call  
**Description**: test all shortest paths  
**Expected**: self.assertIn(expected[0], paths)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

self.assertEqual(len(paths), 2)
self.assertIn(expected[0], paths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_shortest_paths.py:51*

### test_all_shortest_paths

**Category**: method_call  
**Description**: test all shortest paths  
**Expected**: self.assertIn(expected[1], paths)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

self.assertIn(expected[0], paths)
self.assertIn(expected[1], paths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_shortest_paths.py:52*

### test_all_shortest_paths

**Category**: method_call  
**Description**: test all shortest paths  
**Expected**: self.assertIn(expected[0], paths)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(paths), 2)
self.assertIn(expected[0], paths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_shortest_paths.py:51*

### test_all_shortest_paths

**Category**: method_call  
**Description**: test all shortest paths  
**Expected**: self.assertIn(expected[1], paths)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn(expected[0], paths)
self.assertIn(expected[1], paths)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_shortest_paths.py:52*

### test_graph_bfs_tree_edges

**Category**: method_call  
**Description**: test graph bfs tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.graph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_search.py:43*

### test_graph_bfs_tree_edges_no_starting_point

**Category**: method_call  
**Description**: test graph bfs tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3), (4, 7)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.graph_bfs_search(self.graph, None, vis)
self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_search.py:55*

### test_graph_bfs_tree_edges_restricted

**Category**: method_call  
**Description**: test graph bfs tree edges restricted  
**Expected**: self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.graph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_search.py:72*

### test_graph_bfs_goal_search_with_stop_search_exception

**Category**: method_call  
**Description**: test graph bfs goal search with stop search exception  
**Expected**: self.assertEqual(vis.reconstruct_path(), [0, 1, 3])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 3), (2, 1), (2, 5), (2, 6), (5, 3), (4, 7)])

rustworkx.graph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.reconstruct_path(), [0, 1, 3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_search.py:100*

### test_graph_bfs_tree_edges

**Category**: method_call  
**Description**: test graph bfs tree edges  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
rustworkx.graph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_search.py:43*

### test_graph_bfs_tree_edges_no_starting_point

**Category**: method_call  
**Description**: test graph bfs tree edges no starting point  
**Expected**: self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3), (4, 7)])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
rustworkx.graph_bfs_search(self.graph, None, vis)
self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3), (4, 7)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_search.py:55*

### test_subgraph

**Category**: method_call  
**Description**: test subgraph  
**Expected**: self.assertEqual(['b', 'd'], subgraph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([(0, 1, 4)], subgraph.weighted_edge_list())
self.assertEqual(['b', 'd'], subgraph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph.py:27*

### test_subgraph_empty_list

**Category**: method_call  
**Description**: test subgraph empty list  
**Expected**: self.assertEqual(0, len(subgraph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph.py:38*

### test_subgraph_invalid_entry

**Category**: method_call  
**Description**: test subgraph invalid entry  
**Expected**: self.assertEqual(0, len(subgraph))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph.py:49*

### test_subgraph_pass_by_reference

**Category**: method_call  
**Description**: test subgraph pass by reference  
**Expected**: self.assertEqual([{'a': 0}, 'b', 'd'], subgraph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([(0, 1, 1), (0, 2, 3), (1, 2, 4)], subgraph.weighted_edge_list())
self.assertEqual([{'a': 0}, 'b', 'd'], subgraph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph.py:60*

### test_subgraph_replace_weight_no_reference

**Category**: method_call  
**Description**: test subgraph replace weight no reference  
**Expected**: self.assertEqual([{'a': 0}, 'b', 'd'], subgraph.nodes())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual([(0, 1, 1), (0, 2, 3), (1, 2, 4)], subgraph.weighted_edge_list())
self.assertEqual([{'a': 0}, 'b', 'd'], subgraph.nodes())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph.py:73*

### test_edge_subgraph

**Category**: method_call  
**Description**: test edge subgraph  
**Expected**: self.assertEqual([(0, 1, 1), (1, 3, 4)], subgraph.weighted_edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(['a', 'b', 'd'], subgraph.nodes())
self.assertEqual([(0, 1, 1), (1, 3, 4)], subgraph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_subgraph.py:86*

### test_disconnected_graph

**Category**: method_call  
**Description**: test disconnected graph  
**Expected**: self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 1), [[n] for n in graph.nodes()])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (1, 2), (2, 3), (0, 3), (0, 4), (4, 5), (4, 7), (7, 6), (5, 6)]
self.nodes = list(range(8))
g = rustworkx.PyGraph()
g.add_nodes_from(self.nodes)
g.add_edges_from_no_data(self.edges)
self.expected_subgraphs = {k: list(bruteforce(g, k)) for k in range(1, 9)}

graph.add_edge(3, 4, None)
self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 1), [[n] for n in graph.nodes()])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_connected_subgraphs.py:83*

### test_disconnected_graph

**Category**: method_call  
**Description**: test disconnected graph  
**Expected**: self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 2), graph.edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (1, 2), (2, 3), (0, 3), (0, 4), (4, 5), (4, 7), (7, 6), (5, 6)]
self.nodes = list(range(8))
g = rustworkx.PyGraph()
g.add_nodes_from(self.nodes)
g.add_edges_from_no_data(self.edges)
self.expected_subgraphs = {k: list(bruteforce(g, k)) for k in range(1, 9)}

self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 1), [[n] for n in graph.nodes()])
self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 2), graph.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_connected_subgraphs.py:85*

### test_disconnected_graph

**Category**: method_call  
**Description**: test disconnected graph  
**Expected**: self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 3), [[0, 1, 2]])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (1, 2), (2, 3), (0, 3), (0, 4), (4, 5), (4, 7), (7, 6), (5, 6)]
self.nodes = list(range(8))
g = rustworkx.PyGraph()
g.add_nodes_from(self.nodes)
g.add_edges_from_no_data(self.edges)
self.expected_subgraphs = {k: list(bruteforce(g, k)) for k in range(1, 9)}

self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 2), graph.edge_list())
self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 3), [[0, 1, 2]])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_connected_subgraphs.py:88*

### test_disconnected_graph

**Category**: method_call  
**Description**: test disconnected graph  
**Expected**: self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 4), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (1, 2), (2, 3), (0, 3), (0, 4), (4, 5), (4, 7), (7, 6), (5, 6)]
self.nodes = list(range(8))
g = rustworkx.PyGraph()
g.add_nodes_from(self.nodes)
g.add_edges_from_no_data(self.edges)
self.expected_subgraphs = {k: list(bruteforce(g, k)) for k in range(1, 9)}

self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 3), [[0, 1, 2]])
self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 4), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_connected_subgraphs.py:91*

### test_disconnected_graph

**Category**: method_call  
**Description**: test disconnected graph  
**Expected**: self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 1), [[n] for n in graph.nodes()])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
graph.add_edge(3, 4, None)
self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 1), [[n] for n in graph.nodes()])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_connected_subgraphs.py:83*

### test_disconnected_graph

**Category**: method_call  
**Description**: test disconnected graph  
**Expected**: self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 2), graph.edge_list())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 1), [[n] for n in graph.nodes()])
self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 2), graph.edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_connected_subgraphs.py:85*

### test_disconnected_graph

**Category**: method_call  
**Description**: test disconnected graph  
**Expected**: self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 3), [[0, 1, 2]])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 2), graph.edge_list())
self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 3), [[0, 1, 2]])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_connected_subgraphs.py:88*

### test_disconnected_graph

**Category**: method_call  
**Description**: test disconnected graph  
**Expected**: self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 4), [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 3), [[0, 1, 2]])
self.assertConnectedSubgraphsEqual(rustworkx.connected_subgraphs(graph, 4), [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_connected_subgraphs.py:91*

### test_node_frequency

**Category**: method_call  
**Description**: test node frequency  
**Expected**: self.assertAlmostEqual(counts[1] / (path_length + 1), 2 / 14, delta=tol)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertAlmostEqual(counts[0] / (path_length + 1), 1 / 14, delta=tol)
self.assertAlmostEqual(counts[1] / (path_length + 1), 2 / 14, delta=tol)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_random_walk.py:46*

### test_node_frequency

**Category**: method_call  
**Description**: test node frequency  
**Expected**: self.assertAlmostEqual(counts[2] / (path_length + 1), 4 / 14, delta=tol)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertAlmostEqual(counts[1] / (path_length + 1), 2 / 14, delta=tol)
self.assertAlmostEqual(counts[2] / (path_length + 1), 4 / 14, delta=tol)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_random_walk.py:47*

### test_node_frequency

**Category**: method_call  
**Description**: test node frequency  
**Expected**: self.assertAlmostEqual(counts[3] / (path_length + 1), 1 / 14, delta=tol)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertAlmostEqual(counts[2] / (path_length + 1), 4 / 14, delta=tol)
self.assertAlmostEqual(counts[3] / (path_length + 1), 1 / 14, delta=tol)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_random_walk.py:48*

### test_node_frequency

**Category**: method_call  
**Description**: test node frequency  
**Expected**: self.assertAlmostEqual(counts[4] / (path_length + 1), 2 / 14, delta=tol)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertAlmostEqual(counts[3] / (path_length + 1), 1 / 14, delta=tol)
self.assertAlmostEqual(counts[4] / (path_length + 1), 2 / 14, delta=tol)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_random_walk.py:49*

### test_node_frequency

**Category**: method_call  
**Description**: test node frequency  
**Expected**: self.assertAlmostEqual(counts[5] / (path_length + 1), 3 / 14, delta=tol)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertAlmostEqual(counts[4] / (path_length + 1), 2 / 14, delta=tol)
self.assertAlmostEqual(counts[5] / (path_length + 1), 3 / 14, delta=tol)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_random_walk.py:50*

### test_node_frequency

**Category**: method_call  
**Description**: test node frequency  
**Expected**: self.assertAlmostEqual(counts[6] / (path_length + 1), 1 / 14, delta=tol)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertAlmostEqual(counts[5] / (path_length + 1), 3 / 14, delta=tol)
self.assertAlmostEqual(counts[6] / (path_length + 1), 1 / 14, delta=tol)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_random_walk.py:51*

### test_node_frequency

**Category**: method_call  
**Description**: test node frequency  
**Expected**: self.assertAlmostEqual(counts[1] / (path_length + 1), 2 / 14, delta=tol)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertAlmostEqual(counts[0] / (path_length + 1), 1 / 14, delta=tol)
self.assertAlmostEqual(counts[1] / (path_length + 1), 2 / 14, delta=tol)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_random_walk.py:46*

### test_node_frequency

**Category**: method_call  
**Description**: test node frequency  
**Expected**: self.assertAlmostEqual(counts[2] / (path_length + 1), 4 / 14, delta=tol)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertAlmostEqual(counts[1] / (path_length + 1), 2 / 14, delta=tol)
self.assertAlmostEqual(counts[2] / (path_length + 1), 4 / 14, delta=tol)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_random_walk.py:47*

### test_deepcopy_returns_graph

**Category**: instantiation  
**Description**: Instantiate add_node: test deepcopy returns graph  
**Expected**: self.assertIsInstance(dag_b, rustworkx.PyGraph)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_a = dag_a.add_node('a_1')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_deepcopy.py:22*

### test_deepcopy_returns_graph

**Category**: instantiation  
**Description**: Instantiate add_node: test deepcopy returns graph  
**Expected**: self.assertIsInstance(dag_b, rustworkx.PyGraph)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_b = dag_a.add_node('a_2')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_deepcopy.py:23*

### test_deepcopy_returns_graph

**Category**: instantiation  
**Description**: Instantiate add_node: test deepcopy returns graph  
**Expected**: self.assertIsInstance(dag_b, rustworkx.PyGraph)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_c = dag_a.add_node('a_3')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_deepcopy.py:25*

### test_deepcopy_returns_graph

**Category**: instantiation  
**Description**: Instantiate deepcopy: test deepcopy returns graph  
**Expected**: self.assertIsInstance(dag_b, rustworkx.PyGraph)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
dag_b = copy.deepcopy(dag_a)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_deepcopy.py:27*

### test_hits

**Category**: instantiation  
**Description**: Instantiate hits: test hits  
**Confidence**: 0.80  
**Tags**: unittest  

```python
rx_h, rx_a = rustworkx.hits(rx_graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_hits.py:117*

### test_hits

**Category**: instantiation  
**Description**: Instantiate hits_python: test hits  
**Confidence**: 0.80  
**Tags**: unittest  

```python
nx_h, nx_a = hits_python(nx_graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_hits.py:118*

### test_no_convergence

**Category**: instantiation  
**Description**: Instantiate directed_path_graph: test no convergence  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_hits.py:125*

### test_normalized

**Category**: instantiation  
**Description**: Instantiate directed_complete_graph: test normalized  
**Expected**: self.assertEqual({0: 1, 1: 1}, h)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_complete_graph(2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_hits.py:130*

### test_petersen_graph_count

**Category**: instantiation  
**Description**: Instantiate generalized_petersen_graph: test petersen graph count  
**Expected**: self.assertEqual(len(graph), 2 * n)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.generalized_petersen_graph(n, k)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_petersen.py:22*

### test_petersen_graph_edge

**Category**: instantiation  
**Description**: Instantiate generalized_petersen_graph: test petersen graph edge  
**Expected**: self.assertEqual(edge_list, expected_edge_list)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.generalized_petersen_graph(5, 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_petersen.py:27*

### test_petersen_graph_count

**Category**: instantiation  
**Description**: Instantiate generalized_petersen_graph: test petersen graph count  
**Expected**: self.assertEqual(len(graph), 2 * n)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.generalized_petersen_graph(n, k)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_petersen.py:22*

### test_petersen_graph_edge

**Category**: instantiation  
**Description**: Instantiate generalized_petersen_graph: test petersen graph edge  
**Expected**: self.assertEqual(edge_list, expected_edge_list)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.generalized_petersen_graph(5, 2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_petersen.py:27*

### test_dagcircuit_basic

**Category**: instantiation  
**Description**: Instantiate add_node: test dagcircuit basic  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
qr_0_in = dag.add_node('qr[0]')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layers.py:21*

### test_dagcircuit_basic

**Category**: instantiation  
**Description**: Instantiate add_node: test dagcircuit basic  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
qr_0_out = dag.add_node('qr[0]')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layers.py:22*

### test_dagcircuit_basic

**Category**: instantiation  
**Description**: Instantiate add_node: test dagcircuit basic  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
qr_1_in = dag.add_node('qr[1]')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layers.py:23*

### test_dagcircuit_basic

**Category**: instantiation  
**Description**: Instantiate add_node: test dagcircuit basic  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
qr_1_out = dag.add_node('qr[1]')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layers.py:24*

### test_dagcircuit_basic

**Category**: instantiation  
**Description**: Instantiate add_node: test dagcircuit basic  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
cr_0_in = dag.add_node('cr[0]')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layers.py:25*

### test_dagcircuit_basic

**Category**: instantiation  
**Description**: Instantiate add_node: test dagcircuit basic  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
cr_0_out = dag.add_node('cr[0]')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layers.py:26*

### test_single_source_all_shortest_paths_cycle

**Category**: instantiation  
**Description**: Instantiate graph_single_source_all_shortest_paths: test single source all shortest paths cycle  
**Expected**: self.assertEqual(sorted(paths[2]), sorted(expected[2]))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.grid = rustworkx.generators.grid_graph(4, 4)
for edge in self.grid.edge_list():
    self.grid.update_edge(edge[0], edge[1], 1.0)
self.disconnected = rustworkx.PyGraph()
self.disconnected_nodes = self.disconnected.add_nodes_from([0, 1, 2, 3, 4])
self.disconnected.add_edges_from([(self.disconnected_nodes[0], self.disconnected_nodes[1], 1), (self.disconnected_nodes[1], self.disconnected_nodes[2], 1), (self.disconnected_nodes[2], self.disconnected_nodes[3], 1), (self.disconnected_nodes[3], self.disconnected_nodes[0], 1)])

paths = rustworkx.graph_single_source_all_shortest_paths(self.cycle, self.cycle_nodes[0])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_single_source_all_shortest_paths.py:35*

### test_single_source_all_shortest_paths_grid

**Category**: instantiation  
**Description**: Instantiate graph_single_source_all_shortest_paths: test single source all shortest paths grid  
**Expected**: self.assertEqual(sorted(paths[11]), sorted(expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.grid = rustworkx.generators.grid_graph(4, 4)
for edge in self.grid.edge_list():
    self.grid.update_edge(edge[0], edge[1], 1.0)
self.disconnected = rustworkx.PyGraph()
self.disconnected_nodes = self.disconnected.add_nodes_from([0, 1, 2, 3, 4])
self.disconnected.add_edges_from([(self.disconnected_nodes[0], self.disconnected_nodes[1], 1), (self.disconnected_nodes[1], self.disconnected_nodes[2], 1), (self.disconnected_nodes[2], self.disconnected_nodes[3], 1), (self.disconnected_nodes[3], self.disconnected_nodes[0], 1)])

paths = rustworkx.graph_single_source_all_shortest_paths(self.grid, 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_single_source_all_shortest_paths.py:40*

### test_single_source_all_shortest_paths_weighted_cycle

**Category**: instantiation  
**Description**: Instantiate graph_single_source_all_shortest_paths: test single source all shortest paths weighted cycle  
**Expected**: self.assertEqual(sorted(paths[2]), sorted(expected[2]))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.grid = rustworkx.generators.grid_graph(4, 4)
for edge in self.grid.edge_list():
    self.grid.update_edge(edge[0], edge[1], 1.0)
self.disconnected = rustworkx.PyGraph()
self.disconnected_nodes = self.disconnected.add_nodes_from([0, 1, 2, 3, 4])
self.disconnected.add_edges_from([(self.disconnected_nodes[0], self.disconnected_nodes[1], 1), (self.disconnected_nodes[1], self.disconnected_nodes[2], 1), (self.disconnected_nodes[2], self.disconnected_nodes[3], 1), (self.disconnected_nodes[3], self.disconnected_nodes[0], 1)])

paths = rustworkx.graph_single_source_all_shortest_paths(self.cycle, self.cycle_nodes[0], weight_fn=lambda x: float(x))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_single_source_all_shortest_paths.py:52*

### test_single_source_all_shortest_paths_weighted_grid

**Category**: instantiation  
**Description**: Instantiate graph_single_source_all_shortest_paths: test single source all shortest paths weighted grid  
**Expected**: self.assertEqual(sorted(paths[11]), sorted(expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.grid = rustworkx.generators.grid_graph(4, 4)
for edge in self.grid.edge_list():
    self.grid.update_edge(edge[0], edge[1], 1.0)
self.disconnected = rustworkx.PyGraph()
self.disconnected_nodes = self.disconnected.add_nodes_from([0, 1, 2, 3, 4])
self.disconnected.add_edges_from([(self.disconnected_nodes[0], self.disconnected_nodes[1], 1), (self.disconnected_nodes[1], self.disconnected_nodes[2], 1), (self.disconnected_nodes[2], self.disconnected_nodes[3], 1), (self.disconnected_nodes[3], self.disconnected_nodes[0], 1)])

paths = rustworkx.graph_single_source_all_shortest_paths(self.grid, 1, weight_fn=lambda x: float(x) if x is not None else 1.0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_single_source_all_shortest_paths.py:59*

### test_single_source_all_shortest_paths_disconnected_from_cycle

**Category**: instantiation  
**Description**: Instantiate graph_single_source_all_shortest_paths: test single source all shortest paths disconnected from cycle  
**Expected**: self.assertEqual(sorted(paths[2]), sorted(expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.grid = rustworkx.generators.grid_graph(4, 4)
for edge in self.grid.edge_list():
    self.grid.update_edge(edge[0], edge[1], 1.0)
self.disconnected = rustworkx.PyGraph()
self.disconnected_nodes = self.disconnected.add_nodes_from([0, 1, 2, 3, 4])
self.disconnected.add_edges_from([(self.disconnected_nodes[0], self.disconnected_nodes[1], 1), (self.disconnected_nodes[1], self.disconnected_nodes[2], 1), (self.disconnected_nodes[2], self.disconnected_nodes[3], 1), (self.disconnected_nodes[3], self.disconnected_nodes[0], 1)])

paths = rustworkx.graph_single_source_all_shortest_paths(self.disconnected, self.disconnected_nodes[0])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_single_source_all_shortest_paths.py:73*

### test_single_source_all_shortest_paths_disconnected_from_isolated

**Category**: instantiation  
**Description**: Instantiate graph_single_source_all_shortest_paths: test single source all shortest paths disconnected from isolated  
**Expected**: self.assertEqual(paths[4], expected)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.grid = rustworkx.generators.grid_graph(4, 4)
for edge in self.grid.edge_list():
    self.grid.update_edge(edge[0], edge[1], 1.0)
self.disconnected = rustworkx.PyGraph()
self.disconnected_nodes = self.disconnected.add_nodes_from([0, 1, 2, 3, 4])
self.disconnected.add_edges_from([(self.disconnected_nodes[0], self.disconnected_nodes[1], 1), (self.disconnected_nodes[1], self.disconnected_nodes[2], 1), (self.disconnected_nodes[2], self.disconnected_nodes[3], 1), (self.disconnected_nodes[3], self.disconnected_nodes[0], 1)])

paths = rustworkx.graph_single_source_all_shortest_paths(self.disconnected, self.disconnected_nodes[4])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_single_source_all_shortest_paths.py:80*

### test_single_source_all_shortest_paths_zero_weight

**Category**: instantiation  
**Description**: Instantiate add_nodes_from: test single source all shortest paths zero weight  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.grid = rustworkx.generators.grid_graph(4, 4)
for edge in self.grid.edge_list():
    self.grid.update_edge(edge[0], edge[1], 1.0)
self.disconnected = rustworkx.PyGraph()
self.disconnected_nodes = self.disconnected.add_nodes_from([0, 1, 2, 3, 4])
self.disconnected.add_edges_from([(self.disconnected_nodes[0], self.disconnected_nodes[1], 1), (self.disconnected_nodes[1], self.disconnected_nodes[2], 1), (self.disconnected_nodes[2], self.disconnected_nodes[3], 1), (self.disconnected_nodes[3], self.disconnected_nodes[0], 1)])

nodes = graph.add_nodes_from([0, 1, 2, 3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_single_source_all_shortest_paths.py:103*

### test_single_source_all_shortest_paths_zero_weight

**Category**: instantiation  
**Description**: Instantiate dijkstra_shortest_path_lengths: test single source all shortest paths zero weight  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.grid = rustworkx.generators.grid_graph(4, 4)
for edge in self.grid.edge_list():
    self.grid.update_edge(edge[0], edge[1], 1.0)
self.disconnected = rustworkx.PyGraph()
self.disconnected_nodes = self.disconnected.add_nodes_from([0, 1, 2, 3, 4])
self.disconnected.add_edges_from([(self.disconnected_nodes[0], self.disconnected_nodes[1], 1), (self.disconnected_nodes[1], self.disconnected_nodes[2], 1), (self.disconnected_nodes[2], self.disconnected_nodes[3], 1), (self.disconnected_nodes[3], self.disconnected_nodes[0], 1)])

shortest_lengths = rustworkx.dijkstra_shortest_path_lengths(graph, source, lambda x: x)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_single_source_all_shortest_paths.py:112*

### test_astar_null_heuristic

**Category**: instantiation  
**Description**: Instantiate graph_astar_shortest_path: test astar null heuristic  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
path = rustworkx.graph_astar_shortest_path(g, a, lambda goal: goal == 'E', lambda x: float(x), lambda y: 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_astar.py:36*

### test_astar_manhattan_heuristic

**Category**: instantiation  
**Description**: Instantiate add_node: test astar manhattan heuristic  
**Confidence**: 0.80  
**Tags**: unittest  

```python
a = g.add_node((0.0, 0.0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_astar.py:44*

### test_astar_manhattan_heuristic

**Category**: instantiation  
**Description**: Instantiate add_node: test astar manhattan heuristic  
**Confidence**: 0.80  
**Tags**: unittest  

```python
b = g.add_node((2.0, 0.0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_astar.py:45*

### test_astar_manhattan_heuristic

**Category**: instantiation  
**Description**: Instantiate add_node: test astar manhattan heuristic  
**Confidence**: 0.80  
**Tags**: unittest  

```python
c = g.add_node((1.0, 1.0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_astar.py:46*

### test_astar_manhattan_heuristic

**Category**: instantiation  
**Description**: Instantiate add_node: test astar manhattan heuristic  
**Confidence**: 0.80  
**Tags**: unittest  

```python
d = g.add_node((0.0, 2.0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_astar.py:47*

### test_astar_manhattan_heuristic

**Category**: instantiation  
**Description**: Instantiate add_node: test astar manhattan heuristic  
**Confidence**: 0.80  
**Tags**: unittest  

```python
e = g.add_node((3.0, 3.0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_astar.py:48*

### test_all_simple_paths

**Category**: instantiation  
**Description**: Instantiate graph_all_simple_paths: test all simple paths  
**Expected**: self.assertEqual(len(expected), len(paths))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 5), (5, 2), (5, 3)]

paths = rustworkx.graph_all_simple_paths(graph, 0, 5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_simple_paths.py:42*

### test_all_simple_paths_default_min_depth

**Category**: instantiation  
**Description**: Instantiate graph_all_simple_paths: test all simple paths default min depth  
**Expected**: self.assertEqual(len(expected), len(paths))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 5), (5, 2), (5, 3)]

paths = rustworkx.graph_all_simple_paths(graph, 0, 5, min_depth=0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_simple_paths.py:97*

### test_s_t_blossom_with_removed_nodes

**Category**: instantiation  
**Description**: Instantiate add_node: test s t blossom with removed nodes  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_id = graph.add_node(None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_max_weight_matching.py:210*

### test_determinism_five_node_max_cardinality

**Category**: instantiation  
**Description**: Instantiate max_weight_matching: test determinism five node max cardinality  
**Confidence**: 0.80  
**Tags**: unittest  

```python
initial_result = rustworkx.max_weight_matching(graph, max_cardinality=True, weight_fn=lambda x: x, verify_optimum=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_max_weight_matching.py:465*

### test_isolates

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates  
**Expected**: self.assertEqual(res, [2, 3])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isolates.py:23*

### test_isolates_with_holes

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates with holes  
**Expected**: self.assertEqual(res, [3])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isolates.py:31*

### test_isolates_empty_graph

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates empty graph  
**Expected**: self.assertEqual(res, [])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isolates.py:36*

### test_isolates_outgoing_star

**Category**: instantiation  
**Description**: Instantiate directed_star_graph: test isolates outgoing star  
**Expected**: self.assertEqual(res, [])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_star_graph(5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isolates.py:40*

### test_isolates_outgoing_star

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates outgoing star  
**Expected**: self.assertEqual(res, [])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isolates.py:41*

### test_isolates_incoming_star

**Category**: instantiation  
**Description**: Instantiate directed_star_graph: test isolates incoming star  
**Expected**: self.assertEqual(res, [])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_star_graph(5, inward=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isolates.py:45*

### test_isolates_incoming_star

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates incoming star  
**Expected**: self.assertEqual(res, [])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isolates.py:46*

### test_isolates

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates  
**Expected**: self.assertEqual(res, [2, 3])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isolates.py:23*

### test_isolates_with_holes

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates with holes  
**Expected**: self.assertEqual(res, [3])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isolates.py:31*

### test_isolates_empty_graph

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates empty graph  
**Expected**: self.assertEqual(res, [])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_isolates.py:36*

### test_is_bipartite

**Category**: instantiation  
**Description**: Instantiate directed_heavy_square_graph: test is bipartite  
**Expected**: self.assertTrue(rustworkx.is_bipartite(graph))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_heavy_square_graph(5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bipartite.py:20*

### test_two_colors

**Category**: instantiation  
**Description**: Instantiate directed_star_graph: test two colors  
**Expected**: self.assertEqual(rustworkx.two_color(graph), {0: 1, 1: 0, 2: 0, 3: 0, 4: 0})  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_star_graph(5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bipartite.py:24*

### test_random_layout

**Category**: instantiation  
**Description**: Instantiate graph_random_layout: test random layout  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(10)

res = rustworkx.graph_random_layout(self.graph, seed=42)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_layout.py:37*

### test_random_layout_center

**Category**: instantiation  
**Description**: Instantiate graph_random_layout: test random layout center  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(10)

res = rustworkx.graph_random_layout(self.graph, center=(0.5, 0.5), seed=42)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_layout.py:53*

### test_random_layout_no_seed

**Category**: instantiation  
**Description**: Instantiate graph_random_layout: test random layout no seed  
**Expected**: self.assertIsInstance(res, rustworkx.Pos2DMapping)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(10)

res = rustworkx.graph_random_layout(self.graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_layout.py:69*

### test_bipartite_layout_empty

**Category**: instantiation  
**Description**: Instantiate bipartite_layout: test bipartite layout empty  
**Expected**: self.assertEqual({}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(10)

res = rustworkx.bipartite_layout(rustworkx.PyGraph(), set())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_layout.py:82*

### test_dagcircuit_basic

**Category**: instantiation  
**Description**: Instantiate add_node: test dagcircuit basic  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
qr_0_in = dag.add_node('qr[0]')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_runs.py:21*

### test_dagcircuit_basic

**Category**: instantiation  
**Description**: Instantiate add_node: test dagcircuit basic  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
qr_0_out = dag.add_node('qr[0]')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_runs.py:22*

### test_graph_dfs_edges

**Category**: instantiation  
**Description**: Instantiate graph_dfs_edges: test graph dfs edges  
**Expected**: self.assertEqual(expected, edges)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
edges = rustworkx.graph_dfs_edges(graph, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_edges.py:22*

### test_graph_disconnected_dfs_edges

**Category**: instantiation  
**Description**: Instantiate graph_dfs_edges: test graph disconnected dfs edges  
**Expected**: self.assertEqual(expected, edges)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
edges = rustworkx.graph_dfs_edges(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_edges.py:29*

### test_graph_dfs_edges_empty

**Category**: instantiation  
**Description**: Instantiate graph_dfs_edges: test graph dfs edges empty  
**Expected**: self.assertEqual([], edges)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
edges = rustworkx.graph_dfs_edges(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_edges.py:35*

### test_graph_dfs_edges_single_node

**Category**: instantiation  
**Description**: Instantiate empty_graph: test graph dfs edges single node  
**Expected**: self.assertEqual([], edges)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.empty_graph(1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_edges.py:39*

### test_graph_dfs_edges_single_node

**Category**: instantiation  
**Description**: Instantiate graph_dfs_edges: test graph dfs edges single node  
**Expected**: self.assertEqual([], edges)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
edges = rustworkx.graph_dfs_edges(graph, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_edges.py:40*

### test_graph_dfs_edges_node_gaps

**Category**: instantiation  
**Description**: Instantiate graph_dfs_edges: test graph dfs edges node gaps  
**Expected**: self.assertEqual([(0, 2), (2, 4)], edges)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
edges = rustworkx.graph_dfs_edges(graph, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_edges.py:50*

### test_graph_dfs_edges_star

**Category**: instantiation  
**Description**: Instantiate star_graph: test graph dfs edges star  
**Expected**: self.assertEqual(len(edges), 100)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.star_graph(101)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_edges.py:54*

### test_graph_dfs_edges_star

**Category**: instantiation  
**Description**: Instantiate list: test graph dfs edges star  
**Expected**: self.assertEqual(len(edges), 100)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
spokes = list(range(1, 101))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dfs_edges.py:56*

### test_clique

**Category**: instantiation  
**Description**: Instantiate complement: test clique  
**Expected**: self.assertEqual(graph.nodes(), complement_graph.nodes())  
**Confidence**: 0.80  
**Tags**: unittest  

```python
complement_graph = rustworkx.complement(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_complement.py:24*

### test_empty

**Category**: instantiation  
**Description**: Instantiate complement: test empty  
**Expected**: self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
complement_graph = rustworkx.complement(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_complement.py:36*

### test_attrs_set_at_init

**Category**: instantiation  
**Description**: Instantiate PyDiGraph: test attrs set at init  
**Expected**: self.assertEqual({'foo': 'bar'}, graph.attrs)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.PyDiGraph(attrs=dict(foo='bar'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_graph_attrs.py:24*

### test_attrs_set_at_init_override

**Category**: instantiation  
**Description**: Instantiate PyDiGraph: test attrs set at init override  
**Expected**: self.assertEqual({'foo': 'bar'}, graph.attrs)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.PyDiGraph(attrs=dict(foo='bar'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_graph_attrs.py:28*

### test_attrs_set_at_init

**Category**: instantiation  
**Description**: Instantiate PyDiGraph: test attrs set at init  
**Expected**: self.assertEqual({'foo': 'bar'}, graph.attrs)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.PyDiGraph(attrs=dict(foo='bar'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_graph_attrs.py:24*

### test_attrs_set_at_init_override

**Category**: instantiation  
**Description**: Instantiate PyDiGraph: test attrs set at init override  
**Expected**: self.assertEqual({'foo': 'bar'}, graph.attrs)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.PyDiGraph(attrs=dict(foo='bar'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_graph_attrs.py:28*

### test_graph_distance_matrix

**Category**: instantiation  
**Description**: Instantiate graph_distance_matrix: test graph distance matrix  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
dist = rustworkx.graph_distance_matrix(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dist_matrix.py:25*

### test_graph_distance_matrix

**Category**: instantiation  
**Description**: Instantiate array: test graph distance matrix  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
expected = np.array([[0.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0], [1.0, 0.0, 1.0, 2.0, 3.0, 3.0, 2.0], [2.0, 1.0, 0.0, 1.0, 2.0, 3.0, 3.0], [3.0, 2.0, 1.0, 0.0, 1.0, 2.0, 3.0], [3.0, 3.0, 2.0, 1.0, 0.0, 1.0, 2.0], [2.0, 3.0, 3.0, 2.0, 1.0, 0.0, 1.0], [1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 0.0]])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dist_matrix.py:26*

### test_graph_distance_matrix_parallel

**Category**: instantiation  
**Description**: Instantiate graph_distance_matrix: test graph distance matrix parallel  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
dist = rustworkx.graph_distance_matrix(graph, parallel_threshold=5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dist_matrix.py:43*

### test_graph_distance_matrix_parallel

**Category**: instantiation  
**Description**: Instantiate array: test graph distance matrix parallel  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
expected = np.array([[0.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0], [1.0, 0.0, 1.0, 2.0, 3.0, 3.0, 2.0], [2.0, 1.0, 0.0, 1.0, 2.0, 3.0, 3.0], [3.0, 2.0, 1.0, 0.0, 1.0, 2.0, 3.0], [3.0, 3.0, 2.0, 1.0, 0.0, 1.0, 2.0], [2.0, 3.0, 3.0, 2.0, 1.0, 0.0, 1.0], [1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 0.0]])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dist_matrix.py:44*

### test_graph_distance_matrix_non_zero_null

**Category**: instantiation  
**Description**: Instantiate graph_distance_matrix: test graph distance matrix non zero null  
**Expected**: self.assertTrue(np.array_equal(dist, expected, equal_nan=True))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
dist = rustworkx.graph_distance_matrix(graph, null_value=np.nan)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dist_matrix.py:62*

### test_graph_distance_matrix_non_zero_null

**Category**: instantiation  
**Description**: Instantiate array: test graph distance matrix non zero null  
**Expected**: self.assertTrue(np.array_equal(dist, expected, equal_nan=True))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
expected = np.array([[0.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, np.nan], [1.0, 0.0, 1.0, 2.0, 3.0, 3.0, 2.0, np.nan], [2.0, 1.0, 0.0, 1.0, 2.0, 3.0, 3.0, np.nan], [3.0, 2.0, 1.0, 0.0, 1.0, 2.0, 3.0, np.nan], [3.0, 3.0, 2.0, 1.0, 0.0, 1.0, 2.0, np.nan], [2.0, 3.0, 3.0, 2.0, 1.0, 0.0, 1.0, np.nan], [1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 0.0, np.nan], [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 0.0]])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dist_matrix.py:63*

### test_graph_distance_matrix_parallel_non_zero_null

**Category**: instantiation  
**Description**: Instantiate graph_distance_matrix: test graph distance matrix parallel non zero null  
**Expected**: self.assertTrue(np.array_equal(dist, expected, equal_nan=True))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
dist = rustworkx.graph_distance_matrix(graph, parallel_threshold=5, null_value=np.nan)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dist_matrix.py:82*

### test_graph_distance_matrix_parallel_non_zero_null

**Category**: instantiation  
**Description**: Instantiate array: test graph distance matrix parallel non zero null  
**Expected**: self.assertTrue(np.array_equal(dist, expected, equal_nan=True))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
expected = np.array([[0.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, np.nan], [1.0, 0.0, 1.0, 2.0, 3.0, 3.0, 2.0, np.nan], [2.0, 1.0, 0.0, 1.0, 2.0, 3.0, 3.0, np.nan], [3.0, 2.0, 1.0, 0.0, 1.0, 2.0, 3.0, np.nan], [3.0, 3.0, 2.0, 1.0, 0.0, 1.0, 2.0, np.nan], [2.0, 3.0, 3.0, 2.0, 1.0, 0.0, 1.0, np.nan], [1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 0.0, np.nan], [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 0.0]])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dist_matrix.py:83*

### test_graph_distance_matrix_node_hole

**Category**: instantiation  
**Description**: Instantiate path_graph: test graph distance matrix node hole  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dist_matrix.py:98*

### test_graph_distance_matrix_node_hole

**Category**: instantiation  
**Description**: Instantiate graph_distance_matrix: test graph distance matrix node hole  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
dist = rustworkx.graph_distance_matrix(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_dist_matrix.py:100*

### test_single_source_all_shortest_paths_cycle

**Category**: instantiation  
**Description**: Instantiate digraph_single_source_all_shortest_paths: test single source all shortest paths cycle  
**Expected**: self.assertEqual(paths[2], expected[2])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyDiGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.directed = rustworkx.PyDiGraph()
self.directed_nodes = self.directed.add_nodes_from([0, 1, 2, 3])
self.directed.add_edges_from([(self.directed_nodes[0], self.directed_nodes[1], 1), (self.directed_nodes[0], self.directed_nodes[2], 1), (self.directed_nodes[1], self.directed_nodes[3], 1), (self.directed_nodes[2], self.directed_nodes[3], 1)])

paths = rustworkx.digraph_single_source_all_shortest_paths(self.cycle, self.cycle_nodes[0])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_digraph_single_source_all_shortest_paths.py:29*

### test_single_source_all_shortest_paths_directed

**Category**: instantiation  
**Description**: Instantiate digraph_single_source_all_shortest_paths: test single source all shortest paths directed  
**Expected**: self.assertEqual(sorted(paths[3]), sorted(expected[3]))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyDiGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.directed = rustworkx.PyDiGraph()
self.directed_nodes = self.directed.add_nodes_from([0, 1, 2, 3])
self.directed.add_edges_from([(self.directed_nodes[0], self.directed_nodes[1], 1), (self.directed_nodes[0], self.directed_nodes[2], 1), (self.directed_nodes[1], self.directed_nodes[3], 1), (self.directed_nodes[2], self.directed_nodes[3], 1)])

paths = rustworkx.digraph_single_source_all_shortest_paths(self.directed, self.directed_nodes[0])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_digraph_single_source_all_shortest_paths.py:34*

### test_single_source_all_shortest_paths_as_undirected

**Category**: instantiation  
**Description**: Instantiate digraph_single_source_all_shortest_paths: test single source all shortest paths as undirected  
**Expected**: self.assertEqual(sorted(paths[3]), sorted(expected[3]))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyDiGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.directed = rustworkx.PyDiGraph()
self.directed_nodes = self.directed.add_nodes_from([0, 1, 2, 3])
self.directed.add_edges_from([(self.directed_nodes[0], self.directed_nodes[1], 1), (self.directed_nodes[0], self.directed_nodes[2], 1), (self.directed_nodes[1], self.directed_nodes[3], 1), (self.directed_nodes[2], self.directed_nodes[3], 1)])

paths = rustworkx.digraph_single_source_all_shortest_paths(self.directed, self.directed_nodes[0], as_undirected=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_digraph_single_source_all_shortest_paths.py:41*

### test_single_source_all_shortest_paths_zero_weight

**Category**: instantiation  
**Description**: Instantiate add_nodes_from: test single source all shortest paths zero weight  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyDiGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.directed = rustworkx.PyDiGraph()
self.directed_nodes = self.directed.add_nodes_from([0, 1, 2, 3])
self.directed.add_edges_from([(self.directed_nodes[0], self.directed_nodes[1], 1), (self.directed_nodes[0], self.directed_nodes[2], 1), (self.directed_nodes[1], self.directed_nodes[3], 1), (self.directed_nodes[2], self.directed_nodes[3], 1)])

nodes = graph.add_nodes_from([0, 1, 2, 3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_digraph_single_source_all_shortest_paths.py:58*

### test_single_source_all_shortest_paths_zero_weight

**Category**: instantiation  
**Description**: Instantiate digraph_dijkstra_shortest_path_lengths: test single source all shortest paths zero weight  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyDiGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.directed = rustworkx.PyDiGraph()
self.directed_nodes = self.directed.add_nodes_from([0, 1, 2, 3])
self.directed.add_edges_from([(self.directed_nodes[0], self.directed_nodes[1], 1), (self.directed_nodes[0], self.directed_nodes[2], 1), (self.directed_nodes[1], self.directed_nodes[3], 1), (self.directed_nodes[2], self.directed_nodes[3], 1)])

shortest_lengths = rustworkx.digraph_dijkstra_shortest_path_lengths(graph, source, lambda e: e)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_digraph_single_source_all_shortest_paths.py:67*

### test_single_source_all_shortest_paths_zero_weight

**Category**: instantiation  
**Description**: Instantiate digraph_single_source_all_shortest_paths: test single source all shortest paths zero weight  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyDiGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.directed = rustworkx.PyDiGraph()
self.directed_nodes = self.directed.add_nodes_from([0, 1, 2, 3])
self.directed.add_edges_from([(self.directed_nodes[0], self.directed_nodes[1], 1), (self.directed_nodes[0], self.directed_nodes[2], 1), (self.directed_nodes[1], self.directed_nodes[3], 1), (self.directed_nodes[2], self.directed_nodes[3], 1)])

all_shortest_paths = rustworkx.digraph_single_source_all_shortest_paths(graph, source)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_digraph_single_source_all_shortest_paths.py:72*

### test_single_source_all_shortest_paths_zero_weight

**Category**: instantiation  
**Description**: Instantiate all_simple_paths: test single source all shortest paths zero weight  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyDiGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.directed = rustworkx.PyDiGraph()
self.directed_nodes = self.directed.add_nodes_from([0, 1, 2, 3])
self.directed.add_edges_from([(self.directed_nodes[0], self.directed_nodes[1], 1), (self.directed_nodes[0], self.directed_nodes[2], 1), (self.directed_nodes[1], self.directed_nodes[3], 1), (self.directed_nodes[2], self.directed_nodes[3], 1)])

all_paths = rustworkx.all_simple_paths(graph, source, target_idx)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_digraph_single_source_all_shortest_paths.py:81*

### test_single_source_all_shortest_paths_zero_weight

**Category**: instantiation  
**Description**: Instantiate get: test single source all shortest paths zero weight  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.cycle = rustworkx.PyDiGraph()
self.cycle_nodes = self.cycle.add_nodes_from([0, 1, 2, 3])
self.cycle.add_edges_from([(self.cycle_nodes[0], self.cycle_nodes[1], 1), (self.cycle_nodes[1], self.cycle_nodes[2], 1), (self.cycle_nodes[2], self.cycle_nodes[3], 1), (self.cycle_nodes[3], self.cycle_nodes[0], 1)])
self.directed = rustworkx.PyDiGraph()
self.directed_nodes = self.directed.add_nodes_from([0, 1, 2, 3])
self.directed.add_edges_from([(self.directed_nodes[0], self.directed_nodes[1], 1), (self.directed_nodes[0], self.directed_nodes[2], 1), (self.directed_nodes[1], self.directed_nodes[3], 1), (self.directed_nodes[2], self.directed_nodes[3], 1)])

computed_paths = all_shortest_paths.get(target_idx, [])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_digraph_single_source_all_shortest_paths.py:97*

### test_simple_example

**Category**: instantiation  
**Description**: Instantiate graph_unweighted_average_shortest_path_length: test simple example  
**Expected**: self.assertAlmostEqual(2.5714285714285716, res, delta=1e-07)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.graph_unweighted_average_shortest_path_length(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_avg_shortest_path.py:24*

### test_cycle_graph

**Category**: instantiation  
**Description**: Instantiate cycle_graph: test cycle graph  
**Expected**: self.assertAlmostEqual(2, res, delta=1e-07)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.cycle_graph(7)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_avg_shortest_path.py:28*

### test_cycle_graph

**Category**: instantiation  
**Description**: Instantiate unweighted_average_shortest_path_length: test cycle graph  
**Expected**: self.assertAlmostEqual(2, res, delta=1e-07)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.unweighted_average_shortest_path_length(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_avg_shortest_path.py:29*

### test_path_graph

**Category**: instantiation  
**Description**: Instantiate path_graph: test path graph  
**Expected**: self.assertAlmostEqual(2, res, delta=1e-07)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_avg_shortest_path.py:33*

### test_path_graph

**Category**: instantiation  
**Description**: Instantiate unweighted_average_shortest_path_length: test path graph  
**Expected**: self.assertAlmostEqual(2, res, delta=1e-07)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.unweighted_average_shortest_path_length(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_avg_shortest_path.py:34*

### test_parallel_grid

**Category**: instantiation  
**Description**: Instantiate grid_graph: test parallel grid  
**Expected**: self.assertAlmostEqual(13.666666666666666, res, delta=1e-07)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.grid_graph(30, 11)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_avg_shortest_path.py:38*

### test_transitivity_directed

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity directed  
**Expected**: self.assertEqual(res, 3 / 10)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitivity.py:23*

### test_transitivity_triangle_directed

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity triangle directed  
**Expected**: self.assertEqual(res, 0.5)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitivity.py:30*

### test_transitivity_fulltriangle_directed

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity fulltriangle directed  
**Expected**: self.assertEqual(res, 1.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitivity.py:37*

### test_transitivity_empty_directed

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity empty directed  
**Expected**: self.assertEqual(res, 0.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitivity.py:42*

### test_transitivity_directed

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity directed  
**Expected**: self.assertEqual(res, 3 / 10)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitivity.py:23*

### test_transitivity_triangle_directed

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity triangle directed  
**Expected**: self.assertEqual(res, 0.5)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitivity.py:30*

### test_transitivity_fulltriangle_directed

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity fulltriangle directed  
**Expected**: self.assertEqual(res, 1.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitivity.py:37*

### test_transitivity_empty_directed

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity empty directed  
**Expected**: self.assertEqual(res, 0.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitivity.py:42*

### test_complete_graph

**Category**: instantiation  
**Description**: Instantiate complete_graph: test complete graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.complete_graph(m)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_complete.py:21*

### test_complete_directed_graph

**Category**: instantiation  
**Description**: Instantiate directed_complete_graph: test complete directed graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_complete_graph(m)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_complete.py:27*

### test_complete_graph

**Category**: instantiation  
**Description**: Instantiate complete_graph: test complete graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.complete_graph(m)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_complete.py:21*

### test_complete_directed_graph

**Category**: instantiation  
**Description**: Instantiate directed_complete_graph: test complete directed graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_complete_graph(m)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_complete.py:27*

### test_directed_empty

**Category**: instantiation  
**Description**: Instantiate core_number: test directed empty  
**Expected**: self.assertIsInstance(res, dict)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.example_edges = [(0, 2), (0, 3), (0, 5), (1, 4), (1, 6), (1, 7), (2, 3), (3, 5), (2, 5), (5, 6), (4, 6), (4, 7), (6, 7), (5, 8), (6, 8), (6, 9), (8, 9), (0, 10), (1, 10), (1, 11), (10, 11), (12, 13), (13, 15), (14, 15), (12, 14), (8, 19), (11, 16), (11, 17), (12, 18)]
example_core = {}
for i in range(8):
    example_core[i] = 3
for i in range(8, 16):
    example_core[i] = 2
for i in range(16, 20):
    example_core[i] = 1
example_core[20] = 0
self.example_core = example_core

res = rustworkx.core_number(digraph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_core_number.py:71*

### test_directed_all_0

**Category**: instantiation  
**Description**: Instantiate core_number: test directed all 0  
**Expected**: self.assertIsInstance(res, dict)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.example_edges = [(0, 2), (0, 3), (0, 5), (1, 4), (1, 6), (1, 7), (2, 3), (3, 5), (2, 5), (5, 6), (4, 6), (4, 7), (6, 7), (5, 8), (6, 8), (6, 9), (8, 9), (0, 10), (1, 10), (1, 11), (10, 11), (12, 13), (13, 15), (14, 15), (12, 14), (8, 19), (11, 16), (11, 17), (12, 18)]
example_core = {}
for i in range(8):
    example_core[i] = 3
for i in range(8, 16):
    example_core[i] = 2
for i in range(16, 20):
    example_core[i] = 1
example_core[20] = 0
self.example_core = example_core

res = rustworkx.core_number(digraph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_core_number.py:78*

### test_simple_chain

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test simple chain  
**Expected**: self.assertEqual([sorted(layer) for layer in layers], [[3], [2, 4], [1, 5], [0]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(6).to_directed()

layers = rustworkx.bfs_layers(self.graph, [3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_layer.py:10*

### test_multiple_sources

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test multiple sources  
**Expected**: self.assertEqual(sorted(layers[0]), [0, 3])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(6).to_directed()

layers = rustworkx.bfs_layers(self.graph, [0, 3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_layer.py:14*

### test_disconnected_digraph

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test disconnected digraph  
**Expected**: self.assertEqual(layers, [[2], [3]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(6).to_directed()

layers = rustworkx.bfs_layers(g, [2])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_layer.py:20*

### test_no_sources_defaults

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test no sources defaults  
**Expected**: self.assertTrue(any((0 in layer for layer in layers)))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(6).to_directed()

layers = rustworkx.bfs_layers(self.graph, None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_layer.py:24*

### test_simple_chain

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test simple chain  
**Expected**: self.assertEqual([sorted(layer) for layer in layers], [[3], [2, 4], [1, 5], [0]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
layers = rustworkx.bfs_layers(self.graph, [3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_layer.py:10*

### test_multiple_sources

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test multiple sources  
**Expected**: self.assertEqual(sorted(layers[0]), [0, 3])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
layers = rustworkx.bfs_layers(self.graph, [0, 3])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_layer.py:14*

### test_disconnected_digraph

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test disconnected digraph  
**Expected**: self.assertEqual(layers, [[2], [3]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
layers = rustworkx.bfs_layers(g, [2])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_layer.py:20*

### test_no_sources_defaults

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test no sources defaults  
**Expected**: self.assertTrue(any((0 in layer for layer in layers)))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
layers = rustworkx.bfs_layers(self.graph, None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bfs_layer.py:24*

### test_find_cycle

**Category**: instantiation  
**Description**: Instantiate digraph_find_cycle: test find cycle  
**Expected**: self.assertCycle(0, graph, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.add_nodes_from(list(range(10)))
self.graph.add_edges_from_no_data([(0, 1), (3, 0), (0, 5), (8, 0), (1, 2), (1, 6), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9)])

res = rustworkx.digraph_find_cycle(graph, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_find_cycle.py:54*

### test_find_cycle_multiple_roots_same_cycles

**Category**: instantiation  
**Description**: Instantiate digraph_find_cycle: test find cycle multiple roots same cycles  
**Expected**: self.assertCycle(0, self.graph, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.add_nodes_from(list(range(10)))
self.graph.add_edges_from_no_data([(0, 1), (3, 0), (0, 5), (8, 0), (1, 2), (1, 6), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9)])

res = rustworkx.digraph_find_cycle(self.graph, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_find_cycle.py:58*

### test_find_cycle_multiple_roots_same_cycles

**Category**: instantiation  
**Description**: Instantiate digraph_find_cycle: test find cycle multiple roots same cycles  
**Expected**: self.assertCycle(1, self.graph, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.add_nodes_from(list(range(10)))
self.graph.add_edges_from_no_data([(0, 1), (3, 0), (0, 5), (8, 0), (1, 2), (1, 6), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9)])

res = rustworkx.digraph_find_cycle(self.graph, 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_find_cycle.py:60*

### test_find_cycle_multiple_roots_same_cycles

**Category**: instantiation  
**Description**: Instantiate digraph_find_cycle: test find cycle multiple roots same cycles  
**Expected**: self.assertEqual(res, [])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.graph.add_nodes_from(list(range(10)))
self.graph.add_edges_from_no_data([(0, 1), (3, 0), (0, 5), (8, 0), (1, 2), (1, 6), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9)])

res = rustworkx.digraph_find_cycle(self.graph, 5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_find_cycle.py:62*

### test_num_shortest_path_unweighted

**Category**: instantiation  
**Description**: Instantiate add_node: test num shortest path unweighted  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_a = graph.add_node(0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_num_shortest_path.py:21*

### test_num_shortest_path_unweighted

**Category**: instantiation  
**Description**: Instantiate add_node: test num shortest path unweighted  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_b = graph.add_node('end')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_num_shortest_path.py:22*

### test_num_shortest_path_unweighted

**Category**: instantiation  
**Description**: Instantiate digraph_num_shortest_paths_unweighted: test num shortest path unweighted  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.digraph_num_shortest_paths_unweighted(graph, node_a)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_num_shortest_path.py:26*

### test_num_shortest_path_unweighted

**Category**: instantiation  
**Description**: Instantiate add_child: test num shortest path unweighted  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node = graph.add_child(node_a, i, None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_num_shortest_path.py:24*

### test_parallel_paths

**Category**: instantiation  
**Description**: Instantiate num_shortest_paths_unweighted: test parallel paths  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.num_shortest_paths_unweighted(graph, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_num_shortest_path.py:42*

### test_grid_graph

**Category**: instantiation  
**Description**: Instantiate directed_grid_graph: Test num shortest paths for a 5x5 grid graph
0 -> 1 -> 2 -> 3 -> 4
|    |    |    |    |
v    v    v    v    v
5 -> 6 -> 7 -> 8 -> 9
|    |    |    |    |
v    v    v    v    v
10-> 11-> 12-> 13-> 14
|    |    |    |    |
v    v    v    v    v
15-> 16-> 17-> 18-> 19
|    |    |    |    |
v    v    v    v    v
20-> 21-> 22-> 23-> 24  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_grid_graph(5, 5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_num_shortest_path.py:68*

### test_isolates

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates  
**Expected**: self.assertEqual(res, [2, 3])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isolates.py:23*

### test_isolates_with_holes

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates with holes  
**Expected**: self.assertEqual(res, [3])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isolates.py:31*

### test_isolates_empty_graph

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates empty graph  
**Expected**: self.assertEqual(res, [])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isolates.py:36*

### test_isolates

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates  
**Expected**: self.assertEqual(res, [2, 3])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isolates.py:23*

### test_isolates_with_holes

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates with holes  
**Expected**: self.assertEqual(res, [3])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isolates.py:31*

### test_isolates_empty_graph

**Category**: instantiation  
**Description**: Instantiate isolates: test isolates empty graph  
**Expected**: self.assertEqual(res, [])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.isolates(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_isolates.py:36*

### test_is_bipartite

**Category**: instantiation  
**Description**: Instantiate heavy_square_graph: test is bipartite  
**Expected**: self.assertTrue(rustworkx.is_bipartite(graph))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.heavy_square_graph(5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bipartite.py:20*

### test_two_colors

**Category**: instantiation  
**Description**: Instantiate star_graph: test two colors  
**Expected**: self.assertEqual(rustworkx.two_color(graph), {0: 1, 1: 0, 2: 0, 3: 0, 4: 0})  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.star_graph(5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bipartite.py:24*

### test_metric_closure

**Category**: instantiation  
**Description**: Instantiate metric_closure: test metric closure  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph(multigraph=False)
self.graph.add_node(None)
self.graph.extend_from_weighted_edge_list([(1, 2, 10), (2, 3, 10), (3, 4, 10), (4, 5, 10), (5, 6, 10), (2, 7, 1), (7, 5, 1)])
self.graph.remove_node(0)

closure_graph = rustworkx.metric_closure(self.graph, weight_fn=float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_steiner_tree.py:37*

### test_metric_closure

**Category**: instantiation  
**Description**: Instantiate list: test metric closure  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph(multigraph=False)
self.graph.add_node(None)
self.graph.extend_from_weighted_edge_list([(1, 2, 10), (2, 3, 10), (3, 4, 10), (4, 5, 10), (5, 6, 10), (2, 7, 1), (7, 5, 1)])
self.graph.remove_node(0)

edges = list(closure_graph.weighted_edge_list())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_steiner_tree.py:61*

### test_metric_closure_empty_graph

**Category**: instantiation  
**Description**: Instantiate metric_closure: test metric closure empty graph  
**Expected**: self.assertEqual([], closure.weighted_edge_list())  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph(multigraph=False)
self.graph.add_node(None)
self.graph.extend_from_weighted_edge_list([(1, 2, 10), (2, 3, 10), (3, 4, 10), (4, 5, 10), (5, 6, 10), (2, 7, 1), (7, 5, 1)])
self.graph.remove_node(0)

closure = rustworkx.metric_closure(graph, weight_fn=float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_steiner_tree.py:112*

### test_steiner_graph

**Category**: instantiation  
**Description**: Instantiate steiner_tree: test steiner graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph(multigraph=False)
self.graph.add_node(None)
self.graph.extend_from_weighted_edge_list([(1, 2, 10), (2, 3, 10), (3, 4, 10), (4, 5, 10), (5, 6, 10), (2, 7, 1), (7, 5, 1)])
self.graph.remove_node(0)

steiner_tree = rustworkx.steiner_tree(self.graph, [1, 2, 3, 4, 5], weight_fn=float)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_steiner_tree.py:116*

### test_zero_degree_early_stop

**Category**: instantiation  
**Description**: Instantiate generate_random_path: test zero degree early stop  
**Expected**: self.assertEqual(res, [0, 1])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rx.generate_random_path(graph, 0, 10, None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_random_walk.py:29*

### test_zero_degree_early_stop

**Category**: instantiation  
**Description**: Instantiate generate_random_path: test zero degree early stop  
**Expected**: self.assertEqual(res, [0, 1])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rx.generate_random_path(graph, 0, 10, None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_random_walk.py:29*

### test_is_maximum_bisimulation

**Category**: instantiation  
**Description**: Instantiate digraph_maximum_bisimulation: test is maximum bisimulation  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
graphs = []
reference_solution = []
graphs.append(rustworkx.PyDiGraph())
graphs[0].add_nodes_from(list(range(5)))
graphs[0].add_edges_from_no_data([(0, 1), (0, 2), (0, 3), (1, 2)])
reference_solution.append({(1,), (2, 3, 4), (0,)})
graphs.append(rustworkx.PyDiGraph())
graphs[1].add_nodes_from(list(range(5)))
graphs[1].add_edges_from([(0, 1, 'C'), (0, 2, 'D'), (0, 3, 'B'), (1, 2, 'G')])
reference_solution.append({(1,), (2, 3, 4), (0,)})
graphs.append(rustworkx.PyDiGraph())
graphs[2].add_nodes_from(list(range(4)))
graphs[2].add_edges_from_no_data([(0, 0), (1, 1), (2, 2), (3, 3)])
reference_solution.append({(0, 1, 2, 3)})
graphs.append(rustworkx.PyDiGraph())
graphs[3].add_nodes_from(list(range(8)))
graphs[3].add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7)])
reference_solution.append({(0, 4), (3, 7), (2, 6), (1, 5)})
graphs.append(rustworkx.PyDiGraph())
graphs[4].add_nodes_from(list(range(12)))
graphs[4].add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7), (8, 9), (9, 10), (10, 11)])
reference_solution.append({(0, 4, 8), (3, 7, 11), (2, 6, 10), (1, 5, 9)})
graphs.append(rustworkx.PyDiGraph())
graphs[5].add_nodes_from(list(range(12)))
graphs[5].add_edges_from_no_data([(0, 1), (0, 7), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7), (8, 9), (9, 10), (10, 11), (11, 5)])
reference_solution.append({(8,), (3, 7), (2, 6), (1, 5), (0,), (4, 11), (10,), (9,)})
self.graphs = graphs
self.reference_solution = reference_solution

res = rustworkx.digraph_maximum_bisimulation(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bisimulation.py:21*

### test_empty_graph

**Category**: instantiation  
**Description**: Instantiate digraph_maximum_bisimulation: test empty graph  
**Expected**: self.assertEqual(res, [])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
graphs = []
reference_solution = []
graphs.append(rustworkx.PyDiGraph())
graphs[0].add_nodes_from(list(range(5)))
graphs[0].add_edges_from_no_data([(0, 1), (0, 2), (0, 3), (1, 2)])
reference_solution.append({(1,), (2, 3, 4), (0,)})
graphs.append(rustworkx.PyDiGraph())
graphs[1].add_nodes_from(list(range(5)))
graphs[1].add_edges_from([(0, 1, 'C'), (0, 2, 'D'), (0, 3, 'B'), (1, 2, 'G')])
reference_solution.append({(1,), (2, 3, 4), (0,)})
graphs.append(rustworkx.PyDiGraph())
graphs[2].add_nodes_from(list(range(4)))
graphs[2].add_edges_from_no_data([(0, 0), (1, 1), (2, 2), (3, 3)])
reference_solution.append({(0, 1, 2, 3)})
graphs.append(rustworkx.PyDiGraph())
graphs[3].add_nodes_from(list(range(8)))
graphs[3].add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7)])
reference_solution.append({(0, 4), (3, 7), (2, 6), (1, 5)})
graphs.append(rustworkx.PyDiGraph())
graphs[4].add_nodes_from(list(range(12)))
graphs[4].add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7), (8, 9), (9, 10), (10, 11)])
reference_solution.append({(0, 4, 8), (3, 7, 11), (2, 6, 10), (1, 5, 9)})
graphs.append(rustworkx.PyDiGraph())
graphs[5].add_nodes_from(list(range(12)))
graphs[5].add_edges_from_no_data([(0, 1), (0, 7), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7), (8, 9), (9, 10), (10, 11), (11, 5)])
reference_solution.append({(8,), (3, 7), (2, 6), (1, 5), (0,), (4, 11), (10,), (9,)})
self.graphs = graphs
self.reference_solution = reference_solution

res = rustworkx.digraph_maximum_bisimulation(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bisimulation.py:34*

### test_multigraph_compatibility

**Category**: instantiation  
**Description**: Instantiate digraph_maximum_bisimulation: test multigraph compatibility  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
graphs = []
reference_solution = []
graphs.append(rustworkx.PyDiGraph())
graphs[0].add_nodes_from(list(range(5)))
graphs[0].add_edges_from_no_data([(0, 1), (0, 2), (0, 3), (1, 2)])
reference_solution.append({(1,), (2, 3, 4), (0,)})
graphs.append(rustworkx.PyDiGraph())
graphs[1].add_nodes_from(list(range(5)))
graphs[1].add_edges_from([(0, 1, 'C'), (0, 2, 'D'), (0, 3, 'B'), (1, 2, 'G')])
reference_solution.append({(1,), (2, 3, 4), (0,)})
graphs.append(rustworkx.PyDiGraph())
graphs[2].add_nodes_from(list(range(4)))
graphs[2].add_edges_from_no_data([(0, 0), (1, 1), (2, 2), (3, 3)])
reference_solution.append({(0, 1, 2, 3)})
graphs.append(rustworkx.PyDiGraph())
graphs[3].add_nodes_from(list(range(8)))
graphs[3].add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7)])
reference_solution.append({(0, 4), (3, 7), (2, 6), (1, 5)})
graphs.append(rustworkx.PyDiGraph())
graphs[4].add_nodes_from(list(range(12)))
graphs[4].add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7), (8, 9), (9, 10), (10, 11)])
reference_solution.append({(0, 4, 8), (3, 7, 11), (2, 6, 10), (1, 5, 9)})
graphs.append(rustworkx.PyDiGraph())
graphs[5].add_nodes_from(list(range(12)))
graphs[5].add_edges_from_no_data([(0, 1), (0, 7), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7), (8, 9), (9, 10), (10, 11), (11, 5)])
reference_solution.append({(8,), (3, 7), (2, 6), (1, 5), (0,), (4, 11), (10,), (9,)})
self.graphs = graphs
self.reference_solution = reference_solution

result = rustworkx.digraph_maximum_bisimulation(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bisimulation.py:59*

### test_is_maximum_bisimulation

**Category**: instantiation  
**Description**: Instantiate digraph_maximum_bisimulation: test is maximum bisimulation  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.digraph_maximum_bisimulation(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bisimulation.py:21*

### test_empty_graph

**Category**: instantiation  
**Description**: Instantiate digraph_maximum_bisimulation: test empty graph  
**Expected**: self.assertEqual(res, [])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.digraph_maximum_bisimulation(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bisimulation.py:34*

### test_multigraph_compatibility

**Category**: instantiation  
**Description**: Instantiate digraph_maximum_bisimulation: test multigraph compatibility  
**Confidence**: 0.80  
**Tags**: unittest  

```python
result = rustworkx.digraph_maximum_bisimulation(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_bisimulation.py:59*

### test_distance_matrix

**Category**: instantiation  
**Description**: Instantiate distance_matrix: test distance matrix  
**Expected**: self.assertIsInstance(res, numpy.ndarray)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
if self.class_type == 'PyGraph':
    self.graph = rustworkx.undirected_gnp_random_graph(10, 0.5, seed=42)
else:
    self.graph = rustworkx.directed_gnp_random_graph(10, 0.5, seed=42)

res = rustworkx.distance_matrix(self.graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_dispatch.py:30*

### test_distance_matrix_as_undirected

**Category**: instantiation  
**Description**: Instantiate distance_matrix: test distance matrix as undirected  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
if self.class_type == 'PyGraph':
    self.graph = rustworkx.undirected_gnp_random_graph(10, 0.5, seed=42)
else:
    self.graph = rustworkx.directed_gnp_random_graph(10, 0.5, seed=42)

res = rustworkx.distance_matrix(self.graph, as_undirected=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_dispatch.py:38*

### test_adjacency_matrix

**Category**: instantiation  
**Description**: Instantiate adjacency_matrix: test adjacency matrix  
**Expected**: self.assertIsInstance(res, numpy.ndarray)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
if self.class_type == 'PyGraph':
    self.graph = rustworkx.undirected_gnp_random_graph(10, 0.5, seed=42)
else:
    self.graph = rustworkx.directed_gnp_random_graph(10, 0.5, seed=42)

res = rustworkx.adjacency_matrix(self.graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_dispatch.py:42*

### test_all_simple_paths

**Category**: instantiation  
**Description**: Instantiate all_simple_paths: test all simple paths  
**Expected**: self.assertIsInstance(res, list)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
if self.class_type == 'PyGraph':
    self.graph = rustworkx.undirected_gnp_random_graph(10, 0.5, seed=42)
else:
    self.graph = rustworkx.directed_gnp_random_graph(10, 0.5, seed=42)

res = rustworkx.all_simple_paths(self.graph, 0, 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_dispatch.py:46*

### test_floyd_warshall

**Category**: instantiation  
**Description**: Instantiate floyd_warshall: test floyd warshall  
**Expected**: self.assertIsInstance(res, rustworkx.AllPairsPathLengthMapping)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
if self.class_type == 'PyGraph':
    self.graph = rustworkx.undirected_gnp_random_graph(10, 0.5, seed=42)
else:
    self.graph = rustworkx.directed_gnp_random_graph(10, 0.5, seed=42)

res = rustworkx.floyd_warshall(self.graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_dispatch.py:50*

### test_floyd_warshall_numpy

**Category**: instantiation  
**Description**: Instantiate floyd_warshall_numpy: test floyd warshall numpy  
**Expected**: self.assertIsInstance(res, numpy.ndarray)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
if self.class_type == 'PyGraph':
    self.graph = rustworkx.undirected_gnp_random_graph(10, 0.5, seed=42)
else:
    self.graph = rustworkx.directed_gnp_random_graph(10, 0.5, seed=42)

res = rustworkx.floyd_warshall_numpy(self.graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_dispatch.py:54*

### test_floyd_warshall_numpy

**Category**: instantiation  
**Description**: Instantiate graph_floyd_warshall_numpy: test floyd warshall numpy  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
if self.class_type == 'PyGraph':
    self.graph = rustworkx.undirected_gnp_random_graph(10, 0.5, seed=42)
else:
    self.graph = rustworkx.directed_gnp_random_graph(10, 0.5, seed=42)

expected_res = rustworkx.graph_floyd_warshall_numpy(self.graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_dispatch.py:58*

### test_floyd_warshall_numpy

**Category**: instantiation  
**Description**: Instantiate digraph_floyd_warshall_numpy: test floyd warshall numpy  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
if self.class_type == 'PyGraph':
    self.graph = rustworkx.undirected_gnp_random_graph(10, 0.5, seed=42)
else:
    self.graph = rustworkx.directed_gnp_random_graph(10, 0.5, seed=42)

expected_res = rustworkx.digraph_floyd_warshall_numpy(self.graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_dispatch.py:60*

### test_astar_shortest_path

**Category**: instantiation  
**Description**: Instantiate astar_shortest_path: test astar shortest path  
**Expected**: self.assertIsInstance(list(res), list)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
if self.class_type == 'PyGraph':
    self.graph = rustworkx.undirected_gnp_random_graph(10, 0.5, seed=42)
else:
    self.graph = rustworkx.directed_gnp_random_graph(10, 0.5, seed=42)

res = rustworkx.astar_shortest_path(self.graph, 0, lambda _: True, lambda _: 1, lambda _: 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_dispatch.py:65*

### test_dijkstra_shortest_paths

**Category**: instantiation  
**Description**: Instantiate dijkstra_shortest_paths: test dijkstra shortest paths  
**Expected**: self.assertIsInstance(res, rustworkx.PathMapping)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
if self.class_type == 'PyGraph':
    self.graph = rustworkx.undirected_gnp_random_graph(10, 0.5, seed=42)
else:
    self.graph = rustworkx.directed_gnp_random_graph(10, 0.5, seed=42)

res = rustworkx.dijkstra_shortest_paths(self.graph, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_dispatch.py:69*

### test_min_cut_empty_graph

**Category**: instantiation  
**Description**: Instantiate stoer_wagner_min_cut: test min cut empty graph  
**Expected**: self.assertEqual(res, None)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.stoer_wagner_min_cut(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_min_cut.py:22*

### test_min_cut_graph_single_node

**Category**: instantiation  
**Description**: Instantiate stoer_wagner_min_cut: test min cut graph single node  
**Expected**: self.assertEqual(res, None)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.stoer_wagner_min_cut(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_min_cut.py:28*

### test_min_cut_graph_single_edge

**Category**: instantiation  
**Description**: Instantiate stoer_wagner_min_cut: test min cut graph single edge  
**Expected**: self.assertEqual(value, 10.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
value, partition = rustworkx.stoer_wagner_min_cut(graph, lambda x: x)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_min_cut.py:34*

### test_min_cut_graph_parallel_edge

**Category**: instantiation  
**Description**: Instantiate stoer_wagner_min_cut: test min cut graph parallel edge  
**Expected**: self.assertEqual(value, 10.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
value, partition = rustworkx.stoer_wagner_min_cut(graph, lambda x: x)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_min_cut.py:41*

### test_draw_no_args

**Category**: instantiation  
**Description**: Instantiate star_graph: test draw no args  
**Expected**: self.assertIsInstance(image, PIL.Image.Image)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.star_graph(24)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_graphviz.py:44*

### test_draw_no_args

**Category**: instantiation  
**Description**: Instantiate graphviz_draw: test draw no args  
**Expected**: self.assertIsInstance(image, PIL.Image.Image)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
image = graphviz_draw(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\visualization\test_graphviz.py:45*

### test_random_layout

**Category**: instantiation  
**Description**: Instantiate digraph_random_layout: test random layout  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.directed_path_graph(10)

res = rustworkx.digraph_random_layout(self.graph, seed=42)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layout.py:37*

### test_random_layout_center

**Category**: instantiation  
**Description**: Instantiate digraph_random_layout: test random layout center  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.directed_path_graph(10)

res = rustworkx.digraph_random_layout(self.graph, center=(0.5, 0.5), seed=42)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layout.py:53*

### test_random_layout_no_seed

**Category**: instantiation  
**Description**: Instantiate digraph_random_layout: test random layout no seed  
**Expected**: self.assertIsInstance(res, rustworkx.Pos2DMapping)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.directed_path_graph(10)

res = rustworkx.digraph_random_layout(self.graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layout.py:69*

### test_bipartite_layout_empty

**Category**: instantiation  
**Description**: Instantiate bipartite_layout: test bipartite layout empty  
**Expected**: self.assertEqual({}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.directed_path_graph(10)

res = rustworkx.bipartite_layout(rustworkx.PyDiGraph(), set())
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_layout.py:82*

### test_tr1

**Category**: instantiation  
**Description**: Instantiate add_node: test tr1  
**Expected**: self.assertCountEqual(list(tr.edge_list()), [(0, 2), (0, 1), (1, 3), (2, 3), (3, 4)])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
a = graph.add_node('a')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitive_reduction.py:21*

### test_tr1

**Category**: instantiation  
**Description**: Instantiate add_node: test tr1  
**Expected**: self.assertCountEqual(list(tr.edge_list()), [(0, 2), (0, 1), (1, 3), (2, 3), (3, 4)])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
b = graph.add_node('b')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_transitive_reduction.py:22*

### test_digraph_disconnected_dfs_edges

**Category**: instantiation  
**Description**: Instantiate digraph_dfs_edges: test digraph disconnected dfs edges  
**Expected**: self.assertEqual(expected, edges)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
edges = rustworkx.digraph_dfs_edges(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_edges.py:22*

### test_digraph_dfs_edges

**Category**: instantiation  
**Description**: Instantiate digraph_dfs_edges: test digraph dfs edges  
**Expected**: self.assertEqual(expected, edges)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
edges = rustworkx.digraph_dfs_edges(graph, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_edges.py:29*

### test_digraph_dfs_edges_empty

**Category**: instantiation  
**Description**: Instantiate digraph_dfs_edges: test digraph dfs edges empty  
**Expected**: self.assertEqual([], edges)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
edges = rustworkx.digraph_dfs_edges(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_edges.py:35*

### test_digraph_dfs_edges_single_node

**Category**: instantiation  
**Description**: Instantiate directed_empty_graph: test digraph dfs edges single node  
**Expected**: self.assertEqual([], edges)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_empty_graph(1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_edges.py:39*

### test_digraph_dfs_edges_single_node

**Category**: instantiation  
**Description**: Instantiate digraph_dfs_edges: test digraph dfs edges single node  
**Expected**: self.assertEqual([], edges)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
edges = rustworkx.digraph_dfs_edges(graph, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_edges.py:40*

### test_digraph_dfs_edges_node_gaps

**Category**: instantiation  
**Description**: Instantiate digraph_dfs_edges: test digraph dfs edges node gaps  
**Expected**: self.assertEqual([(0, 2), (2, 4)], edges)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
edges = rustworkx.digraph_dfs_edges(graph, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_edges.py:50*

### test_digraph_dfs_edges_star

**Category**: instantiation  
**Description**: Instantiate directed_star_graph: test digraph dfs edges star  
**Expected**: self.assertEqual(len(edges), 100)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_star_graph(101)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_edges.py:54*

### test_digraph_dfs_edges_star

**Category**: instantiation  
**Description**: Instantiate list: test digraph dfs edges star  
**Expected**: self.assertEqual(len(edges), 100)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
spokes = list(range(1, 101))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dfs_edges.py:56*

### test_null_graph

**Category**: instantiation  
**Description**: Instantiate complement: test null graph  
**Expected**: self.assertEqual(0, len(complement_graph.nodes()))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
complement_graph = rustworkx.complement(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_complement.py:21*

### test_clique_directed

**Category**: instantiation  
**Description**: Instantiate complement: test clique directed  
**Expected**: self.assertEqual(graph.nodes(), complement_graph.nodes())  
**Confidence**: 0.80  
**Tags**: unittest  

```python
complement_graph = rustworkx.complement(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_complement.py:30*

### test_undirected_empty

**Category**: instantiation  
**Description**: Instantiate core_number: test undirected empty  
**Expected**: self.assertIsInstance(res, dict)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.example_edges = [(0, 2), (0, 3), (0, 5), (1, 4), (1, 6), (1, 7), (2, 3), (3, 5), (2, 5), (5, 6), (4, 6), (4, 7), (6, 7), (5, 8), (6, 8), (6, 9), (8, 9), (0, 10), (1, 10), (1, 11), (10, 11), (12, 13), (13, 15), (14, 15), (12, 14), (8, 19), (11, 16), (11, 17), (12, 18)]
example_core = {}
for i in range(8):
    example_core[i] = 3
for i in range(8, 16):
    example_core[i] = 2
for i in range(16, 20):
    example_core[i] = 1
example_core[20] = 0
self.example_core = example_core

res = rustworkx.core_number(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_core_number.py:71*

### test_undirected_all_0

**Category**: instantiation  
**Description**: Instantiate core_number: test undirected all 0  
**Expected**: self.assertIsInstance(res, dict)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.example_edges = [(0, 2), (0, 3), (0, 5), (1, 4), (1, 6), (1, 7), (2, 3), (3, 5), (2, 5), (5, 6), (4, 6), (4, 7), (6, 7), (5, 8), (6, 8), (6, 9), (8, 9), (0, 10), (1, 10), (1, 11), (10, 11), (12, 13), (13, 15), (14, 15), (12, 14), (8, 19), (11, 16), (11, 17), (12, 18)]
example_core = {}
for i in range(8):
    example_core[i] = 3
for i in range(8, 16):
    example_core[i] = 2
for i in range(16, 20):
    example_core[i] = 1
example_core[20] = 0
self.example_core = example_core

res = rustworkx.core_number(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_core_number.py:78*

### test_simple_path

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test simple path  
**Expected**: self.assertEqual(layers, [[0], [1], [2], [3], [4]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(5)

layers = rustworkx.bfs_layers(self.graph, [0])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_layer.py:10*

### test_multiple_sources

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test multiple sources  
**Expected**: self.assertEqual(layers, [[0, 4], [1, 3], [2]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(5)

layers = rustworkx.bfs_layers(self.graph, [0, 4])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_layer.py:14*

### test_disconnected_graph

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test disconnected graph  
**Expected**: self.assertEqual(layers, [[0], [1]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(5)

layers = rustworkx.bfs_layers(g, [0])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_layer.py:20*

### test_no_sources_default_all_nodes

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test no sources default all nodes  
**Expected**: self.assertTrue(all((isinstance(layer, list) for layer in layers)))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.generators.path_graph(5)

layers = rustworkx.bfs_layers(self.graph, None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_layer.py:24*

### test_simple_path

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test simple path  
**Expected**: self.assertEqual(layers, [[0], [1], [2], [3], [4]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
layers = rustworkx.bfs_layers(self.graph, [0])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_layer.py:10*

### test_multiple_sources

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test multiple sources  
**Expected**: self.assertEqual(layers, [[0, 4], [1, 3], [2]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
layers = rustworkx.bfs_layers(self.graph, [0, 4])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_layer.py:14*

### test_disconnected_graph

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test disconnected graph  
**Expected**: self.assertEqual(layers, [[0], [1]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
layers = rustworkx.bfs_layers(g, [0])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_layer.py:20*

### test_no_sources_default_all_nodes

**Category**: instantiation  
**Description**: Instantiate bfs_layers: test no sources default all nodes  
**Expected**: self.assertTrue(all((isinstance(layer, list) for layer in layers)))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
layers = rustworkx.bfs_layers(self.graph, None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_bfs_layer.py:24*

### test_ancestors

**Category**: instantiation  
**Description**: Instantiate add_node: test ancestors  
**Expected**: self.assertEqual({node_a, node_b}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_a = dag.add_node('a')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_ancestors_descendants.py:21*

### test_ancestors

**Category**: instantiation  
**Description**: Instantiate add_child: test ancestors  
**Expected**: self.assertEqual({node_a, node_b}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_b = dag.add_child(node_a, 'b', {'a': 1})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_ancestors_descendants.py:22*

### test_simple_cycles

**Category**: instantiation  
**Description**: Instantiate list: test simple cycles  
**Expected**: self.assertEqual(len(res), len(expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = list(rustworkx.simple_cycles(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_simple_cycles.py:24*

### test_mesh_graph

**Category**: instantiation  
**Description**: Instantiate directed_mesh_graph: test mesh graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_mesh_graph(n)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_simple_cycles.py:39*

### test_mesh_graph

**Category**: instantiation  
**Description**: Instantiate list: test mesh graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = list(rustworkx.simple_cycles(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_simple_cycles.py:40*

### test_figure_1

**Category**: instantiation  
**Description**: Instantiate list: test figure 1  
**Confidence**: 0.80  
**Tags**: unittest  

```python
cycles = list(rustworkx.simple_cycles(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_simple_cycles.py:68*

### test_simple_cycles

**Category**: instantiation  
**Description**: Instantiate list: test simple cycles  
**Expected**: self.assertEqual(len(res), len(expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = list(rustworkx.simple_cycles(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_simple_cycles.py:24*

### test_mesh_graph

**Category**: instantiation  
**Description**: Instantiate directed_mesh_graph: test mesh graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_mesh_graph(n)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_simple_cycles.py:39*

### test_mesh_graph

**Category**: instantiation  
**Description**: Instantiate list: test mesh graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = list(rustworkx.simple_cycles(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_simple_cycles.py:40*

### test_figure_1

**Category**: instantiation  
**Description**: Instantiate list: test figure 1  
**Confidence**: 0.80  
**Tags**: unittest  

```python
cycles = list(rustworkx.simple_cycles(graph))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_simple_cycles.py:68*

### test_dorogovtsev_goltsev_mendes_graph

**Category**: instantiation  
**Description**: Instantiate dorogovtsev_goltsev_mendes_graph: test dorogovtsev goltsev mendes graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.dorogovtsev_goltsev_mendes_graph(n)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_dorogovtsev_goltsev_mendes.py:22*

### test_dorogovtsev_goltsev_mendes_graph

**Category**: instantiation  
**Description**: Instantiate dorogovtsev_goltsev_mendes_graph: test dorogovtsev goltsev mendes graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.dorogovtsev_goltsev_mendes_graph(n)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_dorogovtsev_goltsev_mendes.py:22*

### test_digraph_distance_matrix

**Category**: instantiation  
**Description**: Instantiate digraph_distance_matrix: test digraph distance matrix  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
dist = rustworkx.digraph_distance_matrix(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dist_matrix.py:25*

### test_digraph_distance_matrix

**Category**: instantiation  
**Description**: Instantiate array: test digraph distance matrix  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
expected = np.array([[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 1.0], [0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0], [0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0], [0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0], [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dist_matrix.py:26*

### test_digraph_distance_matrix_parallel

**Category**: instantiation  
**Description**: Instantiate digraph_distance_matrix: test digraph distance matrix parallel  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
dist = rustworkx.digraph_distance_matrix(graph, parallel_threshold=5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dist_matrix.py:43*

### test_digraph_distance_matrix_parallel

**Category**: instantiation  
**Description**: Instantiate array: test digraph distance matrix parallel  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
expected = np.array([[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 1.0], [0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0], [0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0], [0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0], [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dist_matrix.py:44*

### test_digraph_distance_matrix_as_undirected

**Category**: instantiation  
**Description**: Instantiate digraph_distance_matrix: test digraph distance matrix as undirected  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
dist = rustworkx.digraph_distance_matrix(graph, as_undirected=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dist_matrix.py:61*

### test_digraph_distance_matrix_as_undirected

**Category**: instantiation  
**Description**: Instantiate array: test digraph distance matrix as undirected  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
expected = np.array([[0.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0], [1.0, 0.0, 1.0, 2.0, 3.0, 3.0, 2.0], [2.0, 1.0, 0.0, 1.0, 2.0, 3.0, 3.0], [3.0, 2.0, 1.0, 0.0, 1.0, 2.0, 3.0], [3.0, 3.0, 2.0, 1.0, 0.0, 1.0, 2.0], [2.0, 3.0, 3.0, 2.0, 1.0, 0.0, 1.0], [1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 0.0]])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dist_matrix.py:62*

### test_digraph_distance_matrix_parallel_as_undirected

**Category**: instantiation  
**Description**: Instantiate digraph_distance_matrix: test digraph distance matrix parallel as undirected  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
dist = rustworkx.digraph_distance_matrix(graph, parallel_threshold=5, as_undirected=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dist_matrix.py:79*

### test_digraph_distance_matrix_parallel_as_undirected

**Category**: instantiation  
**Description**: Instantiate array: test digraph distance matrix parallel as undirected  
**Expected**: self.assertTrue(np.array_equal(dist, expected))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
expected = np.array([[0.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0], [1.0, 0.0, 1.0, 2.0, 3.0, 3.0, 2.0], [2.0, 1.0, 0.0, 1.0, 2.0, 3.0, 3.0], [3.0, 2.0, 1.0, 0.0, 1.0, 2.0, 3.0], [3.0, 3.0, 2.0, 1.0, 0.0, 1.0, 2.0], [2.0, 3.0, 3.0, 2.0, 1.0, 0.0, 1.0], [1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 0.0]])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dist_matrix.py:80*

### test_digraph_distance_matrix_non_zero_null

**Category**: instantiation  
**Description**: Instantiate distance_matrix: test digraph distance matrix non zero null  
**Expected**: self.assertTrue(np.array_equal(dist, expected, equal_nan=True))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
dist = rustworkx.distance_matrix(graph, as_undirected=True, null_value=np.nan)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dist_matrix.py:98*

### test_digraph_distance_matrix_non_zero_null

**Category**: instantiation  
**Description**: Instantiate array: test digraph distance matrix non zero null  
**Expected**: self.assertTrue(np.array_equal(dist, expected, equal_nan=True))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
expected = np.array([[0.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, np.nan], [1.0, 0.0, 1.0, 2.0, 3.0, 3.0, 2.0, np.nan], [2.0, 1.0, 0.0, 1.0, 2.0, 3.0, 3.0, np.nan], [3.0, 2.0, 1.0, 0.0, 1.0, 2.0, 3.0, np.nan], [3.0, 3.0, 2.0, 1.0, 0.0, 1.0, 2.0, np.nan], [2.0, 3.0, 3.0, 2.0, 1.0, 0.0, 1.0, np.nan], [1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 0.0, np.nan], [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 0.0]])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dist_matrix.py:99*

### test_single_neighbor

**Category**: instantiation  
**Description**: Instantiate add_node: test single neighbor  
**Expected**: self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_a = graph.add_node('a')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adj.py:21*

### test_single_neighbor

**Category**: instantiation  
**Description**: Instantiate add_node: test single neighbor  
**Expected**: self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_b = graph.add_node('b')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adj.py:22*

### test_single_neighbor

**Category**: instantiation  
**Description**: Instantiate add_node: test single neighbor  
**Expected**: self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_c = graph.add_node('c')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adj.py:24*

### test_single_neighbor

**Category**: instantiation  
**Description**: Instantiate adj: test single neighbor  
**Expected**: self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = graph.adj(node_a)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adj.py:26*

### test_no_neighbor

**Category**: instantiation  
**Description**: Instantiate add_node: test no neighbor  
**Expected**: self.assertEqual({}, graph.adj(node_a))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_a = graph.add_node('a')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adj.py:31*

### test_single_neighbor

**Category**: instantiation  
**Description**: Instantiate add_node: test single neighbor  
**Expected**: self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_a = graph.add_node('a')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adj.py:21*

### test_single_neighbor

**Category**: instantiation  
**Description**: Instantiate add_node: test single neighbor  
**Expected**: self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_b = graph.add_node('b')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adj.py:22*

### test_single_neighbor

**Category**: instantiation  
**Description**: Instantiate add_node: test single neighbor  
**Expected**: self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_c = graph.add_node('c')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_adj.py:24*

### test_null_cartesian_null

**Category**: instantiation  
**Description**: Instantiate digraph_cartesian_product: test null cartesian null  
**Expected**: self.assertEqual(len(graph_product.nodes()), 0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph_product, _ = rustworkx.digraph_cartesian_product(graph_1, graph_2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_cartesian_product.py:22*

### test_directed_path_2_cartesian_path_2

**Category**: instantiation  
**Description**: Instantiate directed_path_graph: test directed path 2 cartesian path 2  
**Expected**: self.assertEqual(len(graph_product.nodes()), 4)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph_1 = rustworkx.generators.directed_path_graph(2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_cartesian_product.py:27*

### test_directed_path_2_cartesian_path_2

**Category**: instantiation  
**Description**: Instantiate directed_path_graph: test directed path 2 cartesian path 2  
**Expected**: self.assertEqual(len(graph_product.nodes()), 4)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph_2 = rustworkx.generators.directed_path_graph(2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_cartesian_product.py:28*

### test_directed_path_2_cartesian_path_2

**Category**: instantiation  
**Description**: Instantiate digraph_cartesian_product: test directed path 2 cartesian path 2  
**Expected**: self.assertEqual(len(graph_product.nodes()), 4)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph_product, _ = rustworkx.digraph_cartesian_product(graph_1, graph_2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_cartesian_product.py:30*

### test_simple_example

**Category**: instantiation  
**Description**: Instantiate digraph_unweighted_average_shortest_path_length: test simple example  
**Expected**: self.assertTrue(math.isinf(res), 'Output is not infinity')  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.digraph_unweighted_average_shortest_path_length(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_avg_shortest_path.py:25*

### test_cycle_graph

**Category**: instantiation  
**Description**: Instantiate directed_cycle_graph: test cycle graph  
**Expected**: self.assertAlmostEqual(3.5, res, delta=1e-07)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_cycle_graph(7)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_avg_shortest_path.py:29*

### test_two_colors

**Category**: instantiation  
**Description**: Instantiate add_node: Input:
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
**Expected**: self.assertEqual([['cx', 'cz']], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
cx_gate = dag.add_node('cx')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_bicolor_runs.py:85*

### test_two_colors

**Category**: instantiation  
**Description**: Instantiate add_node: Input:
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
**Expected**: self.assertEqual([['cx', 'cz']], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
cz_gate = dag.add_node('cz')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_bicolor_runs.py:86*

### test_two_colors_with_pending

**Category**: instantiation  
**Description**: Instantiate add_node: Input:
┌─────────────┐
│             │
│    q0       │
│             │
└───┬─────────┘
    | q0
    │
┌───▼─────────┐
│             │
│    h        │
│             │
└───┬─────────┘
    | q0
    │                           ┌─────────────┐
    │                           │             │
    │                           │    q1       │
    │                           │             │
    |                           └──────┬──────┘
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
 │    q0       │                │    y        │
 │             │                │             │
 └─────────────┘                └─────────────┘
                                    | q1
                                    │
                                ┌───▼─────────┐
                                │             │
                                │    q1       │
                                │             │
                                └─────────────┘

Expected: [[h, cx, cz, y]]  
**Expected**: self.assertEqual([['h', 'cx', 'cz', 'y']], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
h_gate = dag.add_node('h')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_bicolor_runs.py:170*

### test_two_colors_with_pending

**Category**: instantiation  
**Description**: Instantiate add_node: Input:
┌─────────────┐
│             │
│    q0       │
│             │
└───┬─────────┘
    | q0
    │
┌───▼─────────┐
│             │
│    h        │
│             │
└───┬─────────┘
    | q0
    │                           ┌─────────────┐
    │                           │             │
    │                           │    q1       │
    │                           │             │
    |                           └──────┬──────┘
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
 │    q0       │                │    y        │
 │             │                │             │
 └─────────────┘                └─────────────┘
                                    | q1
                                    │
                                ┌───▼─────────┐
                                │             │
                                │    q1       │
                                │             │
                                └─────────────┘

Expected: [[h, cx, cz, y]]  
**Expected**: self.assertEqual([['h', 'cx', 'cz', 'y']], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
cx_gate = dag.add_node('cx')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_bicolor_runs.py:171*

### test_two_colors_with_pending

**Category**: instantiation  
**Description**: Instantiate add_node: Input:
┌─────────────┐
│             │
│    q0       │
│             │
└───┬─────────┘
    | q0
    │
┌───▼─────────┐
│             │
│    h        │
│             │
└───┬─────────┘
    | q0
    │                           ┌─────────────┐
    │                           │             │
    │                           │    q1       │
    │                           │             │
    |                           └──────┬──────┘
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
 │    q0       │                │    y        │
 │             │                │             │
 └─────────────┘                └─────────────┘
                                    | q1
                                    │
                                ┌───▼─────────┐
                                │             │
                                │    q1       │
                                │             │
                                └─────────────┘

Expected: [[h, cx, cz, y]]  
**Expected**: self.assertEqual([['h', 'cx', 'cz', 'y']], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
cz_gate = dag.add_node('cz')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_bicolor_runs.py:172*

### test_two_colors_with_pending

**Category**: instantiation  
**Description**: Instantiate add_node: Input:
┌─────────────┐
│             │
│    q0       │
│             │
└───┬─────────┘
    | q0
    │
┌───▼─────────┐
│             │
│    h        │
│             │
└───┬─────────┘
    | q0
    │                           ┌─────────────┐
    │                           │             │
    │                           │    q1       │
    │                           │             │
    |                           └──────┬──────┘
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
 │    q0       │                │    y        │
 │             │                │             │
 └─────────────┘                └─────────────┘
                                    | q1
                                    │
                                ┌───▼─────────┐
                                │             │
                                │    q1       │
                                │             │
                                └─────────────┘

Expected: [[h, cx, cz, y]]  
**Expected**: self.assertEqual([['h', 'cx', 'cz', 'y']], rustworkx.collect_bicolor_runs(dag, filter_function, color_function))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
y_gate = dag.add_node('y')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_collect_bicolor_runs.py:173*

### test_num_shortest_path_unweighted

**Category**: instantiation  
**Description**: Instantiate add_node: test num shortest path unweighted  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_a = graph.add_node(0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_num_shortest_path.py:21*

### test_num_shortest_path_unweighted

**Category**: instantiation  
**Description**: Instantiate add_node: test num shortest path unweighted  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_b = graph.add_node('end')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_num_shortest_path.py:22*

### test_num_shortest_path_unweighted

**Category**: instantiation  
**Description**: Instantiate graph_num_shortest_paths_unweighted: test num shortest path unweighted  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.graph_num_shortest_paths_unweighted(graph, node_a)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_num_shortest_path.py:27*

### test_num_shortest_path_unweighted

**Category**: instantiation  
**Description**: Instantiate add_node: test num shortest path unweighted  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node = graph.add_node(i)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_num_shortest_path.py:24*

### test_parallel_paths

**Category**: instantiation  
**Description**: Instantiate num_shortest_paths_unweighted: test parallel paths  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.num_shortest_paths_unweighted(graph, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_num_shortest_path.py:43*

### test_grid_graph

**Category**: instantiation  
**Description**: Instantiate grid_graph: Test num shortest paths for a 5x5 grid graph
0 - 1 - 2 - 3 - 4
|   |   |   |   |
5 - 6 - 7 - 8 - 9
|   |   |   |   |
10- 11- 12- 13- 14
|   |   |   |   |
15- 16- 17- 18- 19
|   |   |   |   |
20- 21- 22- 23- 24  
**Expected**: self.assertEqual(expected, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.grid_graph(5, 5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_num_shortest_path.py:65*

### test_empty_graph

**Category**: instantiation  
**Description**: Instantiate empty_graph: test empty graph  
**Expected**: self.assertEqual(len(graph), 20)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.empty_graph(20)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_empty.py:20*

### test_empty_directed_graph

**Category**: instantiation  
**Description**: Instantiate directed_empty_graph: test empty directed graph  
**Expected**: self.assertEqual(len(graph), 20)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_empty_graph(20)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_empty.py:25*

### test_empty_graph

**Category**: instantiation  
**Description**: Instantiate empty_graph: test empty graph  
**Expected**: self.assertEqual(len(graph), 20)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.empty_graph(20)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_empty.py:20*

### test_empty_directed_graph

**Category**: instantiation  
**Description**: Instantiate directed_empty_graph: test empty directed graph  
**Expected**: self.assertEqual(len(graph), 20)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_empty_graph(20)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_empty.py:25*

### test_digraph_k_shortest_path_lengths

**Category**: instantiation  
**Description**: Instantiate digraph_k_shortest_path_lengths: test digraph k shortest path lengths  
**Expected**: self.assertEqual(res, expected)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.digraph_k_shortest_path_lengths(graph, 1, 2, lambda _: 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_k_shortest_path.py:35*

### test_digraph_k_shortest_path_lengths_with_goal

**Category**: instantiation  
**Description**: Instantiate digraph_k_shortest_path_lengths: test digraph k shortest path lengths with goal  
**Expected**: self.assertEqual(res, {3: 6})  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.digraph_k_shortest_path_lengths(graph, 1, 2, lambda _: 1, 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_k_shortest_path.py:64*

### test_digraph_k_shortest_path_with_goal_node_hole

**Category**: instantiation  
**Description**: Instantiate directed_path_graph: test digraph k shortest path with goal node hole  
**Expected**: self.assertEqual({3: 2}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_k_shortest_path.py:68*

### test_digraph_k_shortest_path_with_goal_node_hole

**Category**: instantiation  
**Description**: Instantiate digraph_k_shortest_path_lengths: test digraph k shortest path with goal node hole  
**Expected**: self.assertEqual({3: 2}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.digraph_k_shortest_path_lengths(graph, start=1, k=1, edge_cost=lambda _: 1, goal=3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_k_shortest_path.py:70*

### test_digraph_k_shortest_path_with_invalid_weight

**Category**: instantiation  
**Description**: Instantiate directed_path_graph: test digraph k shortest path with invalid weight  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.directed_path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_k_shortest_path.py:76*

### test_k_shortest_path_with_no_path

**Category**: instantiation  
**Description**: Instantiate digraph_k_shortest_path_lengths: test k shortest path with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
path_lengths = rustworkx.digraph_k_shortest_path_lengths(g, start=a, k=1, edge_cost=float, goal=b)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_k_shortest_path.py:92*

### test_digraph_k_shortest_path_lengths

**Category**: instantiation  
**Description**: Instantiate digraph_k_shortest_path_lengths: test digraph k shortest path lengths  
**Expected**: self.assertEqual(res, expected)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.digraph_k_shortest_path_lengths(graph, 1, 2, lambda _: 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_k_shortest_path.py:35*

### test_digraph_k_shortest_path_lengths_with_goal

**Category**: instantiation  
**Description**: Instantiate digraph_k_shortest_path_lengths: test digraph k shortest path lengths with goal  
**Expected**: self.assertEqual(res, {3: 6})  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.digraph_k_shortest_path_lengths(graph, 1, 2, lambda _: 1, 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_k_shortest_path.py:64*

### test_multigraph

**Category**: instantiation  
**Description**: Instantiate PyGraph: test multigraph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.PyGraph(multigraph=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_local_complement.py:20*

### test_multigraph

**Category**: instantiation  
**Description**: Instantiate add_node: test multigraph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node = graph.add_node('')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_local_complement.py:21*

### test_invalid_node

**Category**: instantiation  
**Description**: Instantiate PyGraph: test invalid node  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.PyGraph(multigraph=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_local_complement.py:26*

### test_invalid_node

**Category**: instantiation  
**Description**: Instantiate add_node: test invalid node  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node = graph.add_node('')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_local_complement.py:27*

### test_clique

**Category**: instantiation  
**Description**: Instantiate complete_graph: test clique  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.complete_graph(N, multigraph=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_local_complement.py:33*

### test_clique

**Category**: instantiation  
**Description**: Instantiate PyGraph: test clique  
**Confidence**: 0.80  
**Tags**: unittest  

```python
expected_graph = rustworkx.PyGraph(multigraph=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_local_complement.py:36*

### test_attrs_set_at_init

**Category**: instantiation  
**Description**: Instantiate PyGraph: test attrs set at init  
**Expected**: self.assertEqual({'foo': 'bar'}, graph.attrs)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.PyGraph(attrs=dict(foo='bar'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_attrs.py:24*

### test_attrs_set_at_init_override

**Category**: instantiation  
**Description**: Instantiate PyGraph: test attrs set at init override  
**Expected**: self.assertEqual({'foo': 'bar'}, graph.attrs)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.PyGraph(attrs=dict(foo='bar'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_attrs.py:28*

### test_attrs_set_at_init

**Category**: instantiation  
**Description**: Instantiate PyGraph: test attrs set at init  
**Expected**: self.assertEqual({'foo': 'bar'}, graph.attrs)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.PyGraph(attrs=dict(foo='bar'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_attrs.py:24*

### test_attrs_set_at_init_override

**Category**: instantiation  
**Description**: Instantiate PyGraph: test attrs set at init override  
**Expected**: self.assertEqual({'foo': 'bar'}, graph.attrs)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.PyGraph(attrs=dict(foo='bar'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_graph_attrs.py:28*

### test_astar_null_heuristic

**Category**: instantiation  
**Description**: Instantiate digraph_astar_shortest_path: test astar null heuristic  
**Expected**: self.assertEqual(expected, path)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
path = rustworkx.digraph_astar_shortest_path(g, a, lambda goal: goal == 'E', lambda x: float(x), lambda y: 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_astar.py:36*

### test_astar_manhattan_heuristic

**Category**: instantiation  
**Description**: Instantiate add_node: test astar manhattan heuristic  
**Confidence**: 0.80  
**Tags**: unittest  

```python
a = g.add_node((0.0, 0.0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_astar.py:44*

### test_astar_manhattan_heuristic

**Category**: instantiation  
**Description**: Instantiate add_node: test astar manhattan heuristic  
**Confidence**: 0.80  
**Tags**: unittest  

```python
b = g.add_node((2.0, 0.0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_astar.py:45*

### test_astar_manhattan_heuristic

**Category**: instantiation  
**Description**: Instantiate add_node: test astar manhattan heuristic  
**Confidence**: 0.80  
**Tags**: unittest  

```python
c = g.add_node((1.0, 1.0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_astar.py:46*

### test_astar_manhattan_heuristic

**Category**: instantiation  
**Description**: Instantiate add_node: test astar manhattan heuristic  
**Confidence**: 0.80  
**Tags**: unittest  

```python
d = g.add_node((0.0, 2.0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_astar.py:47*

### test_astar_manhattan_heuristic

**Category**: instantiation  
**Description**: Instantiate add_node: test astar manhattan heuristic  
**Confidence**: 0.80  
**Tags**: unittest  

```python
e = g.add_node((3.0, 3.0))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_astar.py:48*

### test_digraph_to_dot_to_file

**Category**: instantiation  
**Description**: Instantiate to_dot: test digraph to dot to file  
**Expected**: self.assertIsNone(res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

res = graph.to_dot(lambda node: node, lambda edge: edge, filename=self.path)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dot.py:50*

### test_digraph_empty_dicts

**Category**: instantiation  
**Description**: Instantiate directed_gnp_random_graph: test digraph empty dicts  
**Expected**: self.assertEqual('digraph {\n0 ;\n1 ;\n2 ;\n0 -> 1 ;\n0 -> 2 ;\n1 -> 2 ;\n2 -> 0 ;\n2 -> 1 ;\n}\n', dot_str)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

graph = rustworkx.directed_gnp_random_graph(3, 0.9, seed=42)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dot.py:58*

### test_digraph_empty_dicts

**Category**: instantiation  
**Description**: Instantiate to_dot: test digraph empty dicts  
**Expected**: self.assertEqual('digraph {\n0 ;\n1 ;\n2 ;\n0 -> 1 ;\n0 -> 2 ;\n1 -> 2 ;\n2 -> 0 ;\n2 -> 1 ;\n}\n', dot_str)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

dot_str = graph.to_dot(lambda _: {}, lambda _: {})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dot.py:59*

### test_digraph_graph_attrs

**Category**: instantiation  
**Description**: Instantiate directed_gnp_random_graph: test digraph graph attrs  
**Expected**: self.assertEqual('digraph {\nbgcolor=red ;\n0 ;\n1 ;\n2 ;\n0 -> 1 ;\n0 -> 2 ;\n1 -> 2 ;\n2 -> 0 ;\n2 -> 1 ;\n}\n', dot_str)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

graph = rustworkx.directed_gnp_random_graph(3, 0.9, seed=42)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dot.py:66*

### test_digraph_graph_attrs

**Category**: instantiation  
**Description**: Instantiate to_dot: test digraph graph attrs  
**Expected**: self.assertEqual('digraph {\nbgcolor=red ;\n0 ;\n1 ;\n2 ;\n0 -> 1 ;\n0 -> 2 ;\n1 -> 2 ;\n2 -> 0 ;\n2 -> 1 ;\n}\n', dot_str)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

dot_str = graph.to_dot(lambda _: {}, lambda _: {}, {'bgcolor': 'red'})
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dot.py:67*

### test_digraph_no_args

**Category**: instantiation  
**Description**: Instantiate directed_gnp_random_graph: test digraph no args  
**Expected**: self.assertEqual('digraph {\n0 ;\n1 ;\n2 ;\n0 -> 2 ;\n1 -> 2 ;\n1 -> 0 ;\n2 -> 0 ;\n2 -> 1 ;\n}\n', dot_str)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
fd, self.path = tempfile.mkstemp()
os.close(fd)
os.remove(self.path)

graph = rustworkx.directed_gnp_random_graph(3, 0.95, seed=24)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_dot.py:75*

### test_simple_planar_graph

**Category**: instantiation  
**Description**: Instantiate is_planar: test simple planar graph  
**Expected**: self.assertTrue(res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rx.is_planar(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_planar.py:37*

### test_planar_with_selfloop

**Category**: instantiation  
**Description**: Instantiate is_planar: test planar with selfloop  
**Expected**: self.assertTrue(res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rx.is_planar(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_planar.py:59*

### test_grid_graph

**Category**: instantiation  
**Description**: Instantiate grid_graph: test grid graph  
**Expected**: self.assertTrue(res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rx.generators.grid_graph(5, 5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_planar.py:63*

### test_grid_graph

**Category**: instantiation  
**Description**: Instantiate is_planar: test grid graph  
**Expected**: self.assertTrue(res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rx.is_planar(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_planar.py:64*

### test_k3_3

**Category**: instantiation  
**Description**: Instantiate is_planar: test k3 3  
**Expected**: self.assertFalse(res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rx.is_planar(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_planar.py:82*

### test_k5

**Category**: instantiation  
**Description**: Instantiate mesh_graph: test k5  
**Expected**: self.assertFalse(res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rx.generators.mesh_graph(5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_planar.py:86*

### test_k5

**Category**: instantiation  
**Description**: Instantiate is_planar: test k5  
**Expected**: self.assertFalse(res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rx.is_planar(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_planar.py:87*

### test_multiple_components_planar

**Category**: instantiation  
**Description**: Instantiate is_planar: test multiple components planar  
**Expected**: self.assertTrue(res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rx.is_planar(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_planar.py:93*

### test_multiple_components_non_planar

**Category**: instantiation  
**Description**: Instantiate mesh_graph: test multiple components non planar  
**Expected**: self.assertFalse(res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rx.generators.mesh_graph(5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_planar.py:97*

### test_multiple_components_non_planar

**Category**: instantiation  
**Description**: Instantiate is_planar: test multiple components non planar  
**Expected**: self.assertFalse(res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rx.is_planar(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_planar.py:101*

### test_all_simple_paths

**Category**: instantiation  
**Description**: Instantiate digraph_all_simple_paths: test all simple paths  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 5), (5, 2), (5, 3)]

paths = rustworkx.digraph_all_simple_paths(dag, 0, 5)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_all_simple_paths.py:42*

### test_all_simple_paths_default_min_depth

**Category**: instantiation  
**Description**: Instantiate digraph_all_simple_paths: test all simple paths default min depth  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 5), (5, 2), (5, 3)]

paths = rustworkx.digraph_all_simple_paths(dag, 0, 5, min_depth=0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_all_simple_paths.py:61*

### test_all_simple_paths_min_depth

**Category**: instantiation  
**Description**: Instantiate digraph_all_simple_paths: test all simple paths min depth  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 5), (5, 2), (5, 3)]

paths = rustworkx.digraph_all_simple_paths(dag, 0, 5, min_depth=6)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_all_simple_paths.py:80*

### test_all_simple_paths_with_cutoff

**Category**: instantiation  
**Description**: Instantiate digraph_all_simple_paths: test all simple paths with cutoff  
**Expected**: self.assertEqual(len(expected), len(paths))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 5), (5, 2), (5, 3)]

paths = rustworkx.digraph_all_simple_paths(dag, 0, 5, cutoff=4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\digraph\test_all_simple_paths.py:93*

### test_correct_successful_path

**Category**: instantiation  
**Description**: Instantiate hyperbolic_greedy_routing: test correct successful path  
**Expected**: self.assertEqual(path, [0, 1, 2, 3])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
path, dist = rx.hyperbolic_greedy_routing(graph, positions, 0, 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_geometry.py:98*

### test_correct_successful_path

**Category**: instantiation  
**Description**: Instantiate hyperbolic_greedy_routing: test correct successful path  
**Expected**: self.assertEqual(path, [0, 1, 2, 5, 6])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
path, dist = rx.hyperbolic_greedy_routing(graph, positions, 0, 6)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_geometry.py:121*

### test_valid

**Category**: instantiation  
**Description**: Instantiate path_graph: test valid  
**Expected**: self.assertTrue(rustworkx.is_maximal_matching(graph, matching))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matching.py:19*

### test_not_matching

**Category**: instantiation  
**Description**: Instantiate path_graph: test not matching  
**Expected**: self.assertFalse(rustworkx.is_maximal_matching(graph, matching))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matching.py:24*

### test_not_maximal

**Category**: instantiation  
**Description**: Instantiate path_graph: test not maximal  
**Expected**: self.assertFalse(rustworkx.is_maximal_matching(graph, matching))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matching.py:29*

### test_is_matching_empty

**Category**: instantiation  
**Description**: Instantiate path_graph: test is matching empty  
**Expected**: self.assertTrue(rustworkx.is_matching(graph, matching))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matching.py:34*

### test_is_matching_single_edge

**Category**: instantiation  
**Description**: Instantiate path_graph: test is matching single edge  
**Expected**: self.assertTrue(rustworkx.is_matching(graph, matching))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matching.py:39*

### test_is_matching_valid

**Category**: instantiation  
**Description**: Instantiate path_graph: test is matching valid  
**Expected**: self.assertTrue(rustworkx.is_matching(graph, matching))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matching.py:44*

### test_is_matching_invalid

**Category**: instantiation  
**Description**: Instantiate path_graph: test is matching invalid  
**Expected**: self.assertFalse(rustworkx.is_matching(graph, matching))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matching.py:49*

### test_is_matching_invalid_edge

**Category**: instantiation  
**Description**: Instantiate path_graph: test is matching invalid edge  
**Expected**: self.assertFalse(rustworkx.is_matching(graph, matching))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matching.py:54*

### test_valid

**Category**: instantiation  
**Description**: Instantiate path_graph: test valid  
**Expected**: self.assertTrue(rustworkx.is_maximal_matching(graph, matching))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matching.py:19*

### test_not_matching

**Category**: instantiation  
**Description**: Instantiate path_graph: test not matching  
**Expected**: self.assertFalse(rustworkx.is_maximal_matching(graph, matching))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_matching.py:24*

### test_transitivity

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity  
**Expected**: self.assertEqual(res, 3 / 8)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_transitivity.py:23*

### test_transitivity_triangle

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity triangle  
**Expected**: self.assertEqual(res, 1.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_transitivity.py:30*

### test_transitivity_star

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity star  
**Expected**: self.assertEqual(res, 0.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_transitivity.py:37*

### test_transitivity_empty

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity empty  
**Expected**: self.assertEqual(res, 0.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_transitivity.py:42*

### test_transitivity_disconnected

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity disconnected  
**Expected**: self.assertEqual(res, 0.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_transitivity.py:48*

### test_transitivity

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity  
**Expected**: self.assertEqual(res, 3 / 8)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_transitivity.py:23*

### test_transitivity_triangle

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity triangle  
**Expected**: self.assertEqual(res, 1.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_transitivity.py:30*

### test_transitivity_star

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity star  
**Expected**: self.assertEqual(res, 0.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_transitivity.py:37*

### test_transitivity_empty

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity empty  
**Expected**: self.assertEqual(res, 0.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_transitivity.py:42*

### test_transitivity_disconnected

**Category**: instantiation  
**Description**: Instantiate transitivity: test transitivity disconnected  
**Expected**: self.assertEqual(res, 0.0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.transitivity(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_transitivity.py:48*

### test_graph

**Category**: instantiation  
**Description**: Instantiate chain_decomposition: test graph  
**Expected**: self.assertEqual(expected, chains)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])
return super().setUp()

chains = rustworkx.chain_decomposition(graph, source=0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_chain_decomposition.py:56*

### test_barbell_graph

**Category**: instantiation  
**Description**: Instantiate chain_decomposition: test barbell graph  
**Expected**: self.assertEqual(expected, chains)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])
return super().setUp()

chains = rustworkx.chain_decomposition(self.graph, source=0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_chain_decomposition.py:67*

### test_disconnected_graph

**Category**: instantiation  
**Description**: Instantiate union: test disconnected graph  
**Expected**: self.assertEqual(expected, chains)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])
return super().setUp()

graph = rustworkx.union(self.graph, self.graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_chain_decomposition.py:72*

### test_disconnected_graph

**Category**: instantiation  
**Description**: Instantiate chain_decomposition: test disconnected graph  
**Expected**: self.assertEqual(expected, chains)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])
return super().setUp()

chains = rustworkx.chain_decomposition(graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_chain_decomposition.py:73*

### test_disconnected_graph_root_node

**Category**: instantiation  
**Description**: Instantiate union: test disconnected graph root node  
**Expected**: self.assertEqual(expected, chains)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])
return super().setUp()

graph = rustworkx.union(self.graph, self.graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_chain_decomposition.py:83*

### test_disconnected_graph_root_node

**Category**: instantiation  
**Description**: Instantiate chain_decomposition: test disconnected graph root node  
**Expected**: self.assertEqual(expected, chains)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.extend_from_edge_list([(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])
return super().setUp()

chains = rustworkx.chain_decomposition(graph, source=0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_chain_decomposition.py:84*

### test_graph

**Category**: instantiation  
**Description**: Instantiate chain_decomposition: test graph  
**Expected**: self.assertEqual(expected, chains)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
chains = rustworkx.chain_decomposition(graph, source=0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_chain_decomposition.py:56*

### test_barbell_graph

**Category**: instantiation  
**Description**: Instantiate chain_decomposition: test barbell graph  
**Expected**: self.assertEqual(expected, chains)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
chains = rustworkx.chain_decomposition(self.graph, source=0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_chain_decomposition.py:67*

### test_cycle_basis

**Category**: instantiation  
**Description**: Instantiate sorted: test cycle basis  
**Expected**: self.assertEqual([[0, 1, 2, 3], [0, 3, 4, 5]], res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.add_nodes_from(list(range(10)))
self.graph.add_edges_from_no_data([(0, 1), (0, 3), (0, 5), (0, 8), (1, 2), (1, 6), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9)])

res = sorted((sorted(c) for c in rustworkx.cycle_basis(graph, 0)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cycle_basis.py:43*

### test_cycle_basis_multiple_roots_same_cycles

**Category**: instantiation  
**Description**: Instantiate sorted: test cycle basis multiple roots same cycles  
**Expected**: self.assertEqual(res, [[0, 1, 2, 3], [0, 1, 6, 7, 8], [0, 3, 4, 5]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.add_nodes_from(list(range(10)))
self.graph.add_edges_from_no_data([(0, 1), (0, 3), (0, 5), (0, 8), (1, 2), (1, 6), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9)])

res = sorted((sorted(x) for x in rustworkx.cycle_basis(self.graph, 0)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cycle_basis.py:47*

### test_cycle_basis_multiple_roots_same_cycles

**Category**: instantiation  
**Description**: Instantiate sorted: test cycle basis multiple roots same cycles  
**Expected**: self.assertEqual(res, [[0, 1, 2, 3], [0, 1, 6, 7, 8], [0, 3, 4, 5]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.add_nodes_from(list(range(10)))
self.graph.add_edges_from_no_data([(0, 1), (0, 3), (0, 5), (0, 8), (1, 2), (1, 6), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9)])

res = sorted((sorted(x) for x in rustworkx.cycle_basis(self.graph, 1)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cycle_basis.py:49*

### test_cycle_basis_multiple_roots_same_cycles

**Category**: instantiation  
**Description**: Instantiate sorted: test cycle basis multiple roots same cycles  
**Expected**: self.assertEqual(res, [[0, 1, 2, 3], [0, 1, 6, 7, 8], [0, 3, 4, 5]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.add_nodes_from(list(range(10)))
self.graph.add_edges_from_no_data([(0, 1), (0, 3), (0, 5), (0, 8), (1, 2), (1, 6), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9)])

res = sorted((sorted(x) for x in rustworkx.cycle_basis(self.graph, 9)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cycle_basis.py:51*

### test_cycle_basis_disconnected_graphs

**Category**: instantiation  
**Description**: Instantiate cycle_basis: test cycle basis disconnected graphs  
**Expected**: self.assertEqual(res, [[0, 1, 2, 3], [0, 1, 6, 7, 8], [0, 3, 4, 5], [10, 11, 12]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.add_nodes_from(list(range(10)))
self.graph.add_edges_from_no_data([(0, 1), (0, 3), (0, 5), (0, 8), (1, 2), (1, 6), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9)])

cycles = rustworkx.cycle_basis(self.graph, 9)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cycle_basis.py:57*

### test_self_loop

**Category**: instantiation  
**Description**: Instantiate sorted: test self loop  
**Expected**: self.assertEqual([[0, 1, 2, 3], [0, 1, 6, 7, 8], [0, 3, 4, 5], [1]], res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.graph.add_nodes_from(list(range(10)))
self.graph.add_edges_from_no_data([(0, 1), (0, 3), (0, 5), (0, 8), (1, 2), (1, 6), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9)])

res = sorted((sorted(c) for c in rustworkx.cycle_basis(self.graph, 0)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cycle_basis.py:68*

### test_cycle_basis

**Category**: instantiation  
**Description**: Instantiate sorted: test cycle basis  
**Expected**: self.assertEqual([[0, 1, 2, 3], [0, 3, 4, 5]], res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = sorted((sorted(c) for c in rustworkx.cycle_basis(graph, 0)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cycle_basis.py:43*

### test_cycle_basis_multiple_roots_same_cycles

**Category**: instantiation  
**Description**: Instantiate sorted: test cycle basis multiple roots same cycles  
**Expected**: self.assertEqual(res, [[0, 1, 2, 3], [0, 1, 6, 7, 8], [0, 3, 4, 5]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = sorted((sorted(x) for x in rustworkx.cycle_basis(self.graph, 0)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cycle_basis.py:47*

### test_cycle_basis_multiple_roots_same_cycles

**Category**: instantiation  
**Description**: Instantiate sorted: test cycle basis multiple roots same cycles  
**Expected**: self.assertEqual(res, [[0, 1, 2, 3], [0, 1, 6, 7, 8], [0, 3, 4, 5]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = sorted((sorted(x) for x in rustworkx.cycle_basis(self.graph, 1)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cycle_basis.py:49*

### test_cycle_basis_multiple_roots_same_cycles

**Category**: instantiation  
**Description**: Instantiate sorted: test cycle basis multiple roots same cycles  
**Expected**: self.assertEqual(res, [[0, 1, 2, 3], [0, 1, 6, 7, 8], [0, 3, 4, 5]])  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = sorted((sorted(x) for x in rustworkx.cycle_basis(self.graph, 9)))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cycle_basis.py:51*

### test_single_neighbor

**Category**: instantiation  
**Description**: Instantiate add_node: test single neighbor  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_a = graph.add_node('a')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_neighbors.py:21*

### test_single_neighbor

**Category**: instantiation  
**Description**: Instantiate add_node: test single neighbor  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_b = graph.add_node('b')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_neighbors.py:22*

### test_single_neighbor

**Category**: instantiation  
**Description**: Instantiate add_node: test single neighbor  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_c = graph.add_node('c')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_neighbors.py:24*

### test_single_neighbor

**Category**: instantiation  
**Description**: Instantiate neighbors: test single neighbor  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = graph.neighbors(node_a)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_neighbors.py:26*

### test_unique_neighbors_on_graphs

**Category**: instantiation  
**Description**: Instantiate add_node: test unique neighbors on graphs  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_a = dag.add_node('a')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_neighbors.py:31*

### test_unique_neighbors_on_graphs

**Category**: instantiation  
**Description**: Instantiate add_node: test unique neighbors on graphs  
**Expected**: self.assertCountEqual([node_c, node_b], res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
node_b = dag.add_node('b')
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_neighbors.py:32*

### test_undirected_gnm_graph

**Category**: instantiation  
**Description**: Instantiate gnm_random_graph: test undirected gnm graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
g = networkx.gnm_random_graph(10, 10, seed=42)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_converters.py:20*

### test_undirected_gnm_graph

**Category**: instantiation  
**Description**: Instantiate networkx_converter: test undirected gnm graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
out_graph = rustworkx.networkx_converter(g, keep_attributes=keep_attributes)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_converters.py:23*

### test_directed_gnm_graph

**Category**: instantiation  
**Description**: Instantiate gnm_random_graph: test directed gnm graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
g = networkx.gnm_random_graph(10, 10, seed=42, directed=True)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_converters.py:30*

### test_directed_gnm_graph

**Category**: instantiation  
**Description**: Instantiate networkx_converter: test directed gnm graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
out_graph = rustworkx.networkx_converter(g, keep_attributes=keep_attributes)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_converters.py:33*

### test_empty_graph

**Category**: instantiation  
**Description**: Instantiate networkx_converter: test empty graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
out_graph = rustworkx.networkx_converter(g, keep_attributes=keep_attributes)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_converters.py:43*

### test_empty_multigraph

**Category**: instantiation  
**Description**: Instantiate networkx_converter: test empty multigraph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
out_graph = rustworkx.networkx_converter(g, keep_attributes=keep_attributes)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_converters.py:53*

### test_empty_directed_graph

**Category**: instantiation  
**Description**: Instantiate networkx_converter: test empty directed graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
out_graph = rustworkx.networkx_converter(g, keep_attributes=keep_attributes)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_converters.py:63*

### test_empty_directed_multigraph

**Category**: instantiation  
**Description**: Instantiate networkx_converter: test empty directed multigraph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
out_graph = rustworkx.networkx_converter(g, keep_attributes=keep_attributes)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_converters.py:73*

### test_cubical_graph

**Category**: instantiation  
**Description**: Instantiate cubical_graph: test cubical graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
g = networkx.cubical_graph(networkx.Graph)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_converters.py:80*

### test_cubical_graph

**Category**: instantiation  
**Description**: Instantiate networkx_converter: test cubical graph  
**Confidence**: 0.80  
**Tags**: unittest  

```python
out_graph = rustworkx.networkx_converter(g, keep_attributes=keep_attributes)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\test_converters.py:83*

### test_barbell_graph_count

**Category**: instantiation  
**Description**: Instantiate barbell_graph: test barbell graph count  
**Expected**: self.assertEqual(len(graph), 37)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.barbell_graph(17, 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_barbell.py:20*

### test_barbell_graph_edge

**Category**: instantiation  
**Description**: Instantiate barbell_graph: test barbell graph edge  
**Expected**: self.assertEqual(set(edge_list), set(expected_edge_list))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.barbell_graph(4, 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_barbell.py:25*

### test_barbell_graph_edge

**Category**: instantiation  
**Description**: Instantiate set: test barbell graph edge  
**Expected**: self.assertEqual(set(edge_list), set(expected_edge_list))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
expected_edge_list = set([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (7, 9), (7, 10), (8, 9), (8, 10), (9, 10)])
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_barbell.py:27*

### test_barbell_graph_no_path_num

**Category**: instantiation  
**Description**: Instantiate barbell_graph: test barbell graph no path num  
**Expected**: self.assertEqual(set(graph.edge_list()), set(mesh.edge_list()))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.barbell_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_barbell.py:50*

### test_barbell_graph_no_path_num

**Category**: instantiation  
**Description**: Instantiate mesh_graph: test barbell graph no path num  
**Expected**: self.assertEqual(set(graph.edge_list()), set(mesh.edge_list()))  
**Confidence**: 0.80  
**Tags**: unittest  

```python
mesh = rustworkx.generators.mesh_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_barbell.py:51*

### test_barbell_graph_count

**Category**: instantiation  
**Description**: Instantiate barbell_graph: test barbell graph count  
**Expected**: self.assertEqual(len(graph), 37)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.barbell_graph(17, 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\generators\test_barbell.py:20*

### test_null_cartesian_null

**Category**: instantiation  
**Description**: Instantiate graph_cartesian_product: test null cartesian null  
**Expected**: self.assertEqual(graph_product.num_nodes(), 0)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph_product, _ = rustworkx.graph_cartesian_product(graph_1, graph_2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cartesian_product.py:22*

### test_path_2_cartesian_path_2

**Category**: instantiation  
**Description**: Instantiate path_graph: test path 2 cartesian path 2  
**Expected**: self.assertEqual(graph_product.num_nodes(), 4)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph_1 = rustworkx.generators.path_graph(2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cartesian_product.py:27*

### test_path_2_cartesian_path_2

**Category**: instantiation  
**Description**: Instantiate path_graph: test path 2 cartesian path 2  
**Expected**: self.assertEqual(graph_product.num_nodes(), 4)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph_2 = rustworkx.generators.path_graph(2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cartesian_product.py:28*

### test_path_2_cartesian_path_2

**Category**: instantiation  
**Description**: Instantiate graph_cartesian_product: test path 2 cartesian path 2  
**Expected**: self.assertEqual(graph_product.num_nodes(), 4)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph_product, _ = rustworkx.graph_cartesian_product(graph_1, graph_2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_cartesian_product.py:30*

### test_all_shortest_paths_single

**Category**: instantiation  
**Description**: Instantiate graph_all_shortest_paths: test all shortest paths single  
**Expected**: self.assertEqual(expected, paths)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

paths = rustworkx.graph_all_shortest_paths(self.graph, self.a, self.e, lambda x: float(x))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_shortest_paths.py:38*

### test_all_shortest_paths

**Category**: instantiation  
**Description**: Instantiate graph_all_shortest_paths: test all shortest paths  
**Expected**: self.assertEqual(len(paths), 2)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

paths = rustworkx.graph_all_shortest_paths(self.graph, self.a, self.e, lambda x: float(x))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_shortest_paths.py:47*

### test_all_shortest_paths_with_no_path

**Category**: instantiation  
**Description**: Instantiate graph_all_shortest_paths: test all shortest paths with no path  
**Expected**: self.assertEqual(expected, paths)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

paths = rustworkx.graph_all_shortest_paths(g, a, b, lambda x: float(x))
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_shortest_paths.py:59*

### test_all_shortest_paths_with_invalid_weights

**Category**: instantiation  
**Description**: Instantiate path_graph: test all shortest paths with invalid weights  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
self.graph.add_edge(self.a, self.b, 7)
self.graph.add_edge(self.c, self.a, 9)
self.graph.add_edge(self.a, self.d, 14)
self.graph.add_edge(self.b, self.c, 10)
self.graph.add_edge(self.d, self.c, 2)
self.graph.add_edge(self.d, self.e, 9)
self.graph.add_edge(self.b, self.f, 15)
self.graph.add_edge(self.c, self.f, 11)
self.graph.add_edge(self.e, self.f, 6)

graph = rustworkx.generators.path_graph(2)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_shortest_paths.py:64*

### test_empty_graph

**Category**: instantiation  
**Description**: Instantiate connected_subgraphs: test empty graph  
**Expected**: self.assertConnectedSubgraphsEqual(subgraphs, expected)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (1, 2), (2, 3), (0, 3), (0, 4), (4, 5), (4, 7), (7, 6), (5, 6)]
self.nodes = list(range(8))
g = rustworkx.PyGraph()
g.add_nodes_from(self.nodes)
g.add_edges_from_no_data(self.edges)
self.expected_subgraphs = {k: list(bruteforce(g, k)) for k in range(1, 9)}

subgraphs = rustworkx.connected_subgraphs(graph, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_connected_subgraphs.py:39*

### test_empty_graph_2

**Category**: instantiation  
**Description**: Instantiate connected_subgraphs: test empty graph 2  
**Expected**: self.assertConnectedSubgraphsEqual(subgraphs, expected)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
super().setUp()
self.edges = [(0, 1), (1, 2), (2, 3), (0, 3), (0, 4), (4, 5), (4, 7), (7, 6), (5, 6)]
self.nodes = list(range(8))
g = rustworkx.PyGraph()
g.add_nodes_from(self.nodes)
g.add_edges_from_no_data(self.edges)
self.expected_subgraphs = {k: list(bruteforce(g, k)) for k in range(1, 9)}

subgraphs = rustworkx.connected_subgraphs(graph, 0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_all_connected_subgraphs.py:47*

### test_graph_k_shortest_path_lengths

**Category**: instantiation  
**Description**: Instantiate graph_k_shortest_path_lengths: test graph k shortest path lengths  
**Expected**: self.assertEqual(res, expected)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.graph_k_shortest_path_lengths(graph, 1, 2, lambda _: 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_k_shortest_path.py:35*

### test_k_graph_shortest_path_with_goal

**Category**: instantiation  
**Description**: Instantiate graph_k_shortest_path_lengths: test k graph shortest path with goal  
**Expected**: self.assertEqual({3: 4}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.graph_k_shortest_path_lengths(graph, 0, 2, lambda _: 1, 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_k_shortest_path.py:43*

### test_k_graph_shortest_path_with_goal_node_hole

**Category**: instantiation  
**Description**: Instantiate path_graph: test k graph shortest path with goal node hole  
**Expected**: self.assertEqual({3: 2}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_k_shortest_path.py:47*

### test_k_graph_shortest_path_with_goal_node_hole

**Category**: instantiation  
**Description**: Instantiate graph_k_shortest_path_lengths: test k graph shortest path with goal node hole  
**Expected**: self.assertEqual({3: 2}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.graph_k_shortest_path_lengths(graph, start=1, k=1, edge_cost=lambda _: 1, goal=3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_k_shortest_path.py:49*

### test_graph_k_shortest_path_with_invalid_weight

**Category**: instantiation  
**Description**: Instantiate path_graph: test graph k shortest path with invalid weight  
**Confidence**: 0.80  
**Tags**: unittest  

```python
graph = rustworkx.generators.path_graph(4)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_k_shortest_path.py:55*

### test_k_shortest_path_with_no_path

**Category**: instantiation  
**Description**: Instantiate graph_k_shortest_path_lengths: test k shortest path with no path  
**Expected**: self.assertEqual(expected, path_lengths)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
path_lengths = rustworkx.graph_k_shortest_path_lengths(g, start=a, k=1, edge_cost=float, goal=b)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_k_shortest_path.py:71*

### test_graph_k_shortest_path_lengths

**Category**: instantiation  
**Description**: Instantiate graph_k_shortest_path_lengths: test graph k shortest path lengths  
**Expected**: self.assertEqual(res, expected)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.graph_k_shortest_path_lengths(graph, 1, 2, lambda _: 1)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_k_shortest_path.py:35*

### test_k_graph_shortest_path_with_goal

**Category**: instantiation  
**Description**: Instantiate graph_k_shortest_path_lengths: test k graph shortest path with goal  
**Expected**: self.assertEqual({3: 4}, res)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
res = rustworkx.graph_k_shortest_path_lengths(graph, 0, 2, lambda _: 1, 3)
```

*Source: C:\Users\Bin\AppData\Local\Temp\rwx-clone\tests\graph\test_k_shortest_path.py:43*

