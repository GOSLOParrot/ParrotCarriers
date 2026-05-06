# rustworkx-docs Skill Documentation

## Description

This skill provides comprehensive documentation and codebase analysis for the `rustworkx` project. `rustworkx` is a high-performance, general-purpose graph library for Python, implemented in Rust. This documentation is designed to help you understand its architecture, APIs, usage patterns, and best practices.

## When to Use This Skill

Use this skill when you need to:

*   **Understand `rustworkx` fundamentals**: Learn about core graph types (`PyGraph`, `PyDiGraph`), graph construction, and basic operations.
*   **Explore algorithms**: Find details and usage examples for graph traversal (BFS, DFS), shortest path algorithms (Dijkstra, A\*), centrality measures (Betweenness, PageRank), and connectivity analysis.
*   **Generate and manipulate graphs**: Discover how to use graph generators and perform common graph modifications.
*   **Visualize graphs**: Understand options for laying out and drawing graphs.
*   **Integrate with other libraries**: Learn about interoperability with `NetworkX` and other data formats.
*   **Understand performance characteristics**: Get insights into `rustworkx`'s Rust-implemented core and performance considerations.
*   **Navigate the `rustworkx` codebase structure**: Find references to key project documentation, API specifics, and tutorials.

## Key Concepts

`rustworkx` provides a robust set of functionalities for graph theory, built for speed and efficiency.

*   **Core Graph Types**:
    *   `PyGraph`: For undirected graphs, featuring stable integer node indices.
    *   `PyDiGraph`: For directed graphs, optimized for DAG-specific operations.
    *   Node and edge payloads can be Python objects (e.g., for weights or custom data). Node indices remain stable even after deletion, creating gaps.
*   **Traversal Algorithms**: Includes Breadth-First Search (`bfs_successors`, `bfs_search`), Depth-First Search (`dfs_search`), topological sort, and various shortest path algorithms like Dijkstra, A\*, and Bellman-Ford.
*   **Centrality Measures**: Offers algorithms to quantify node or edge importance, such as `betweenness_centrality`, `closeness_centrality`, `eigenvector_centrality`, `pagerank`, and `degree_centrality`.
*   **Subgraph Isomorphism / Matching**: Provides tools like `is_isomorphic` and `is_subgraph_isomorphic` based on the VF2 algorithm, supporting custom node/edge matchers.
*   **Connectivity / Components**: Functions to find connected components (`connected_components`), strongly/weakly connected components, articulation points, bridges, and simple cycles.
*   **Graph Generators**: A collection of functions in `rustworkx.generators` to create common graph structures like complete graphs, path graphs, cycle graphs, binomial trees, and random graphs (e.g., Barabási-Albert, GNM/GNP random graphs).
*   **Layout / Visualization**: Utilities for calculating graph layouts (`spring_layout`, `circular_layout`) and drawing graphs using `matplotlib` (`mpl_draw`) or `graphviz` (`graphviz_draw`), supporting custom callbacks for node/edge styling.
*   **Conversion / Interop**: Facilitates conversion to and from `NetworkX` graphs (`networkx_converter`), and supports I/O operations for formats like Node-Link JSON and GraphML.
*   **Performance / Internals**: The core is implemented in Rust, often releasing the Python GIL for computationally intensive loops, allowing for high performance. It uses `u32` for node indices, theoretically supporting up to 4 billion nodes.

## ⚡ Quick Reference: Practical Examples

These examples demonstrate common tasks and key functionalities of `rustworkx`.

### 1. Shortest Path Calculation in an Undirected Graph

This example illustrates how to create a `PyGraph` and find the shortest path between two nodes using Dijkstra's algorithm.

```python
import rustworkx

# Rustworkx's undirected graph type.
graph = rustworkx.PyGraph()

# Each time add_node is called, it returns a new node index
a = graph.add_node("A")
b = graph.add_node("B")
c = graph.add_node("C")

# add_edges_from takes tuples of node indices and weights,
# and returns edge indices
graph.add_edges_from([(a, b, 1.5), (a, c, 5.0), (b, c, 2.5)])

# Returns the path A -> B -> C
path_lengths = rustworkx.dijkstra_shortest_paths(graph, a, c, weight_fn=float)
print(f"Shortest path from A to C: {path_lengths}")
# Expected output: {2: 4.0} (node index 2 is C, total weight 1.5 + 2.5 = 4.0)
```

### 2. Creating and Modifying a Directed Graph (`PyDiGraph`)

Demonstrates how to initialize a `PyDiGraph` and add nodes and directed edges.

```python
import rustworkx

digraph = rustworkx.PyDiGraph()
node_a = digraph.add_node("Start Node")
node_b = digraph.add_node("Middle Node")
node_c = digraph.add_node("End Node")

# Add a directed edge from A to B with a dictionary payload
digraph.add_edge(node_a, node_b, {"capacity": 10, "cost": 1.0})
# Add another directed edge from B to C
digraph.add_edge(node_b, node_c, {"capacity": 5, "cost": 2.5})

print(f"Nodes in digraph: {digraph.node_indices()}")
print(f"Number of edges: {digraph.num_edges()}")
```

