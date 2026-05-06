# Skill Seeker distillation focus — RustworkX Main Repo

> **Repo:** Qiskit/rustworkx (full tree) | **Pin:** main (2026-05-05)

蒸馏目标：把整个 rustworkx 仓库（src/ Rust 实现 + rustworkx/ Python 绑定 + tests/ + docs/）
压缩成一个偏向**底层架构理解**的 SKILL.md。本块覆盖：实现层 + 测试 + 发布，相对官方 docs
关注更深层的工程。

## §A — Repository Layout

- `src/` — Rust core implementation (PyO3 bindings)
- `rustworkx-core/` — pure Rust crate, language-agnostic
- `rustworkx/` — Python package surface
- `tests/` — Python test suite (richest API usage examples)
- `docs/source/` — Sphinx + reStructuredText user docs
- `releasenotes/` — reno-managed yaml release notes
- `tools/` — internal release / lint scripts

## §B — PyO3 Binding Pattern

- `#[pyclass]` for `PyGraph` / `PyDiGraph`
- `#[pymethods]` for Python-visible methods
- Rust `petgraph::stable_graph::StableGraph` as backing store
- node/edge index stability via `StableGraph` semantics
- Python callbacks: `PyAny` payload, deferred conversion
- GIL release: `py.allow_threads(...)` for long-running loops

## §C — Algorithms (Rust impls)

- `src/centrality/` — betweenness, closeness, eigenvector, katz, pagerank
- `src/connectivity/` — SCC (Tarjan), articulation points, bridges
- `src/shortest_path/` — Dijkstra, Bellman-Ford, A*, Floyd-Warshall, Johnson
- `src/isomorphism/` — VF2++ (vf2pp), digraph & graph variants
- `src/traversal/` — BFS, DFS, topological sort
- `src/layout/` — spring, circular, shell, bipartite layouts
- `src/generators/` — graph generators (random, structured)
- `src/coloring/` — graph coloring algorithms
- `src/dag_algo/` — DAG-specific (longest_path, lexicographical_topological_sort)

## §D — Python API Surface

- `rustworkx/__init__.py` — top-level public API
- `rustworkx.generators` — generator submodule
- `rustworkx.visualization` — mpl_draw, graphviz_draw
- `rustworkx.networkx_converter` — convert from networkx
- `is_isomorphic`, `is_subgraph_isomorphic`, `vf2_mapping`
- function-overload-style: `digraph_X` / `graph_X` / `X` (auto-dispatch)

## §E — Test Patterns (tests/)

- `tests/rustworkx_tests/` — algorithm tests
- `tests/digraph/test_isomorphism.py` — VF2 + call_limit usage
- `tests/test_centrality.py` — centrality benchmarks against known graphs
- `tests/test_traversal.py` — BFS/DFS/topo sort
- typical pattern: build small known graph → run algo → assert exact result

## §F — Build / Distribution

- `Cargo.toml` — Rust deps (petgraph, ndarray, rayon, numpy, pyo3)
- `setup.py` + `pyproject.toml` — maturin-based build
- `noxfile.py` — multi-env testing
- pre-built wheels for Linux x86_64/aarch64, macOS, Windows
- `MANIFEST.in` — sdist contents

## §G — Performance Knobs

- `parallel_threshold` for parallelizable algos (rayon)
- node weight as Python object vs as integer index
- `get_node_data` returns reference, not copy
- bulk APIs (`add_nodes_from` etc.) outperform single calls

## §H — Notable Implementation Details

- `StableGraph` keeps gaps; `compact()` not exposed in Python
- node-index stability across `remove_node` is core invariant
- VF2++ implementation in `src/isomorphism/vf2.rs` with call_limit
- topological sort via Kahn's algorithm (`src/dag_algo/`)

## §I — Public Symbols Worth Distilling

- `PyGraph`, `PyDiGraph`, `PyDAG`
- `EdgeList`, `WeightedEdgeList`, `BFSSuccessors`
- `NodeIndices`, `EdgeIndices`
- `Pos2DMapping`, `EigenvectorCentralityMapping`
- `vf2_mapping`, `is_isomorphic_node_match`

## What NOT to focus on (out of scope)

- Tutorial-grade examples (handled by docs-only distill)
- Specific algorithm citations / references
- Visualization styling
- Conda / PyPI publishing automation
