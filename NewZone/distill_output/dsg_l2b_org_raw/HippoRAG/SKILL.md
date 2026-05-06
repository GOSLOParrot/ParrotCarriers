# HippoRAG Skill Documentation

## Description

The HippoRAG skill provides local codebase analysis and documentation, with a primary focus on the core mechanisms of the HippoRAG project itself. This skill is designed to help users understand the "hippocampal-indexed memory graph organization method," which defines what nodes and edges are, and how Personalized PageRank is used for knowledge graph construction, retrieval, and incremental updates. It specifically avoids distilling information about LLM calls, API servers, or benchmark reproduction, emphasizing the core RAG (Retrieval-Augmented Generation) indexing and retrieval components.

**Path:** `C:\Users\Bin\AppData\Local\Temp\hipporag-clone`
**Analysis Depth:** surface

## Table of Contents

-   [When to Use This Skill](#when-to-use-this-skill)
-   [Key Concepts](#key-concepts)
    -   [Knowledge Graph Organization](#knowledge-graph-organization)
    -   [Personalized PageRank Retrieval](#personalized-pagerank-retrieval)
    -   [Continuous Integration and Incremental Updates](#continuous-integration-and-incremental-updates)
-   [⚡ Quick Reference](#-quick-reference)
-   [Codebase Statistics](#codebase-statistics)
-   [⚙️ Configuration Patterns](#️-configuration-patterns)
-   [📖 Project Documentation](#-project-documentation)
-   [📚 Available References](#-available-references)

## When to Use This Skill

Use this skill when you need to:
-   Understand the core architecture and design principles of HippoRAG's knowledge graph.
-   Explore the mechanics of HippoRAG's retrieval methods, particularly Personalized PageRank.
-   Learn about HippoRAG's approach to incremental knowledge graph updates.
-   Review configuration patterns and project-specific documentation.
-   Navigate the codebase structure to understand its key components.

## Key Concepts

HippoRAG is centered around an innovative knowledge graph structure and retrieval mechanism. The skill's analysis focuses on these core ideas, which are essential for understanding the project.

### Knowledge Graph Organization

The HippoRAG knowledge graph uses specific types of nodes and edges to represent information extracted from text.

-   **OpenIE Triple (`(subject, predicate, object)`)**: These triples are the fundamental building blocks, serving as the primary source for candidate nodes and edges in the graph.
-   **Entity Node (`entity node`)**: Represents core conceptual entities, akin to "cortical concepts."
-   **Passage Node (`passage node`)**: Acts as a pointer to specific episodic instances or text segments from which information was extracted.
-   **Synonym Edge (`synonym edge`)**: Connects nodes that are synonymous or co-referential, facilitating node merging and deduplication based on embedding similarity.
-   **Relation Edge (`relation edge`)**: Represents the predicate relationships between subject and object entities as identified by OpenIE triples.
-   **Node Storage**: Involves storing node embeddings and pointers to source information, crucial for linking and deduplication across documents.

### Personalized PageRank Retrieval

HippoRAG employs a Personalized PageRank algorithm for retrieving relevant information, simulating a "subconscious associative" recall.

-   **Personalized PageRank (`personalized_pagerank`)**: A diffusion activation process initiated from query-triggered seed nodes.
-   **Damping Factor (`damping factor`)**: A parameter controlling the influence of directly connected nodes versus the overall graph structure during diffusion.
-   **Seed Node Selection (`seed node selection`)**: The process of identifying initial nodes in the graph that are relevant to a given query, serving as starting points for PageRank diffusion.
-   **Restart Probability (`restart probability`)**: The likelihood of the random walk returning to the initial seed nodes during the PageRank iteration, influencing the scope of diffusion.
-   **Top-K Retrieval (`top-k retrieval`)**: The final step where the highest-ranked nodes (after PageRank convergence) are selected as the most relevant results.

### Continuous Integration and Incremental Updates

HippoRAG is designed to continually integrate new information and incrementally update its knowledge graph.

-   **Index Continual Update (`index_continual_update`)**: The process of incrementally updating the knowledge index as new documents become available.
-   **OpenIE on New Docs (`OpenIE on new docs`)**: Applying the OpenIE triple extraction process to newly added documents to identify new candidate nodes and edges.
-   **Node Merge Across Documents (`node merge across documents`)**: The mechanism for merging and linking entity nodes that refer to the same concept but originate from different documents, ensuring a coherent and non-redundant knowledge graph.

## ⚡ Quick Reference

This section provides practical examples of structured information and common patterns found within the HippoRAG project documentation.

### 1. HippoRAG Prompt Template Structure

This example from the project's `README.md` shows the expected structure for defining prompt templates.

```python
# A prompt template can be:
# - A str with or without ${}-like placeholders for filling values (will be converted with Template(...)) OR
# - A Template instance OR
# - A chat history (List[dict[str, Any]]) with each dict is like {"role": "system"/"user"/"assistant", "content": the above two option items}.
```

### 2. HippoRAG Contribution Workflow

This snippet from `CONTRIBUTING.md` outlines the standard steps for contributing code to the HippoRAG project.

```bash
# How to Contribute to HippoRAG:
1. Fork the repository and clone it to your local machine.
2. Create a new branch for your contribution: git checkout -b my-contribution
3. Make your changes and ensure tests pass.
4. Commit your changes: git commit -m "Add my contribution"
5. Push your changes: git push origin my-contribution
6. Open a pull request to the main repository.
```

### 3. Example Configuration File Summary (OpenIE Results)

This structured data example from `config_patterns.md` describes a JSON configuration file generated during OpenIE (Open Information Extraction) analysis with a specific LLM.

```json
{
  "file": "outputs\\musique\\openie_results_ner_gpt-4o-mini.json",
  "type": "json",
  "purpose": "general_configuration",
  "settings": 3
}
```

### 4. Example Configuration File Summary (Large Dataset Corpus)

Another structured data example from `config_patterns.md`, detailing a large dataset corpus file used for reproduction purposes.

```json
{
  "file": "reproduce\\dataset\\hotpotqa_corpus.json",
  "type": "json",
  "purpose": "general_configuration",
  "settings": 29433
}
```

### 5. Example Configuration File Summary (DSPy Prompt Filter)

This example from `config_patterns.md` illustrates a configuration file related to DSPy prompts, specifically for a filter.

```json
{
  "file": "src\\hipporag\\prompts\\dspy_prompts\\filter_llama3.3-70B-Instruct.json",
  "type": "json",
  "purpose": "general_configuration",
  "settings": 7
}
```

### 6. Key Concept Definition: OpenIE Triple

From `skill_seeker_focus.md`, this defines a fundamental concept in HippoRAG's knowledge graph construction.

```markdown
**OpenIE Triple (`OpenIE triple`)**: (subject, predicate, object) — This foundational structure serves as the source for candidate nodes and edges in the knowledge graph.
```

## Codebase Statistics

**Languages:** (Not specified in analyzed files)

**Analysis Performed:**
-   ✅ API Reference (C2.5)
-   ✅ Dependency Graph (C2.6)
-   ✅ Design Patterns (C3.1)
-   ✅ Test Examples (C3.2)
-   ✅ Configuration Patterns (C3.4)
-   ✅ Architectural Analysis (C3.7)
-   ✅ Project Documentation (C3.9)

## ⚙️ Configuration Patterns

*From C3.4 configuration analysis*

**Configuration Files Analyzed:** 11
**Total Settings:** 89013
**Patterns Detected:** 0

**Configuration Types:**
-   unknown: 11 files (All identified configuration files are JSON, serving general configuration purposes for datasets and prompt filtering.)

*See `references/config_patterns/` for detailed configuration analysis, including specific files like `outputs\musique\openie_results_ner_gpt-4o-mini.json`, `reproduce\dataset\2wikimultihopqa.json`, and `src\hipporag\prompts\dspy_prompts\filter_llama3.3-70B-Instruct.json`.*

## 📖 Project Documentation

*Extracted from markdown files in the project (C3.9)*

**Total Documentation Files:** 5
**Categories:** 4

### Overview

-   **README.md** (`README.md`): General information about prompt templates.

### Contributing

-   **CONTRIBUTING.md** (`CONTRIBUTING.md`): Guidelines for contributing to the HippoRAG project.

### Other

-   **README.md** (`reproduce\README.md`): Documentation specific to reproduction steps.
-   **README.md** (`src\hipporag\evaluation\README.md`): Documentation related to evaluation processes.

### Templates

-   **README.md** (`src\hipporag\prompts\templates\README.md`): Information pertaining to prompt templates within the project.

*See `references/documentation/` for all project documentation files, including detailed contribution guides and prompt template definitions.*

## 📚 Available References

This skill includes detailed reference documentation to provide deeper insights into the HippoRAG project:

-   **Dependencies**: `references/dependencies/` - Dependency graph and analysis (not detailed in current references).
-   **Patterns**: `references/patterns/` - Detected design patterns (not detailed in current references).
-   **Configuration**: `references/config_patterns/` - Detailed analysis of configuration files and detected patterns.
-   **Documentation**: `references/documentation/` - Comprehensive project documentation, including READMEs and contribution guides.

---

**Generated by Skill Seeker** | Codebase Analyzer with C3.x Analysis