### 3. Breadth-First Search (BFS) Traversal

Illustrates how to perform a BFS traversal to find successors from a starting node.

```python
import rustworkx

graph = rustworkx.PyGraph()
a, b, c, d = graph.add_nodes_from(["A", "B", "C", "D"])
graph.add_edges_from([(a, b, None), (b, c, None), (a, d, None)])

# Get BFS successors from node 'a' (index 0)
# bfs_successors returns an iterator of (node, list_of_successors) tuples
bfs_successors_list = list(rustworkx.bfs_successors(graph, a))
print(f"BFS successors from A: {bfs_successors_list}")
# Expected output: [(0, [1, 3]), (1, [2])] (assuming 0=A, 1=B, 2=C, 3=D)
```

### 4. Calculating Betweenness Centrality

Shows how to compute the betweenness centrality for all nodes in a graph, a measure of influence in information flow.

```python
import rustworkx

graph = rustworkx.PyGraph()
n = graph.add_nodes_from(range(4)) # Nodes 0, 1, 2, 3
graph.add_edges_from([(0, 1, None), (1, 2, None), (2, 3, None), (3, 0, None)])

# Calculate betweenness centrality for each node
centrality = rustworkx.betweenness_centrality(graph)
print(f"Betweenness Centrality: {centrality}")
# For a cycle graph, all nodes typically have the same betweenness centrality (0.0 in this unweighted case).
```

### 5. Generating a Complete Graph

Uses the `rustworkx.generators` module to quickly create a complete graph.

```python
import rustworkx.generators as gen

# Create a complete graph with 5 nodes (each node connected to every other node)
complete_graph = gen.complete_graph(5)

print(f"Number of nodes in complete graph: {complete_graph.num_nodes()}")
print(f"Number of edges in complete graph: {complete_graph.num_edges()}")
# Expected: 5 nodes, 10 edges (N*(N-1)/2)
```

### 6. Converting a `rustworkx` Graph to `NetworkX`

Demonstrates interoperability by converting a `rustworkx.PyGraph` to a `networkx.Graph` object.

```python
import rustworkx
import networkx as nx

# Create a sample rustworkx graph
graph_rx = rustworkx.PyGraph()
graph_rx.add_nodes_from(["Node X", "Node Y", "Node Z"])
graph_rx.add_edges_from([(0, 1, None), (1, 2, None)])

# Convert the rustworkx graph to a networkx Graph
# The second argument specifies the NetworkX graph type
graph_nx = rustworkx.networkx_converter(graph_rx, nx.Graph)

print(f"NetworkX graph nodes: {graph_nx.nodes()}")
print(f"NetworkX graph edges: {graph_nx.edges()}")
```

## 📚 Available Reference Documents & How to Use Them

This skill includes detailed reference documentation categorized for easy navigation.

### Project Documentation (`references/documentation/`)

These files provide high-level overviews, tutorials, and API specifications directly extracted from the `rustworkx` project's documentation.

*   **Overview**:
    *   `benchmarks.rst`: Performance benchmarks.
    *   `index.rst`: Main documentation index.
    *   `install.rst`: Installation instructions.
    *   `networkx.rst`: Notes on `rustworkx` vs. `NetworkX`.
    *   `README.md`: Project overview, usage, installation, and community information.
    *   *...and 2 more*
*   **Guides (`tutorial/`)**: Step-by-step guides for specific algorithms and concepts.
    *   `betweenness_centrality.rst`: Tutorial on using betweenness centrality.
    *   `dags.rst`: Guide to working with Directed Acyclic Graphs.
    *   `index.rst`: Tutorial section index.
    *   `introduction.rst`: Introduction to `rustworkx`.
*   **API Reference (`api/algorithm_functions/`)**: Detailed documentation for `rustworkx` functions and classes.
    *   `centrality.rst`: API for centrality algorithms.
    *   `coloring.rst`: API for graph coloring algorithms.
    *   `connectivity_and_cycles.rst`: API for connectivity and cycle detection.
    *   `dag_algorithms.rst`: API for DAG-specific algorithms.
    *   `dominance.rst`: API for dominance algorithms.
    *   *...and 21 more*
*   **Contributing**:
    *   `CONTRIBUTING.md`: Guidelines for contributing to the `rustworkx` project.
*   **Templates**: Internal documentation templates.
    *   `class.rst`: `_templates/autosummary/class.rst`

### Other References

*   **Dependencies (`references/dependencies/`)**: Provides insights into the project's dependency graph and analysis, useful for understanding the codebase's internal structure and interconnections.

**To use these references effectively**:
*   **For quick answers**: Refer to the `README.md` for installation and basic usage, and the "Quick Reference" section above for common code patterns.
*   **For in-depth understanding**: Dive into the `tutorial/` guides for practical application knowledge.
*   **For API specifics**: Consult the `api/` documentation for detailed function signatures, parameters, and return values.
*   **For project health**: Check `CONTRIBUTING.md` for development guidelines.
*   **For internal structure**: Explore `references/dependencies/` for dependency analysis.