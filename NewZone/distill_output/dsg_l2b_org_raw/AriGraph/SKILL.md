# AriGraph: Knowledge Graph World Models for LLM Agents

## Description
AriGraph is a skill for analyzing and interacting with the `arigraph-clone` codebase, which implements a novel knowledge graph external memory architecture for Large Language Models (LLMs). This memory, configured as a semantic knowledge graph augmented with episodic vertices and edges, significantly enhances Retrieval-Augmented Generation (RAG) performance, particularly in text-based games. The `arigraph-clone` project serves as a key component of the Ariadne agent, designed to navigate the challenges of text-based games within the [TextWorld](https://github.com/microsoft/TextWorld) framework.

This skill provides comprehensive insights into the codebase's architecture, design patterns, configuration patterns, and project documentation generated from code analysis.

## When to Use This Skill
Use this skill when you need to:
- Understand the codebase architecture and design patterns, especially related to knowledge graph construction and memory management for LLMs.
- Find implementation examples and usage patterns for building and querying dual-class memory nodes (episodic vs. semantic).
- Review API documentation extracted from the code.
- Check configuration patterns, particularly how TextWorld environments are defined and managed.
- Explore test examples and real-world usage of AriGraph in TextWorld and QA tasks.
- Navigate the codebase structure efficiently to understand its components and their interactions.
- Gain insight into how AriGraph improves LLM agent performance in complex, dynamic environments.

## Key Concepts

### Dual-Class Memory Nodes (Episodic vs. Semantic Memory)
At the core of AriGraph's memory architecture is a novel organization of knowledge graph nodes into two distinct categories, designed to capture different types of an LLM agent's experience:

*   **Episodic Memory**: These nodes store specific event memories, encompassing concrete observations, precise timestamps, and the situational context in which events occurred. They capture the unique, sequential experiences of the agent.
*   **Semantic Memory**: These nodes hold generalized knowledge, factual information, entity properties, and abstract concepts. They represent the consolidated, background understanding derived from various experiences.

These two classes of nodes are designed to coexist and interact. Crucially, "bridging edges" connect episodic nodes to semantic entities, allowing specific experiences to inform and be understood within the broader context of general knowledge. Gemini should prioritize understanding *how these nodes are organized, how they reference each other, and how they are queried by an LLM agent* to enhance reasoning and retrieval in dynamic environments.

### Graph Operations
AriGraph facilitates various operations on its knowledge graph to maintain and leverage the stored memory:

*   **Triplet Extraction**: This process identifies (subject, predicate, object) triplets from text, which are then used to add new nodes and edges to the graph.
*   **Node Merging**: To avoid redundancy and maintain a coherent knowledge base, nodes representing the same real-world entity mentioned at different times are merged.
*   **Node Updating**: The properties and relationships of existing nodes can be updated as new information or corrected facts emerge.
*   **Retrieval**: Advanced retrieval mechanisms, including graph traversal and subgraph extraction, are employed to fetch the most relevant working memory for an LLM's query.

### Agent Query Patterns
The AriGraph memory architecture supports sophisticated query patterns adapted to the LLM agent's current task or state:

*   **Exploration Mode**: Queries might be designed to discover new entities, map unknown areas, or gather general information about the environment.
*   **Exploitation Mode**: Queries are typically more targeted, aiming to retrieve specific facts, action sequences, or critical information to achieve a defined goal.
*   **Working Memory Management**: The system dynamically selects and formats a "working set" of relevant memory nodes, managing its size and content to serve as concise, contextually rich input for the LLM.

## ⚡ Quick Reference

### 🚀 Setting up the AriGraph Environment

These commands are crucial for preparing your system to run the AriGraph project, especially given its dependencies on the TextWorld framework.

#### Install System Dependencies (Debian/Ubuntu)
```bash
sudo apt update && sudo apt install build-essential libffi-dev python3-dev curl git
```

#### Install System Dependencies (macOS)
```bash
brew install libffi curl git
```

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 📄 Identifying Configuration Files

AriGraph utilizes numerous JSON files for configuration, primarily defining various TextWorld environments and QA datasets. These examples show how to identify key characteristics of these configuration files.

#### General Game Configuration File
```
# Path: envs\cook\game.json
# Type: json
# Purpose: general_configuration
# Settings: 47
```
*This identifies a typical configuration file for a TextWorld cooking environment, detailing its path, file type, general purpose, and the number of settings it contains.*

#### Large QA Dataset Configuration File
```
# Path: qa_data\hotpot_dev_distractor_v1.json
# Type: json
# Purpose: general_configuration
# Settings: 51835
```
*This identifies a large JSON file used for QA testing, indicating it contains a significant amount of configuration or dataset-like settings, likely defining a complex test scenario.*

### ✍️ Citing AriGraph
If you find the AriGraph work useful in your research or projects, please consider citing the accompanying paper using the BibTeX entry below.

```markdown
@misc{anokhin2024arigraphlearningknowledgegraph,
      title={AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents},
      author={Petr Anokhin and Nikita Semenov and Artyom Sorokin and Dmitry Evseev and Mikhail Burtsev and Evgeny Burnaev},
      year={2024},
      eprint={2407.04363},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2407.04363},
}
```

## 📚 Table of Contents

*   [Description](#description)
*   [When to Use This Skill](#when-to-use-this-skill)
*   [Key Concepts](#key-concepts)
    *   [Dual-Class Memory Nodes (Episodic vs. Semantic Memory)](#dual-class-memory-nodes-episodic-vs-semantic-memory)
    *   [Graph Operations](#graph-operations)
    *   [Agent Query Patterns](#agent-query-patterns)
*   [⚡ Quick Reference](#️-quick-reference)
    *   [🚀 Setting up the AriGraph Environment](#-setting-up-the-arigraph-environment)
    *   [📄 Identifying Configuration Files](#-identifying-configuration-files)
    *   [✍️ Citing AriGraph](#️-citing-arigraph)
*   [Codebase Structure](#codebase-structure)
*   [Configuration Patterns](#configuration-patterns)
*   [Project Documentation Overview](#project-documentation-overview)
*   [Available Reference Files](#available-reference-files)
*   [Practical Usage Guidance for Gemini](#practical-usage-guidance-for-gemini)

## Codebase Structure

The `arigraph-clone` repository is organized into several key directories, each serving a specific purpose in the AriGraph system:

*   **agents**: Contains the implementations of various LLM agents, such as `GPTagent`, which interact with the TextWorld environments using AriGraph.
*   **envs**: Holds TextWorld files responsible for defining and loading diverse game environments used for evaluation, including Treasure Hunt, Cleaning, and Cooking tasks.
*   **qa_data**: Stores datasets for Question Answering (QA) tasks, such as MuSiQue and HotpotQA, used to benchmark AriGraph's performance in different domains.
*   **graphs**: Implements the core knowledge graph structures, including the base `TripletGraph` (found in `parent_graph.py`) and other specialized graph types that inherit from it.
*   **logs**: Stores detailed execution logs from various agent runs, useful for debugging and performance analysis.
*   **prompts**: Contains the collection of prompts used within the LLM agent pipelines for decision-making and interaction with the knowledge graph.
*   **src** and **utils**: House service classes and general utility functions that support the overall functionality of the AriGraph system.

Other top-level Python files typically contain pipelines for individual agents and code for running games in interactive console mode.

## Configuration Patterns

The codebase extensively uses JSON files for various configurations, primarily defining numerous TextWorld environments and specific QA datasets.

*   **Total Configuration Files Analyzed**: 22
*   **Total Settings Across All Files**: 52672
*   **Detected Patterns**: 0 (No high-confidence design patterns were explicitly detected within the configuration files, though they exhibit structured definitions).
*   **Configuration Types**: All analyzed configuration files are of type `json`, predominantly serving a `general_configuration` purpose.

Specific examples of analyzed configuration files include:
*   `envs\clean_3x3\clean_3x3_default.json` (17 settings) - A default configuration for a cleaning environment.
*   `envs\cook\game.json` (47 settings) - A general configuration for a cooking environment.
*   `qa_data\hotpot_dev_distractor_v1.json` (51835 settings) - A large configuration, likely representing a dataset or complex test scenario for QA tasks.

For a complete and detailed list of all configuration files and their metadata, refer to the `references/config_patterns/` section within the skill's file structure.

## Project Documentation Overview

The primary and most comprehensive piece of project documentation is the `README.md` file, which has been extracted and made available through this skill.

*   **Total Documentation Files**: 1
*   **Categories**: 1 (General Project Overview)

The `README.md` provides a rich overview, covering:
*   The fundamental concept of AriGraph as an external memory architecture for LLMs.
*   Its specific application and integration as the Ariadne agent within the TextWorld framework.
*   Detailed performance results and comparative analyses against various baselines in both TextWorld games (Treasure Hunt, Cleaning, Cooking) and QA tasks (MuSiQue, HotpotQA).
*   Essential system and Python requirements for setting up and running the project locally.
*   A clear and logical breakdown of the repository's directory structure.
*   The academic citation information for the associated research paper.

To access the full content of the `README.md` file and any other extracted markdown documentation, please refer to the `references/documentation/` section.

## Available Reference Files

This skill is complemented by detailed reference documentation files, which offer deeper insights into specific analyses performed on the codebase:

*   **Dependencies**: `references/dependencies/` - Contains analysis and visualizations of the project's dependency graph.
*   **Patterns**: `references/patterns/` - Details any design patterns detected within the codebase, such as instances of the "Adapter" pattern.
*   **Configuration**: `references/config_patterns/` - Provides a comprehensive report on all analyzed configuration files, including their paths, types, purposes, and setting counts.
*   **Documentation**: `references/documentation/` - Houses extracted project documentation, including the full `README.md` file.

## Practical Usage Guidance for Gemini

To effectively utilize this documentation and answer user queries about AriGraph, consider the following strategies:

*   **For High-Level Understanding**: Begin by reading the "Description" and "Key Concepts" sections. These provide the foundational knowledge of what AriGraph is and its core architectural principles (e.g., dual-class memory nodes).
*   **For Setup and Environment Preparation**: Refer directly to the "⚡ Quick Reference" section for actionable commands related to installing system and Python dependencies.
*   **For Codebase Navigation**: Consult the "Codebase Structure" section to understand the project's directory layout, which is useful for locating specific components like `agents`, `graphs`, or `envs`.
*   **For Specific File Information (e.g., config, docs)**: If a user asks about a particular configuration file or the project's main documentation, first check the "Configuration Patterns" or "Project Documentation Overview" sections for summaries. Then, point to the respective paths within "Available Reference Files" (e.g., `references/config_patterns/` or `references/documentation/`) for the complete details.
*   **For Architectural Insights**: When asked about how the memory works, how agents are organized, or how graph operations are performed, draw heavily from the "Key Concepts" section.
*   **For Research Context and Performance**: The "Project Documentation Overview" highlights the `README.md` content, which includes detailed performance metrics and the academic citation. This is essential for questions about research contributions or comparative results.
*   **Prioritize Conciseness**: Extract the most relevant information without being overly verbose. Use bullet points and code blocks effectively.

By following this guidance, you can efficiently extract and synthesize information to provide accurate, comprehensive, and actionable responses regarding the AriGraph skill.