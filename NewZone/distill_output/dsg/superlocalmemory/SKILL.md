# SuperLocalMemory Skill Documentation

SuperLocalMemory is an intelligent, local-first memory system designed for AI assistants and developers. It helps AI tools like Google Gemini, Claude, Cursor, and other IDEs "remember" your past conversations, code decisions, project contexts, and personal preferences, making interactions more coherent and relevant over time.

## When to Use This Skill

Use the `superlocalmemory` skill when you need to:

*   **Store and retrieve information:** Save code snippets, architectural decisions, important facts, or general knowledge and recall it later using natural language or specific queries.
*   **Enhance AI assistant context:** Provide your AI with a continuous, evolving understanding of your projects, tech stack, and workflow.
*   **Understand codebase architecture and design patterns:** Leverage its code analysis capabilities to gain insights into a local codebase.
*   **Find implementation examples and usage patterns:** Quickly locate relevant examples from your past work or analyzed codebases.
*   **Review API documentation extracted from code:** Access documentation automatically generated from your code.
*   **Check configuration patterns and best practices:** Analyze existing configuration files for common patterns and settings.
*   **Explore test examples and real-world usage:** Learn from extracted test cases to understand functionality.
*   **Navigate the codebase structure efficiently:** Get an overview of project documentation and dependencies.
*   **Personalize AI interactions:** Allow the system to learn your preferences and re-rank search results for greater relevance without explicit configuration.
*   **Maintain data privacy and security:** Ensure all your data remains 100% local, private, and under your control.

## Table of Contents

