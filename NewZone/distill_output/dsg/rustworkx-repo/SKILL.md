# rustworkx-repo Documentation

This document provides comprehensive information about the `rustworkx` library, focusing on its codebase structure, design patterns, core algorithms, and practical usage. It is generated from local code analysis to assist with understanding and interacting with the `rwx-clone` project.

## Description

`rustworkx` is a high-performance, general-purpose graph library for Python, implemented in Rust. This skill provides local codebase analysis and documentation generated directly from the `rwx-clone` project source.

**Codebase Path:** `C:\Users\Bin\AppData\Local\Temp\rwx-clone`
**Analysis Depth:** surface

## When to Use This Skill

Use this skill when you need to:
*   **Understand Architecture**: Grasp the underlying architecture, design patterns, and Rust-Python binding mechanisms of `rustworkx`.
*   **Explore Implementations**: Find concrete implementation examples for various graph algorithms and usage patterns.
*   **Review APIs**: Access API documentation extracted from the code.
*   **Analyze Configurations**: Check configuration patterns, especially for build and release processes.
*   **Discover Test Cases**: Examine test examples for real-world usage and expected behavior.
*   **Navigate Codebase**: Efficiently locate and understand different components of the `rustworkx` project.

## Key Concepts

`rustworkx` leverages Rust for performance while providing a Python-friendly interface. Understanding these core concepts enhances effective use.

### Architecture and Bindings

*   **Rust Core (`src/`, `rustworkx-core/`)**: The high-performance algorithms and graph data structures are primarily implemented in Rust. `rustworkx-core/` is a pure Rust crate, while `src/` contains the Python bindings.
*   **PyO3 Bindings**: Python interaction is facilitated by `PyO3`, using `#[pyclass]` for Python-exposed classes (like `PyGraph`, `PyDiGraph`) and `#[pymethods]` for Python-callable methods.
*   **`StableGraph` Backing Store**: `rustworkx` uses `petgraph::stable_graph::StableGraph` internally, ensuring node and edge index stability even after removals.
*   **Python Callbacks and GIL**: Python callback functions can be passed to Rust algorithms. The Global Interpreter Lock (GIL) is released for long-running Rust computations using `py.allow_threads(...)` to prevent blocking.

### Graph Types and Core Functionality

*   **`PyGraph`**: Represents undirected graphs.
*   **`PyDiGraph`**: Represents directed graphs.
*   **`PyDAG`**: A specialized `PyDiGraph` that maintains a strict Directed Acyclic Graph invariant and provides additional DAG-specific methods.
*   **Node and Edge Data**: Nodes and edges can store arbitrary Python objects as associated data.

### Key Algorithms

The library provides a wide range of graph algorithms, categorized as:
*   **Centrality**: Betweenness, closeness, eigenvector, Katz, PageRank.
*   **Connectivity**: Strongly Connected Components (Tarjan), articulation points, bridges.
*   **Shortest Path**: Dijkstra, Bellman-Ford, A*, Floyd-Warshall, Johnson.
*   **Isomorphism**: VF2++ (vf2pp) for both directed and undirected graphs.
*   **Traversal**: Breadth-First Search (BFS), Depth-First Search (DFS), topological sort.
*   **Generators**: Functions to create various types of graphs (e.g., random, structured).
*   **Graph Coloring**: Algorithms for vertex and edge coloring.
*   **DAG-specific**: Longest path, lexicographical topological sort, layers.

### Performance Considerations

*   **`parallel_threshold`**: Many algorithms leverage `rayon` for parallelization, with a configurable threshold to determine when to use parallel execution.
*   **Data Representation**: Node and edge weights can be Python objects or integer indices; performance can vary.
*   **Reference vs. Copy**: `get_node_data` returns a reference, not a copy, for efficiency.
*   **Bulk APIs**: Using methods like `add_nodes_from` and `extend_from_edge_list` is generally more performant than individual `add_node` or `add_edge` calls.

### Important Public Symbols

Key classes and functions frequently used in `rustworkx` include:
*   `PyGraph`, `PyDiGraph`, `PyDAG`
*   `EdgeList`, `WeightedEdgeList`
*   `NodeIndices`, `EdgeIndices`
*   `vf2_mapping`, `is_isomorphic`, `is_subgraph_isomorphic`
*   `digraph_astar_shortest_path`, `dijkstra_shortest_path_lengths`
*   `ancestors`, `descendants`, `topological_sort`

## ⚡ Quick Reference

### Codebase Statistics

**Languages:** Python, Rust
**Analysis Performed:**
*   ✅ API Reference
*   ✅ Dependency Graph
*   ✅ Design Patterns
*   ✅ Test Examples
*   ✅ Configuration Patterns
*   ✅ Architectural Analysis
*   ✅ Project Documentation

