# Skill Seeker distillation focus — RustworkX Official Docs

> **Repo:** Qiskit/rustworkx (only `docs/source/`) | **Pin:** main (2026-05-05)

蒸馏目标：把 rustworkx.org 官方文档（API reference + tutorials + release notes）压缩成一个
ParrotCarriers 可读的 SKILL.md。本块 **只看 `docs/source/`**，不看 src。

## §A — Core Graph Types & Construction

- `PyGraph` — undirected graph with stable integer node indices
- `PyDiGraph` — directed graph (DAG-friendly)
- `PyDAG` — alias / shim for DAG-specific helpers
- `add_node`, `add_edge`, `add_nodes_from`, `add_edges_from`
- `extend_from_edge_list`, `extend_from_weighted_edge_list`
- `remove_node`, `remove_edge`, `remove_node_retain_edges`
- node payload via Python objects (callbacks); edge payload weight or callable
- node index stability after deletion (gap remains)

## §B — Traversal Algorithms

- `bfs_successors`, `bfs_predecessors`, `bfs_search`
- `dfs_search`, `dfs_edges`, `topological_sort`
- `descendants`, `ancestors`
- `digraph_dijkstra_shortest_paths`, `dijkstra_shortest_path_lengths`
- `astar_shortest_path`, `bellman_ford_shortest_paths`
- `all_simple_paths`, `all_pairs_dijkstra_path_lengths`
- `digraph_floyd_warshall_numpy`

## §C — Centrality / Importance

- `betweenness_centrality`, `edge_betweenness_centrality`
- `closeness_centrality`, `eigenvector_centrality`
- `katz_centrality`
- `pagerank`
- `degree_centrality`

## §D — Subgraph Isomorphism / Matching

- `is_isomorphic`, `is_subgraph_isomorphic`
- VF2 algorithm (vf2pp)
- `node_matcher` callback, `edge_matcher` callback
- `id_order: bool` heuristic
- `call_limit: int` — early-termination quota
- `vf2_mapping` — generator of valid mappings

## §E — Connectivity / Components

- `connected_components`, `number_connected_components`
- `strongly_connected_components`, `weakly_connected_components`
- `articulation_points`, `bridges`
- `cycle_basis`, `simple_cycles`

## §F — Generators

- `generators.directed_path_graph`, `directed_cycle_graph`
- `generators.complete_graph`, `binomial_tree_graph`
- `generators.random_geometric_graph`, `random_bipartite_graph`
- `generators.barabasi_albert_graph` (preferential attachment)
- `generators.gnm_random_graph` / `gnp_random_graph`

## §G — Layout / Visualization

- `spring_layout`, `circular_layout`, `shell_layout`, `random_layout`
- `bipartite_layout`
- `mpl_draw` (matplotlib), `graphviz_draw`
- node/edge color callbacks for visualization

## §H — Conversion / Interop

- `networkx_converter` ↔ NetworkX
- `from_node_link_json_file`, `node_link_json`
- `read_graphml`, `write_graphml`
- `digraph_adjacency_matrix`, `adjacency_matrix`

## §I — Performance / Internals

- Rust-implemented core; GIL released for hot loops
- node index stability ↔ "gap" semantics after `remove_node`
- 4 billion node theoretical maximum (u32 indices)
- C-extension `.pyd` / `.so` distribution

## §J — Release Notes / Stability Hints

- 0.17.x latest stable line
- Backwards-compat policy across minor versions
- Known caveats (signed weights, community detection gaps)

## What NOT to focus on

- Build instructions / Cargo internals
- Tox / CI scripts
- Crate-level Rust API (rustworkx-core) — Python users don't need it
