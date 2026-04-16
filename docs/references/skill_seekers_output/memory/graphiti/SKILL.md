# Graphiti Skill Documentation

This document provides comprehensive information and practical guidance for using the `graphiti` skill effectively with Google Gemini. Graphiti is an open-source Python framework designed for building and querying temporal context graphs for AI agents. Unlike static knowledge graphs, Graphiti tracks how facts change over time, maintains provenance to source data, and supports both prescribed and learned ontologies, making it ideal for agents operating on evolving, real-world data.

Use this skill when you need to:
*   Understand the codebase architecture and design patterns.
*   Find implementation examples and usage patterns for building temporal context graphs.
*   Review API documentation extracted from code.
*   Check configuration patterns and best practices for Graphiti and its integrations.
*   Explore test examples and real-world usage of Graphiti functionalities.
*   Navigate the codebase structure efficiently.
*   Integrate Graphiti into AI agent workflows for dynamic, context-aware memory.
*   Develop AI agent memory with temporal awareness and explicit provenance.
*   Manage evolving data where facts change over time and history must be preserved.
*   Implement multi-tenant or session-isolated context graphs using `group_id`.
*   Define custom entity and relationship types to suit specific domain requirements (e.g., for ParrotCarriers).
*   Perform efficient, hybrid retrieval (semantic, keyword, graph traversal) of context for LLMs.
*   Self-host a lightweight graph database backend like FalkorDB for resource-constrained environments.