### 🎨 Design Patterns Detected

*From codebase analysis (confidence > 0.7)*
*   **Strategy**: 1 instances
*   **Builder**: 1 instances
*   Total: 2 high-confidence patterns

### 📝 Practical Code Examples

These examples demonstrate common tasks and important functionalities in `rustworkx`.

**1. Basic Undirected Graph Creation and Edge Addition**
Create a `PyGraph`, add nodes with data, and add weighted edges.

```python
import rustworkx

# Create an undirected graph
graph = rustworkx.PyGraph()

# Add nodes and get their indices
node_a = graph.add_node("A")
node_b = graph.add_node("B")
node_c = graph.add_node("C")

# Add edges with weights
graph.add_edges_from([(node_a, node_b, 1.5), (node_a, node_c, 5.0), (node_b, node_c, 2.5)])

print(f"Nodes: {graph.nodes()}")
print(f"Edges: {graph.edges()}")
```

**2. Directed Acyclic Graph (DAG) with Cycle Check**
Demonstrates `PyDAG` creation, adding children, and how cycle checks prevent invalid operations.

```python
import rustworkx

dag = rustworkx.PyDAG()
dag.check_cycle = True # Enable cycle checking

node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {}) # Add 'b' as a child of 'a'

# Attempting to add an edge that would create a cycle will raise an error
try:
    dag.add_edge(node_b, node_a, {})
except rustworkx.DAGWouldCycle as e:
    print(f"Caught expected error: {e}")
```

**3. Removing Multiple Nodes from a Graph**
Illustrates how to remove a list of nodes and their associated edges from a `PyGraph`.

```python
import rustworkx

graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'Edgy_mk2')

print(f"Nodes before removal: {graph.nodes()}")
print(f"Node indexes before removal: {graph.node_indexes()}")

graph.remove_nodes_from([node_b, node_c])

print(f"Nodes after removal: {graph.nodes()}")       # Expected: ['a']
print(f"Node indexes after removal: {graph.node_indexes()}") # Expected: [0]
```

**4. Finding Ancestors in a Directed Acyclic Graph**
Shows how to use the `ancestors` function to find all predecessors of a given node in a `PyDAG`.

```python
import rustworkx

dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})

# Find all ancestors of node_c
res = rustworkx.ancestors(dag, node_c)
print(f"Ancestors of node {node_c}: {res}") # Expected: {node_a, node_b}
```

**5. Graph Isomorphism Check with Custom Node Matcher**
Compares two `PyDAG` instances for isomorphism using both default and custom node comparison logic.

```python
import rustworkx

dag_a = rustworkx.PyDAG()
node_a1 = dag_a.add_node('data_1')
dag_a.add_child(node_a1, 'data_2', 'edge_1')
dag_a.add_child(node_a1, 'data_3', 'edge_2')

dag_b = rustworkx.PyDAG()
node_b1 = dag_b.add_node('data_1')
dag_b.add_child(node_b1, 'data_2', 'edge_1')
dag_b.add_child(node_b1, 'different_data_3', 'edge_2') # Node data differs here

# Default (identity) comparison - will compare node/edge data directly
is_iso_default = rustworkx.is_isomorphic(dag_a, dag_b)
print(f"Isomorphic (default comparison): {is_iso_default}") # Expected: False

# Custom node comparison (e.g., only compare if nodes have same index)
# Note: This lambda is simplified; a real matcher might compare specific attributes.
is_iso_custom = rustworkx.is_isomorphic(dag_a, dag_b, node_matcher=lambda a, b: True) # Always matches nodes
print(f"Isomorphic (custom node matcher, ignoring data): {is_iso_custom}") # Expected: True
```

**6. A* Shortest Path with Null Heuristic (Dijkstra Equivalent)**
Calculates the shortest path using the A* algorithm with a heuristic that always returns 0, effectively performing Dijkstra's algorithm.

```python
import rustworkx

g = rustworkx.PyDAG()
a = g.add_node('A')
b = g.add_node('B')
c = g.add_node('C')
d = g.add_node('D')
e = g.add_node('E')
g.add_edge(a, b, 7)
g.add_edge(a, d, 14)
g.add_edge(b, c, 10)
g.add_edge(d, c, 2)
g.add_edge(d, e, 9)

# A* shortest path from 'A' to 'E' with a null heuristic (cost_fn is used for edge weights)
# A null heuristic (lambda y: 0) makes A* behave like Dijkstra's.
path = rustworkx.digraph_astar_shortest_path(
    g, a,
    lambda goal_node_data: goal_node_data == 'E', # Goal checker
    lambda edge_weight: float(edge_weight),    # Edge cost function
    lambda node_data: 0                          # Heuristic function
)
print(f"Shortest path from A to E: {path}") # Expected: [a, d, e]
```