1.  [Description](#superlocalmemory-skill-documentation)
2.  [When to Use This Skill](#when-to-use-this-skill)
3.  [Quick Reference](#quick-reference)
4.  [Core Concepts](#core-concepts)
5.  [Navigating the Documentation](#navigating-the-documentation)
6.  [Detailed Reference Files](#detailed-reference-files)

## Quick Reference

This section provides a quick overview of common tasks and practical code examples for using SuperLocalMemory.

### Basic Memory Operations (CLI)

#### 1. Save a Simple Memory

Save any piece of information for later recall.

```bash
slm remember "Successfully migrated the user authentication service to OAuth2."
```

#### 2. Save an Advanced Memory with Tags, Project, and Importance

Provide more context to make memories easier to find and rank higher.

```bash
slm remember "Critical: Production hotfix deployed for CVE-2023-1234. Requires full rollback plan by EOD." \
  --tags security,hotfix,critical \
  --project my-ecom-api \
  --importance 10
```

#### 3. Perform a Basic Search (Recall)

Find memories using natural language.

```bash
slm recall "authentication service migration"
```

#### 4. Perform an Advanced Search with Filters

Refine your search using limits, minimum relevance scores, tags, and projects.

```bash
slm recall "OAuth2 implementation details" \
  --limit 5 \
  --min-score 0.7 \
  --tags security,oauth \
  --project my-ecom-api
```

### Knowledge Graph Management (CLI)

#### 5. Build or Update the Knowledge Graph with Clustering

Improve search accuracy by identifying relationships and clustering memories into topics. (Requires `python-igraph` and `leidenalg` Python packages for clustering).

```bash
slm build-graph --clustering
```

### Python API Usage

#### 6. Add a Memory Programmatically

Integrate SuperLocalMemory into your Python scripts or applications.

```python
from superlocalmemory.memory_store_v2 import MemoryStoreV2

store = MemoryStoreV2()
store.add_memory("Implemented a new data validation pipeline for user inputs.", tags=["pipeline", "validation"])
print("Memory added successfully.")
```

#### 7. Search Memories Programmatically

Retrieve memories directly from your Python code.

```python
from superlocalmemory.memory_store_v2 import MemoryStoreV2

store = MemoryStoreV2()
results = store.search_memories("data validation pipeline", limit=3)

for r in results:
    print(f"ID: {r.id}, Project: {r.project_name}, Content: {r.content[:70]}...")
```

### System Status (CLI)

#### 8. Check SuperLocalMemory System Status

View current profile, memory count, graph status, and pattern learning status.

```bash
slm status --verbose
```

## Core Concepts

SuperLocalMemory is built on several key principles and intelligent features:

*   **Local-First & Privacy-First:** All data is stored on your local machine (`~/.claude-memory/memory.db`) with zero external API calls, telemetry, or cloud synchronization. This ensures complete privacy and control over your data.
*   **Universal Integration:** It supports seamless integration across 17+ IDEs and AI tools via the Model Context Protocol (MCP), a universal CLI (`slm`), and a powerful Python API. This allows for consistent memory access regardless of your development environment.
*   **Knowledge Graph (GraphRAG):** Automatically constructs a network of entities and relationships from your memories using TF-IDF for entity extraction and Leiden clustering for grouping related memories into topics. This enhances search capabilities by discovering implicit connections.
*   **Pattern Learning:** The system silently learns your technology preferences, current project contexts, and workflow patterns. It uses this knowledge to personalize search result rankings, making the most relevant memories rise to the top over time.
*   **Multi-Profile Workflows:** Supports creating isolated memory contexts (profiles) for different projects, clients, or personal use. This ensures data separation and tailored learning for each context.
*   **Progressive Summarization Compression:** Efficiently manages large numbers of memories by using a tier-based compression system. Older memories are progressively summarized and archived to save disk space and maintain performance, without requiring external LLMs.

## Navigating the Documentation

This skill's documentation is organized into several detailed reference files that provide in-depth information on specific aspects of SuperLocalMemory.

*   **For quick command lookups:** Refer to `CLI-Cheatsheet.md` and `CLI-COMMANDS-REFERENCE.md`.
*   **To understand the system's design:** Explore `Architecture-V2.5.md` and `ARCHITECTURE.md` for comprehensive architectural overviews and design decisions.
*   **For in-depth explanations of intelligent features:** See `Knowledge-Graph-Guide.md` for graph functionality, `Learning-System.md` for personalization, and `Pattern-Learning-Explained.md` (if available, otherwise covered in Learning System).
*   **For configuration options and performance tuning:** Consult `Configuration.md`.
*   **For detailed comparisons with other memory systems:** Read `Comparison-Deep-Dive.md`.
*   **For installation and upgrading:** Use `Installation.md`, `Upgrading-to-v2.7.md`, and `Upgrading-to-v2.8.md`.
*   **For framework-specific integrations (LangChain, LlamaIndex):** Refer to `FRAMEWORK-INTEGRATIONS.md`, `LangChain-Integration.md`, and `LlamaIndex-Integration.md`.
*   **For information on compliance features:** Check `Enterprise-Compliance.md`.
*   **For frequently asked questions:** Consult `FAQ.md`.

When seeking information, start with the most specific relevant file. If a quick answer isn't found, broadening your search to related conceptual files (e.g., from a specific command to the overall system architecture) can provide necessary context.

## Detailed Reference Files

The following documentation files contain comprehensive information about the `superlocalmemory` skill:

*   [`_Footer.md`](references/_Footer.md)
*   [`_Sidebar.md`](references/_Sidebar.md)
*   [`ACCESSIBILITY.md`](references/ACCESSIBILITY.md)
*   [`Advanced-Search.md`](references/Advanced-Search.md)
*   [`Architecture-V2.5.md`](references/Architecture-V2.5.md)
*   [`ARCHITECTURE.md`](references/ARCHITECTURE.md)
*   [`Behavioral-Learning.md`](references/Behavioral-Learning.md)
*   [`CLI-Cheatsheet.md`](references/CLI-Cheatsheet.md)
*   [`CLI-COMMANDS-REFERENCE.md`](references/CLI-COMMANDS-REFERENCE.md)
*   [`Comparison-Deep-Dive.md`](references/Comparison-Deep-Dive.md)
*   [`COMPRESSION-README.md`](references/COMPRESSION-README.md)
*   [`config_patterns.md`](references/config_patterns.md)
*   [`Configuration.md`](references/Configuration.md)
*   [`DEPLOYMENT-CHECKLIST.md`](references/DEPLOYMENT-CHECKLIST.md)
*   [`Enterprise-Compliance.md`](references/Enterprise-Compliance.md)
*   [`FAQ.md`](references/FAQ.md)
*   [`FRAMEWORK-INTEGRATIONS.md`](references/FRAMEWORK-INTEGRATIONS.md)
*   [`Home.md`](references/Home.md)
*   [`Installation.md`](references/Installation.md)
*   [`Knowledge-Graph-Guide.md`](references/Knowledge-Graph-Guide.md)
*   [`LangChain-Integration.md`](references/LangChain-Integration.md)
*   [`Learning-System.md`](references/Learning-System.md)
*   [`LlamaIndex-Integration.md`](references/LlamaIndex-Integration.md)