## Table of Contents
1.  [Quick Reference](#quick-reference)
    *   [Design Patterns](#design-patterns)
    *   [Key Code Examples](#key-code-examples)
2.  [Key Concepts](#key-concepts)
    *   [Temporal Context Graphs](#temporal-context-graphs)
    *   [Entities, Facts, and Episodes](#entities-facts-and-episodes)
    *   [Prescribed & Learned Ontology](#prescribed--learned-ontology)
    *   [Hybrid Retrieval](#hybrid-retrieval)
    *   [Group ID for Multi-Tenancy](#group-id-for-multi-tenancy)
3.  [Practical Usage Guidance](#practical-usage-guidance)
    *   [Getting Started with Graphiti](#getting-started-with-graphiti)
    *   [Adding Episodes (Conversation Turns)](#adding-episodes-conversation-turns)
    *   [Defining Custom Entity Types](#defining-custom-entity-types)
    *   [Managing Data with Group IDs](#managing-data-with-group-ids)
    *   [Searching and Retrieving Context](#searching-and-retrieving-context)
    *   [Understanding Temporal Validity](#understanding-temporal-validity)
    *   [Self-Hosting with FalkorDB](#self-hosting-with-falkordb)
4.  [Reference Documentation Summaries](#reference-documentation-summaries)
    *   [Architectural Design & Overview](#architectural-design--overview)
    *   [Configuration & Deployment](#configuration--deployment)
    *   [Development & Contribution](#development--contribution)
    *   [Internal Tools & Specifications](#internal-tools--specifications)
    *   [Code Examples & How-To Guides](#code-examples--how-to-guides)

---

## Quick Reference

This section provides a quick overview of detected design patterns and highly practical code examples extracted directly from the Graphiti codebase tests. These examples demonstrate common tasks and functionalities within the Graphiti framework, ranging from basic data handling to more complex graph operations and concurrent access.

### Design Patterns

*From codebase analysis (confidence > 0.7)*

-   **Adapter**: 3 instances
-   **Factory**: 3 instances

*Total: 6 high-confidence patterns*

### Key Code Examples

**1. Workflow: Ensure thread-safe token usage tracking.**
This example tests the `TokenUsageTracker` for safe concurrent access from multiple threads when recording token usage. Essential for high-concurrency LLM interactions.

```python
from concurrent.futures import ThreadPoolExecutor
from graphiti_core.llm_client.token_tracker import TokenUsageTracker

tracker = TokenUsageTracker()
num_threads = 10
calls_per_thread = 100

def record_tokens(thread_id):
    for _ in range(calls_per_thread):
        tracker.record(f'prompt_{thread_id}', 10, 5)

with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [executor.submit(record_tokens, i) for i in range(num_threads)]
    for f in futures:
        f.result()

usage = tracker.get_usage()
assert len(usage) == num_threads
total = tracker.get_total_usage()
expected_input = num_threads * calls_per_thread * 10
expected_output = num_threads * calls_per_thread * 5
assert total.input_tokens == expected_input
assert total.output_tokens == expected_output
```

**2. Workflow: Convert `datetime` objects within lists and tuples for FalkorDB.**
This snippet demonstrates how `convert_datetimes_to_strings` from the FalkorDB driver handles `datetime` objects in nested data structures, ensuring compatibility with the database.

```python
from datetime import datetime, timezone
from graphiti_core.driver.falkordb_driver import convert_datetimes_to_strings

test_datetime = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
input_list = ['test', test_datetime, ['nested', test_datetime]]
result_list = convert_datetimes_to_strings(input_list)
assert result_list[0] == 'test'
assert result_list[1] == test_datetime.isoformat()
assert result_list[2][1] == test_datetime.isoformat()

input_tuple = ('test', test_datetime)
result_tuple = convert_datetimes_to_strings(input_tuple)
assert isinstance(result_tuple, tuple)
assert result_tuple[0] == 'test'
assert result_tuple[1] == test_datetime.isoformat()
```

**3. Workflow: Verify edge type signatures across multiple node pairs.**
This example tests a fix ensuring that edge types used between different node pairs correctly preserve all their defined signatures within the `edge_type_signatures_map`, crucial for maintaining complex graph schemas.

```python
from pydantic import BaseModel
from graphiti_core.edges import InterpersonalRelationship, LocatedIn

edge_type_map: dict[tuple[str, str], list[str]] = {('Person', 'Person'): ['InterpersonalRelationship'], ('Person', 'Entity'): ['InterpersonalRelationship'], ('Person', 'City'): ['LocatedIn'], ('Entity', 'City'): ['LocatedIn']}
edge_types: dict[str, type[BaseModel]] = {'InterpersonalRelationship': InterpersonalRelationship, 'LocatedIn': LocatedIn}
edge_type_signatures_map: dict[str, list[tuple[str, str]]] = {}

for signature, edge_type_names in edge_type_map.items():
    for edge_type in edge_type_names:
        if edge_type not in edge_type_signatures_map:
            edge_type_signatures_map[edge_type] = []
        edge_type_signatures_map[edge_type].append(signature)

assert 'InterpersonalRelationship' in edge_type_signatures_map
interpersonal_signatures = edge_type_signatures_map['InterpersonalRelationship']
assert len(interpersonal_signatures) == 2
assert ('Person', 'Person') in interpersonal_signatures
assert ('Person', 'Entity') in interpersonal_signatures
```

**4. Workflow: Detect "dense" text content with many proper nouns.**
This example demonstrates a utility function `_text_likely_dense` used for content chunking. It helps identify text segments rich in entities, which can be useful for optimized information extraction.

```python
from graphiti_core.utils import content_chunking, estimate_tokens
from unittest.mock import MagicMock

# Mock monkeypatch to set CHUNK_DENSITY_THRESHOLD for testing
class MockMonkeypatch:
    def setattr(self, obj, name, value):
        setattr(obj, name, value)
monkeypatch = MockMonkeypatch()

monkeypatch.setattr(content_chunking, 'CHUNK_DENSITY_THRESHOLD', 0.01)
text = 'Alice met Bob at Acme Corp. Then Carol and David joined them. '
text += 'Eve from Globex introduced Frank and Grace. '
text += 'Later Henry and Iris arrived from Initech. '
text = text * 10 # Repeat to make it dense
tokens = estimate_tokens(text)
assert content_chunking._text_likely_dense(text, tokens)
```

**5. Workflow: Resolve entity duplicates with exact similarity matches.**
This test shows how `_resolve_with_similarity` identifies and updates the resolution state when an exact match for an extracted entity is found among candidates during the deduplication process.

```python
from graphiti_core.nodes import EntityNode
from graphiti_core.utils.maintenance.dedup_helpers import _build_candidate_indexes, _resolve_with_similarity, DedupResolutionState

candidate = EntityNode(name='Charlie Parker', group_id='group', labels=['Entity'])
extracted = EntityNode(name='Charlie Parker', group_id='group', labels=['Entity'])
indexes = _build_candidate_indexes([candidate])
state = DedupResolutionState(resolved_nodes=[None], uuid_map={}, unresolved_indices=[])

_resolve_with_similarity([extracted], indexes, state)

assert state.resolved_nodes[0].uuid == candidate.uuid
assert state.uuid_map[extracted.uuid] == candidate.uuid
assert state.unresolved_indices == []
assert state.duplicate_pairs == [(extracted, candidate)]
```

---

## Key Concepts

### Temporal Context Graphs
A core concept in Graphiti, a temporal context graph is a dynamic knowledge structure that captures entities, relationships (facts), and their evolution over time. Each fact has a validity window, tracking when it became true and when it was superseded, enabling historical queries and dynamic understanding.

### Entities, Facts, and Episodes
*   **Entities (nodes)**: Represent people, products, concepts, or policies, with summaries that update over time.
*   **Facts/Relationships (edges)**: Triplets (e.g., Entity → Relationship → Entity) with temporal validity windows.
*   **Episodes (provenance)**: The raw, ingested data that serves as the ground truth stream. Every derived fact and entity traces back to its originating episode.

### Prescribed & Learned Ontology
Graphiti allows developers to define custom entity and edge types using Pydantic models (**prescribed ontology**) for structured data. It also supports structure emerging from unstructured data (**learned ontology**), offering flexibility as your understanding of the data evolves.

### Hybrid Retrieval
Graphiti employs a powerful hybrid retrieval strategy combining:
*   **Semantic embeddings**: For conceptual similarity.
*   **Keyword (BM25)**: For exact term matching.
*   **Graph traversal**: For exploring relationships and proximity.
This combination ensures low-latency, high-precision context retrieval without over-reliance on LLM summarization.

### Group ID for Multi-Tenancy
The `group_id` parameter allows for partitioning graph data. This is crucial for multi-tenant applications or for isolating context per user, session, or specific domain, ensuring that searches and operations are scoped correctly. For ParrotCarriers, this is key to isolating customer interaction histories.

---

## Practical Usage Guidance

This section focuses on practical aspects of using Graphiti, particularly aligned with common AI agent use cases like conversation analysis and personalized context.

### Getting Started with Graphiti
To begin using Graphiti, you typically install it with your chosen database backend (e.g., FalkorDB) and LLM/embedding providers (e.g., Google Gemini).

```bash
pip install graphiti-core[falkordb,google-genai]
# or
uv add "graphiti-core[falkordb,google-genai]"
```

Then, initialize the `Graphiti` client:

```python
from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig

# Replace with your actual API key and database connection details
google_api_key = "<YOUR_GOOGLE_API_KEY>"

# Initialize FalkorDB driver (recommended for ParrotCarriers' 2C8G constraint)
falkordb_driver = FalkorDriver(host="localhost", port=6379, database="my_agent_graph")

# Initialize Gemini clients for LLM, Embedder
gemini_llm_client = GeminiClient(config=LLMConfig(api_key=google_api_key, model="gemini-2.5-flash"))
gemini_embedder_client = GeminiEmbedder(config=GeminiEmbedderConfig(api_key=google_api_key, embedding_model="embedding-001"))

# Initialize Graphiti with your driver and LLM/Embedder clients
graphiti_instance = Graphiti(
    graph_driver=falkordb_driver,
    llm_client=gemini_llm_client,
    embedder=gemini_embedder_client
)

# Ensure indices and constraints are built for optimal performance
await graphiti_instance.graph_ops.build_indices_and_constraints()
```

### Adding Episodes (Conversation Turns)
The `add_episode` method is central to ingesting new information into your context graph. It processes raw data (like a conversation turn) and extracts entities and facts, linking them back to the episode as provenance. This is crucial for building memory for AI agents like ParrotCarriers.

```python
from graphiti_core import Graphiti
from graphiti_core.graphiti_types import EpisodeType

# Assuming graphiti_instance is already initialized as above

user_id = "user_123" # Example group_id for a user (e.g., ParrotCarriers customer ID)
conversation_turn = "The user mentioned they prefer black coffee and often bikes to work."

await graphiti_instance.add_episode(
    text=conversation_turn,
    episode_type=EpisodeType.text,
    group_id=user_id,
    source="conversation"
)
print(f"Episode added for user {user_id}: '{conversation_turn}'")

# Example for a structured message list (e.g., from a chat)
message_list_episode = [
    {"role": "user", "content": "I need a new laptop for programming."},
    {"role": "assistant", "content": "What kind of programming do you do? Python, Java, web development?"}
]
await graphiti_instance.add_episode(
    message_list=message_list_episode,
    episode_type=EpisodeType.message_list,
    group_id=user_id,
    source="chat_session"
)
print(f"Message list episode added for user {user_id}")
```

### Defining Custom Entity Types
To tailor the graph to your specific domain (e.g., ParrotCarriers' shipments, customers, products), you can define custom entity types using Pydantic models. This allows Graphiti to extract and manage domain-specific entities with precise schemas.

```python
from pydantic import Field
from graphiti_core.nodes import EntityNode, Relationship
from typing import Literal

# Define a custom entity type for ParrotCarriers: 'Shipment'
class Shipment(EntityNode):
    labels: Literal['Shipment'] = 'Shipment'
    tracking_number: str = Field(description="Unique tracking number for the shipment")
    destination: str = Field(description="Final destination address or city")
    status: Literal['pending', 'in_transit', 'delivered', 'delayed'] = 'pending'

# Define a custom edge type: 'ContainsItem'
class ContainsItem(Relationship):
    type: Literal['CONTAINS_ITEM'] = 'CONTAINS_ITEM' # Note: Updated from CONTAINSItem for consistency
    quantity: int = Field(description="Number of items contained in the shipment")

# Initialize Graphiti with custom types (example - ensure these are registered during client init)
# graphiti_instance = Graphiti(
#     ...,
#     custom_entity_types={"Shipment": Shipment},
#     custom_edge_types={"CONTAINS_ITEM": ContainsItem} # Use the type Literal value as the key
# )
```

### Managing Data with Group IDs
The `group_id` parameter is essential for implementing multi-partition strategies, allowing you to isolate data for different users, sessions, or contexts (e.g., a specific `ParrotCarriers` customer's interaction history). Always provide a `group_id` when adding episodes or performing searches to maintain data isolation.

```python
# When adding an episode (as shown above)
await graphiti_instance.add_episode(text="User preference: I always ship with express delivery.", group_id="customer_alice", source="chat")

# When searching for facts or entities
from graphiti_core.search import SearchConfig
search_results = await graphiti_instance.search(
    query="what are Alice's shipping preferences?",
    group_ids=["customer_alice"], # Specify the group_id for scoped search
    config=SearchConfig(limit=5)
)
```

### Searching and Retrieving Context
The `search` method is the primary way to retrieve relevant context from the graph. You can specify a query, `group_ids`, and `SearchConfig` to fine-tune your retrieval using hybrid methods, making it ideal for injecting context into an AI agent's "Brain."

```python
from graphiti_core.search import SearchConfig, SearchType

# Assuming graphiti_instance is initialized and has data
customer_id = "customer_alice"

# Example: Hybrid search for context related to a query
search_query = "What is the status of the new laptop order?"
search_results = await graphiti_instance.search(
    query=search_query,
    group_ids=[customer_id],
    config=SearchConfig(
        search_type=SearchType.HYBRID, # Combines semantic, keyword, and graph traversal
        limit=5,
        min_score=0.7 # Minimum relevance score for results
    )
)

print(f"Search results for '{search_query}' (User: {customer_id}):")
for result in search_results:
    print(f"- {result.text[:100]}...") # Print first 100 characters of result text
```

### Understanding Temporal Validity
Graphiti automatically handles the temporal validity of facts. When new information contradicts or supersedes old information, the old facts are marked as invalid (not deleted), preserving a complete history. Queries can then be made "as of" a specific time to retrieve historical context.

```python
import datetime

# Add an initial fact
await graphiti_instance.add_episode(
    text="John Doe lives in New York.", group_id="user_john", source="user_profile"
)
# Later, John moves
await graphiti_instance.add_episode(
    text="John Doe moved to San Francisco.", group_id="user_john", source="user_profile"
)

# A query for John's current residence will return San Francisco.
current_facts = await graphiti_instance.search(
    query="Where does John Doe live?", group_ids=["user_john"]
)
print(f"Current facts about John: {current_facts[0].text if current_facts else 'None'}")

# To retrieve facts valid at a past point in time:
past_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30)
past_facts = await graphiti_instance.search(
    query="Where did John Doe live?", group_ids=["user_john"], reference_time=past_time
)
print(f"Past facts about John (as of {past_time.date()}): {past_facts[0].text if past_facts else 'None'}")
```

### Self-Hosting with FalkorDB
For lighter deployments or environments with memory constraints (e.g., a 2C8G constraint, as might be relevant for ParrotCarriers), FalkorDB is a suitable graph database backend for self-hosting. It can be run easily via Docker.

```bash
docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest
```
Then, configure your `Graphiti` instance to use `FalkorDriver` as shown in the "Getting Started" example above. This is often preferred in resource-constrained environments over more heavyweight alternatives like Neo4j.

---

## Reference Documentation Summaries

### Architectural Design & Overview
*   **README.md**: Provides a high-level overview of Graphiti, its purpose in building temporal context graphs for AI agents, core concepts (entities, facts, episodes), and comparisons with Zep and GraphRAG. It also includes installation instructions and quick start examples.
*   **AGENTS.md**: Details the project's structure, module organization, development commands (`uv sync`, `make format`, `make lint`, `make test`), coding style, naming conventions, and testing guidelines.
*   **CLAUDE.md**: Offers specific guidance for Claude Code AI when working with the repository, including project overview, development commands, code architecture (`graphiti_core/`, `server/`, `mcp_server/`), testing, and LLM provider support details.
*   **OTEL_TRACING.md**: Explains how to integrate OpenTelemetry distributed tracing into Graphiti applications for better observability.
*   **driver-operations-redesign.md**: A draft specification detailing the redesign of Graphiti's driver operations, aiming for clearer interfaces, better separation of concerns, and improved testability. It outlines the architecture, design decisions, and specific operations ABCs for various graph elements.

### Configuration & Deployment
*   **config_patterns.md**: A report identifying 49 configuration files and 5124 settings across the project, categorized by purpose (e.g., `environment_configuration`, `docker_configuration`, `package_configuration`, `database_configuration`). Key files include `.env.example`, `pyproject.toml`, and `docker-compose.yml`.
*   **README-falkordb-combined.md**: Provides instructions for a Docker setup that bundles FalkorDB (graph database) and the Graphiti MCP Server into a single container image for simplified deployment, including quick start, building, and configuration details.
*   **Dependency Graph**: An analysis of the project's dependency graph, offering insights into inter-module relationships and external library usage. (Summary provided from original document, inferred analysis).

### Development & Contribution
*   **CODE_OF_CONDUCT.md**: Outlines the Contributor Covenant Code of Conduct, emphasizing a harassment-free experience, respectful interaction, and enforcement responsibilities.
*   **CONTRIBUTING.md**: A comprehensive guide for contributing to Graphiti, covering ways to get involved (issues, feature requests, bug reports, use cases, Discord help), setup instructions, making changes, submitting pull requests, code style, quality, and specific guidelines for third-party integrations and adding new graph drivers.
*   **Zep-CLA.md**: The Contributor License Agreement (CLA) that contributors must agree to when submitting contributions to Zep Software, Inc., clarifying intellectual property licenses.
*   **SECURITY.md**: Details the security policy for Graphiti, including supported versions and the mechanism for reporting vulnerabilities via GitHub's Private Vulnerability Reporting.
*   **pull_request_template.md**: A standard template for submitting pull requests on GitHub, ensuring contributors provide necessary information like summary, type of change, objective, testing details, breaking changes, and a checklist.
*   **bug_report.md**: A template for creating bug reports, guiding users to provide essential information for reproduction, expected/actual behavior, environment details, and tracebacks.

### Internal Tools & Specifications
*   **cursor_rules.md**: Provides specific instructions and best practices for using Graphiti's Model Context Protocol (MCP) tools for AI agent memory, focusing on searching, saving information, and maintaining consistency.

### Code Examples & How-To Guides
*   **test_examples.md**: A report of 123 high-value Python code examples extracted from the project's test files, categorized by type (`config`, `instantiation`, `method_call`, `workflow`) and confidence. These are crucial for understanding API usage and behavior.
*   **index.md**: An index of 23 "How-To Guides" derived from the test examples, categorized by use case and difficulty level (Beginner, Intermediate, Advanced). This includes guides like "How To: Array Preserves All Elements" and "How To: Thread Safety".
*   **Individual How-To Guides (e.g., `array-preserves-all-elements.md`, `convert-datetime-list-and-tuple.md`, etc.)**: Each guide provides an overview, prerequisites, step-by-step instructions with code snippets, and a complete example for specific workflows or functionalities, making complex tasks actionable and easy to follow.