**7. Clearing All Nodes and Edges from a Graph**
Demonstrates the `clear()` method to reset a graph to an empty state.

```python
import rustworkx

graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'weight': 1})

print(f"Nodes before clear: {graph.nodes()}")
print(f"Edges before clear: {graph.edges()}")

graph.clear() # Removes all nodes and edges

print(f"Number of nodes after clear: {graph.num_nodes()}") # Expected: 0
print(f"Number of edges after clear: {graph.num_edges()}") # Expected: 0
```

## 📖 Project Documentation

Project documentation, including guides and API references, is extracted from the project's markdown and reStructuredText files.

**Total Documentation Files:** 46
**Categories:** 8

### Overview

*   **README.md** (`README.md`)

### Guides

*   **betweenness_centrality.rst** (`docs\source\tutorial\betweenness_centrality.rst`)
*   **dags.rst** (`docs\source\tutorial\dags.rst`)
*   **introduction.rst** (`docs\source\tutorial\introduction.rst`)

### Api

*   **centrality.rst** (`docs\source\api\algorithm_functions\centrality.rst`)
*   **coloring.rst** (`docs\source\api\algorithm_functions\coloring.rst`)
*   **connectivity_and_cycles.rst** (`docs\source\api\algorithm_functions\connectivity_and_cycles.rst`)
*   **dag_algorithms.rst** (`docs\source\api\algorithm_functions\dag_algorithms.rst`)
*   **dominance.rst** (`docs\source\api\algorithm_functions\dominance.rst`)
*   *...and 21 more files*

### Community

*   **CODE_OF_CONDUCT.md** (`CODE_OF_CONDUCT.md`)

### Contributing

*   **CONTRIBUTING.md** (`CONTRIBUTING.md`)

### Other

*   **PULL_REQUEST_TEMPLATE.md** (`.github\PULL_REQUEST_TEMPLATE.md`)
*   **benchmarks.rst** (`docs\source\benchmarks.rst`)
*   **install.rst** (`docs\source\install.rst`)
*   *...and 7 more files*

## Available Reference Files

This skill includes several detailed reference markdown files, organized by topic, to provide granular insights into the `rustworkx` codebase:

*   **Configuration Patterns (`config_patterns.md`)**: Detailed report on configuration files, settings, and detected patterns (e.g., `Cargo.toml`, `pyproject.toml`, CI/CD configurations).
*   **Code of Conduct (`CODE_OF_CONDUCT.md`)**: Guidelines for community interaction.
*   **Contributing (`CONTRIBUTING.md`)**: Information for developers on how to contribute to the project.
*   **Pull Request Template (`PULL_REQUEST_TEMPLATE.md`)**: The template used for submitting pull requests.
*   **README (`README.md`)**: The main project overview and quick start guide.
*   **Security Policy (`SECURITY.md`)**: Details on supported versions and vulnerability reporting procedures.
*   **Bug Report Template (`BUG_REPORT.md`)**: Template for reporting software defects.
*   **Enhancement Request Template (`ENHANCEMENT_REQUEST.md`)**: Template for suggesting new features or improvements.
*   **Skill Seeker Focus (`skill_seeker_focus.md`)**: An internal document outlining the distillation focus for this skill, emphasizing core architecture, Rust/Python bindings, and key algorithms.
*   **Test Examples (`test_examples.md`)**: An extensive report of extracted code examples from the project's test suite, categorized by type (instantiation, method_call, workflow) and confidence.
*   **How To Guides (e.g., `add-cycle.md`, `ancestors.md`, `astar-manhattan-heuristic.md`, etc.)**: Individual guides created from high-quality test examples, detailing specific workflows and usage patterns.

## How to Use This Documentation Effectively

1.  **For a quick overview**: Start with the "Description" and "When to Use This Skill" sections.
2.  **To understand the core design**: Refer to the "Key Concepts" section for insights into the Rust-Python architecture and graph types.
3.  **To see common tasks in action**: Browse the "Quick Reference" code examples for practical snippets. Each example includes a brief description.
4.  **For detailed usage or implementation examples**: Explore the `test_examples.md` file or the specific "How To" guides (e.g., `add-cycle.md`, `ancestors.md`) listed under "Available Reference Files". These often contain full, runnable code.
5.  **For development guidelines**: Consult `CONTRIBUTING.md` and related `.github` templates.
6.  **For in-depth understanding of specific algorithms**: Look for relevant `.rst` files in the "Project Documentation" API section.
7.  **For build or environment configurations**: Check `config_patterns.md`.

---
Generated by Skill Seeker | Codebase Analyzer with C3.x Analysis